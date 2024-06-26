import cantera as ct
import numpy as np
from phasepy import component, mixture, preos
from phasepy.equilibrium import flash

from Capex import app_drying_time, residence_time, app_volume, app_massflow_rate
from relations import *

PROCESS_PRESSURE = 120  # bar
PROCESS_TEMPERATURE = 40  # degrees per celsius
THROTTLE_PRESSURE = 6  # bar
MEAN_ALCOHOL_COMPOSITION_ON_OUTLET = 0.3
INIT_COMPOSITION = [MEAN_ALCOHOL_COMPOSITION_ON_OUTLET, 1 - MEAN_ALCOHOL_COMPOSITION_ON_OUTLET]
PRESSURE_COMPRESSOR = 50
CONDENSATION_TEMPERATURE = 0

R = 8.314  # J / (mol * K)



productivity = 1000  # cubic meter per year
app_volume_cur = app_volume[0]

flow_list = app_massflow_rate(app_volume_cur, residence_time)

gas1 = ct.CarbonDioxide()
gas1.TP = 273.15 + 40, 101325 * 120


def heat_exchanger_press_drop(flowrate, pressure=PROCESS_PRESSURE, temperature_inlet=PROCESS_TEMPERATURE, temperature_outlet=88):
    mean_temperature = (temperature_inlet + temperature_outlet) / 2
    gas1.TP = 273.15 + mean_temperature, 101325 * pressure
    cp = gas1.cp
    # print(mean_temperature, cp)
    heat = cp * (temperature_outlet - temperature_inlet) * flowrate
    return heat


def throttle(flowrate, temperature_inlet, pressure_inlet=PROCESS_PRESSURE, pressure_outlet=THROTTLE_PRESSURE):
    t_1 = 273.15 + temperature_inlet
    gas1.TP = t_1, 101325 * pressure_inlet
    cv = gas1.cv_mole
    a = 0.42188 * ((ct.gas_constant * gas1.critical_temperature) ** 2) / gas1.critical_pressure
    b = 0.125 * (ct.gas_constant * gas1.critical_temperature) / gas1.critical_pressure
    v_1 = gas1.volume_mole
    gas1.TP = t_1, 101325 * pressure_outlet
    v_2 = gas1.volume_mole
    delta_T = a / cv * (1 / v_1 - 1 / v_2)
    # print('delta_T', delta_T, v_1, v_2)
    t_2 = t_1 - delta_T
    return t_2 - 273.15


def molar_to_mass_concentration(x_1, M1, M2):
    y_1 = M1 * x_1 / (M1 * x_1 + M2 * (1 - x_1))
    return y_1


def separator(flow_rate, initial_composition, temperature, pressure):
    co2 = component(name='carbon dioxide', Tc=304.12, Pc=73.74,
                      w=0.225, GC={'H2O': 1})

    isopropanol = component(name='2-propanol', Tc=508.3, Pc=47.62,
                        w=0.665, GC={'CH3': 2, 'CH': 1, 'OH(P)': 1})

    mix = mixture(isopropanol, co2)
    # or
    # mix = isopropanol + co2

    mix.unifac()
    eos = preos(mix, 'qmr')
    T = 273+temperature
    P = pressure
    Z = np.array(initial_composition)
    # print(Z, T, P)
    x0 = np.array([0.7, 0.3])
    y0 = np.array([0.9, 0.1])
    a = flash(x0, y0, 'LV', Z, T, P, eos, full_output=True)
    x = a['X']
    y = a['Y']
    vapor_phase_fraction = a['beta']
    mole_rate = flow_rate / (Z[0] * 60.09 + Z[1] * 44) * 1000  # mol/sec
    co2_mole_rate = mole_rate * vapor_phase_fraction * x[1]
    co2_mass_rate = co2_mole_rate * 44 / 1000  # kg
    return x, y, vapor_phase_fraction, co2_mass_rate


def compressor(flowrate, pressure_inlet, pressure_outlet, temperature_inlet):
    temperature_outlet, density_outlet, delta_h = compressor_main_calc(temperature_inlet, pressure_inlet, pressure_outlet)

    # print(flowrate)
    mol_flowrate = flowrate / 0.044
    # print(mol_flowrate)

    power = mol_flowrate * delta_h
    koefficient = 0.8
    power = power / koefficient


    return temperature_outlet, power

def condenser(flowrate, pressure, inlet_temperature, outlet_temperature):
    t_1 = 273.15 + inlet_temperature
    gas1.TP = t_1, 101325 * pressure
    entalphy_1 = gas1.enthalpy_mass

    t_2 = 273.15 + outlet_temperature
    gas1.TP = t_2, 101325 * pressure
    entalphy_2 = gas1.enthalpy_mass

    delta_h = abs(entalphy_1 - entalphy_2)
    delta_heat = delta_h * flowrate

    return delta_heat




flow = flow_list[0]
print('\n')
print('-----Initial Data-----')
print('Possible volumes of apparatuses, cub.m:', app_volume)
print('Chosen volume of apparatus, cub.m:', app_volume_cur)
print('List of flow rates for current volume of apparatus, kg/h:', np.round(flow_list * 3600, 2), np.round(flow * 3600, 2))
print('\n')

print('-----Drying Apparatus-----')
t = app_drying_time(flow, app_volume_cur)
print('Drying time for different flow rates, h:', np.round(t, 1))
print('\n')

print('-----Heat Exchanger-----')
heat_of_first_exchanger = heat_exchanger_press_drop(flow)
print('Heat exchanger power, W:', np.round(heat_of_first_exchanger, 1))
print('\n')

print('-----Throttle-----')
temperature_after_throttle = throttle(flow, 88)
print('Temperature of flow after throttle, deg C:', np.round(temperature_after_throttle, 2))
print('\n')

print('-----Separator-----')
liquid_phase_composition, vapor_phase_composition, vapor_phase_fraction, co2_mass_rate = separator(flow, INIT_COMPOSITION, -10, THROTTLE_PRESSURE)
print('flow rate, kg/h:', np.round(flow * 3600, 2))
print('Liquid phase composition, mol/mol:', liquid_phase_composition)
print('Gas phase composition, mol/mol:', vapor_phase_composition)
print('Vapor phase fraction, mol/mol:', np.round(vapor_phase_fraction, 3))
print('Mass flow rate of CO2 in liquid phase, kg/h:', np.round(co2_mass_rate * 3600, 2))
print('Losses of CO2, %:', np.round((co2_mass_rate / flow)*100, 2))
print('\n')

print('-----Compressor-----')
temp_after_compressor, compressor_power = compressor(flow, THROTTLE_PRESSURE, PRESSURE_COMPRESSOR, 273-20)
print('Temperature after compressor, deg C:', np.round(temp_after_compressor-273, 2))
print('Power of compressor, W', np.round(compressor_power, 2))
print('\n')

print('-----Condenser-----')
power_heat_condenser = condenser(flow, PRESSURE_COMPRESSOR, temp_after_compressor - 273, CONDENSATION_TEMPERATURE)
print('Condenser cooling power, W:', np.round(power_heat_condenser, 2))
print('\n')

print('-----Pump-----')
temp_after_pump, pump_power = compressor(flow, PRESSURE_COMPRESSOR, PROCESS_PRESSURE, 273 + CONDENSATION_TEMPERATURE)
print('Temperature after pump, deg C:', np.round(temp_after_pump, 2))
print('Power of pump, W', np.round(pump_power, 2))
print('\n')

print('-----Heat Exchanger-----')
power_heat_last_exchanger = condenser(flow, PROCESS_PRESSURE, 5, PROCESS_TEMPERATURE)
print('Exchanger power, W:', np.round(power_heat_last_exchanger, 2))
print('\n')


total_heat_exchangers_per_cycle = (heat_of_first_exchanger + power_heat_condenser + power_heat_last_exchanger) * t
print('Heat exchanger per cycle, W', total_heat_exchangers_per_cycle)

power_consumtions_compressing_and_pumping = (compressor_power + pump_power) * t
print('Pumping power per cycle, W', power_consumtions_compressing_and_pumping)

loss_co2 = co2_mass_rate * t * 3600
print('CO2 loss per cycle, kg', loss_co2)

total_energy = (total_heat_exchangers_per_cycle + power_consumtions_compressing_and_pumping) / t
print('total energy', total_energy)

print('drying time', t)

print('Heat exchanger power, W:', np.round(heat_of_first_exchanger, 1))
print('Temperature of flow after throttle, deg C:', np.round(temperature_after_throttle, 2))
print('Liquid phase composition, mol/mol:', liquid_phase_composition)
print('Gas phase composition, mol/mol:', vapor_phase_composition)
print('Vapor phase fraction, mol/mol:', np.round(vapor_phase_fraction, 3))
print('Losses of CO2, %:', np.round((co2_mass_rate / flow)*100, 2))
print('Temperature after compressor, deg C:', np.round(temp_after_compressor, 2))
print('Condenser cooling power, W:', np.round(power_heat_condenser, 2))
print('Power of pump, W', np.round(pump_power, 2))
print('Exchanger power, W:', np.round(power_heat_last_exchanger, 2))
#     return
#
# calculation()
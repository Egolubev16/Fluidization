import cantera as ct
import numpy as np
from phasepy import component, mixture, preos
from phasepy.equilibrium import flash

from Capex import app_drying_time, residence_time, app_volume, app_massflow_rate

PROCESS_PRESSURE = 120  # bar
PROCESS_TEMPERATURE = 40  # degrees per celsius
THROTTLE_PRESSURE = 6  # bar
MEAN_ALCOHOL_COMPOSITION_ON_OUTLET = 0.3
INIT_COMPOSITION = [MEAN_ALCOHOL_COMPOSITION_ON_OUTLET, 1 - MEAN_ALCOHOL_COMPOSITION_ON_OUTLET]
PRESSURE_COMPRESSOR = 50

R = 8.314  # J / (mol * K)



productivity = 1000  # cubic meter per year
app_volume_cur = app_volume[0]

flow_list = app_massflow_rate(app_volume_cur, residence_time)

gas1 = ct.CarbonDioxide()
gas1.TP = 273.15 + 40, 101325 * 120



def heat_exchanger_press_drop(flowrate, pressure=PROCESS_PRESSURE, temperature_inlet=PROCESS_TEMPERATURE, temperature_outlet=80):
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


def compressor():
    return

def condencor(flowrate, pressure, inlet_temperature, outlet_temperature):
    t_1 = 273.15 + inlet_temperature
    gas1.TP = t_1, 101325 * pressure
    entalphy_1 = gas1.enthalpy_mass

    t_2 = 273.15 + outlet_temperature
    gas1.TP = t_2, 101325 * pressure
    entalphy_2 = gas1.enthalpy_mass

    delta_h = abs(entalphy_1 - entalphy_2)
    delta_heat = entalphy_2 * flowrate

    return delta_heat

print('app_volumes', app_volume)

print(heat_exchanger_press_drop(flow_list))

t = app_drying_time(flow_list, app_volume_cur)
print('drying_times', t)

temperature_after_throttle = throttle(flow_list, 80)
print(temperature_after_throttle)

liquid_phase_composition, vapor_phase_composition, vapor_phase_fraction, co2_mass_rate = separator(flow_list, INIT_COMPOSITION, temperature_after_throttle, THROTTLE_PRESSURE)
print('flow rate', flow_list)
print(liquid_phase_composition, vapor_phase_composition, vapor_phase_fraction, co2_mass_rate)
print('losses of CO2', (co2_mass_rate / flow_list)*100)

condencor(flow_list, PRESSURE_COMPRESSOR)


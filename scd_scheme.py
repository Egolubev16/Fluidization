import cantera as ct

from Capex import app_drying_time, residence_time, app_volume, app_massflow_rate

PROCESS_PRESSURE = 120  # bar
PROCESS_TEMPERATURE = 40  # degrees per celsius
THROTTLE_PRESSURE = 10  # bar

R = 8.314  # J / (mol * K)



productivity = 1000  # cubic meter per year
app_volume = app_volume[0]

flow_list = app_massflow_rate(app_volume, residence_time)

gas1 = ct.CarbonDioxide()
gas1.TP = 273.15 + 40, 101325 * 120

def co2_heat_capasity(temperature, pressure):
    return


def heat_exhanger_press_drop(flowrate, pressure=PROCESS_PRESSURE, temperature_inlet=PROCESS_TEMPERATURE, temperature_outlet=80):
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


print(heat_exhanger_press_drop(flow_list))



t = app_drying_time(flow_list, app_volume)
print('drying_times', t)

temp = throttle(flow_list, 80)
print(temp)

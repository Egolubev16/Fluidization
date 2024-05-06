from Capex import app_drying_time, residence_time, app_volume, app_massflow_rate

PROCESS_PRESSURE = 120  # bar
PROCESS_TEMPERATURE = 40  # degrees per celsius


productivity = 1000  # cubic meter per year
app_volume = app_volume[0]

flow_list = app_massflow_rate(app_volume, residence_time)


def co2_heat_capasity(temperature, pressure):
    return


def heat_exhanger_press_drop(pressure=PROCESS_PRESSURE, temperature_inlet=PROCESS_TEMPERATURE, temperature_outlet=80):






t = app_drying_time(flow_list, app_volume)
print(t)

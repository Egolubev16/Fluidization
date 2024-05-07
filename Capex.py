import numpy as np
import math
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

PRODUCTIVITY = 100000

ROLL_HEIGHT = 1  # m
APP_HEIGHT = ROLL_HEIGHT + 0.03  # m
APP_LOADING = 0.7

STEEL_DENSITY = 7800  # kg / m3
STEEL_COST_PER_T = 500000

WORK_DAYS_PER_YEAR = 365 - 14

APP_LOADING_TIME = 2  # hours

GAP_WALL_ROLL = 0.004 * 2
ROLL_INNER_DIAMETER = 0.08
PRODUCT_WIDTH = 0.01

PRESSURE = 25  # MPa
PERMISSIBLE_STRESS = 179  # MPa
COEF_SEAM = 0.52

COST_WELDING_PER_CM = 12500  # RUB/M
COST_ROLLING_PER_T = 75000  # RUB/T

DENSITY_CO2 = 689  # KG/M3

app_volume = np.array([0.1, 0.15, 0.2, 0.3, 0.4, 0.5])
# mass_flow_rate = np.array([0.01984447, 0.03968894, 0.059499136, 0.07937788, 0.099279539])
residence_time = np.array([1041.6, 520, 347, 260, 208])  # s

ENTHALPY_COOLING = 327.85  # kJ/kg
ENTHALPY_PUMP = 7.7  # kJ/kg
ENTHALPY_HEAT_1 = 75.38  # kJ/kg
ENTHALPY_HEAT_2 = 169.23  # kJ/kg
ENTHALPY_COMPRESSOR = 76  # kJ/kg

EFFICIENCY_HEAT_EX = 0.85
EFFICIENCY_PUMP = 0.35

COST_CO2_PER_KG = 70  # RUB

ELECRTIC_COST_PER_KW_H = 6.741  # RUB

CO2_RECUPERATION_EFFICIENCY = 0.7


def app_massflow_rate(volume, res_time):
    vol_rate = (volume - volume * APP_LOADING) / res_time
    mass_flow_rate = vol_rate * DENSITY_CO2
    return mass_flow_rate


def app_drying_time(mass_flow_rate, volume):
    if volume == 0.1:
        print('check: apparatus volume =', volume)
        drying_time = -19340 * mass_flow_rate ** 3 + 4501.2 * mass_flow_rate ** 2 - 359.66 * mass_flow_rate + 19.348

    elif (volume == 0.15).all():
        print('check: apparatus volume =', volume)
        drying_time = -4730.4 * mass_flow_rate ** 3 + 1715.3 * mass_flow_rate ** 2 - 221.19 * mass_flow_rate + 20.059

    elif (volume == 0.2).all():
        print('check: apparatus volume =', volume)
        drying_time = 907.53 * mass_flow_rate ** 3 - 58.158 * mass_flow_rate ** 2 - 61.034 * mass_flow_rate + 17.571

    elif (volume == 0.3).all():
        print('check: apparatus volume =', volume)
        drying_time = -433.8 * mass_flow_rate ** 3 + 365.55 * mass_flow_rate ** 2 - 106.85 * mass_flow_rate + 21.456

    elif (volume == 0.4).all():
        print('check: apparatus volume =', volume)
        drying_time = -132.93 * mass_flow_rate ** 3 + 167.96 * mass_flow_rate ** 2 - 73.345 * mass_flow_rate + 22.549

    else:
        print('check: apparatus volume =', volume)
        drying_time = -163.18 * mass_flow_rate ** 3 + 205.66 * mass_flow_rate ** 2 - 94.674 * mass_flow_rate + 28.299

    return drying_time


def app_diameter_ness(volume):
    diameter = (volume / APP_HEIGHT * 4 / np.pi) ** 0.5
    return diameter


def app_wall_width(diameter):
    width = PRESSURE * diameter / (2 * PERMISSIBLE_STRESS * COEF_SEAM - PRESSURE)
    return width


def app_free_volume(volume):
    free_volume = volume * (1 - APP_LOADING)
    return free_volume


def steel_cost(app_wall_d, app_wall_w):
    volume_of_steel = math.pi * (
                app_wall_d + 2 * app_wall_w) * 2 * APP_HEIGHT / 4 - math.pi * app_wall_d * 2 * APP_HEIGHT / 4

    cost_steel = volume_of_steel * STEEL_DENSITY * STEEL_COST_PER_T / 1000
    cost_welding = COST_WELDING_PER_CM * (2 * math.pi * app_wall_d + 2 * APP_HEIGHT)
    cost_rolling = volume_of_steel * STEEL_DENSITY / 1000 * COST_ROLLING_PER_T

    volume_of_steel_for_bottom = math.pi * (app_wall_d + 2 * app_wall_w) ** 2 * app_wall_w * 2 / 4
    cost_bottom = volume_of_steel_for_bottom * STEEL_DENSITY * STEEL_COST_PER_T / 1000

    cost_flange = (cost_steel + cost_bottom) / 2

    cost = cost_steel + cost_welding + cost_rolling + cost_bottom + cost_flange
    return cost


def cycles_number(drying_time):
    number = WORK_DAYS_PER_YEAR * 24 / (drying_time + APP_LOADING_TIME)
    # print(number)
    return number


def product_volume(cycles_number, app_volume):
    product = app_volume * APP_LOADING * cycles_number
    return product


def co2_consumption(flow_rate, drying_time, cycles_number):
    consumtion = (1 - CO2_RECUPERATION_EFFICIENCY) * flow_rate * 3600 * drying_time * cycles_number
    return consumtion


def roll_area(app_diameter):
    roll_diameter = app_diameter - GAP_WALL_ROLL
    roll_lenght = np.pi * (roll_diameter * 2 - ROLL_INNER_DIAMETER * 2) / 4 / PRODUCT_WIDTH
    roll_area = roll_lenght * ROLL_HEIGHT
    return roll_area


def nessesary_app_number(app_diameter, possible_cycles):
    cycles = PRODUCTIVITY / roll_area(app_diameter)
    app_number = cycles / possible_cycles
    # print("app_number", possible_cycles)

    return app_number


def capex(cost, app_number, consumtion, electric_cost):
    capex_apparatus = app_number * cost / 10 / PRODUCTIVITY
    capex_co2 = consumtion * COST_CO2_PER_KG / PRODUCTIVITY
    capex_electrisity = electric_cost / PRODUCTIVITY
    # print('capex app check', capex_apparatus, 'capex co2 check', capex_co2, 'capex electr check', capex_electrisity)

    capex = capex_apparatus + capex_co2 + capex_electrisity
    return capex


def app_res_time(vol, mass_flow_rate):
    vol_rate = mass_flow_rate / DENSITY_CO2
    res_time = vol / vol_rate
    return res_time


def electric_power_cost(mass_flow_rate, drying_time, cycles):
    power = (ENTHALPY_COOLING + ENTHALPY_HEAT_1 + ENTHALPY_HEAT_2) * mass_flow_rate / EFFICIENCY_HEAT_EX + (
                ENTHALPY_PUMP + ENTHALPY_COMPRESSOR) * mass_flow_rate / EFFICIENCY_PUMP
    electric_cost_per_year = power * drying_time * cycles * ELECRTIC_COST_PER_KW_H
    return electric_cost_per_year

def main():
    total_capex_cost = []

    for vol in app_volume:
        mass_flow_rate = app_massflow_rate(vol, residence_time)
        res_time = app_res_time(vol, mass_flow_rate)

        drying_time = app_drying_time(mass_flow_rate, vol)
        diameter_list = app_diameter_ness(vol)
        width_list = app_wall_width(diameter_list)
        free_list = app_free_volume(vol)
        cost = steel_cost(diameter_list, width_list)

        number_of_cycles_per_app = cycles_number(drying_time)

        cost_co2 = co2_consumption(mass_flow_rate, drying_time, number_of_cycles_per_app)

        electric_cost_per_year = electric_power_cost(mass_flow_rate, drying_time, cycles_number(drying_time))

        ness_app_number = np.round(nessesary_app_number(diameter_list, number_of_cycles_per_app), 0)

        capex_cost = capex(cost, ness_app_number, cost_co2,
                           electric_cost_per_year)
        total_capex_cost.append(capex_cost)

        print('Apparatus Volume = ', vol, '\n', 'Nessessary Apparatus Number = ', ness_app_number, '\n', 'Massflow rate = ', mass_flow_rate, '\n', 'Drying time = ', drying_time,
              '\n', 'CAPEX = ', capex_cost, '\n', 'Elecrtic cost', electric_cost_per_year)

    total_capex_cost = np.array(total_capex_cost).T

    x, y = np.meshgrid(app_volume, residence_time)

    print("-------------------------------")
    print(x)
    print("-------------------------------")
    print(y)
    print("-------------------------------")
    print(total_capex_cost)
    print("-------------------------------")

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.plot_surface(x, y, total_capex_cost)
    ax.set_xlabel('App_volume, m3')
    ax.set_ylabel('Residence time, s')
    ax.set_zlabel('Capex, rub')

    plt.show()

# x, y = np.meshgrid(app_volume, residence_time)
# #print('1', x, y)
# diameter_list = app_diameter_ness(x)
# mass_flow_rate = app_massflow_rate(x, y)
# #print('2', diameter_list)
# width_list = app_wall_width(diameter_list)
# #print('3', width_list)
# cost = steel_cost(diameter_list, width_list)
# #print('4', cost)
# dr_t = app_drying_time(mass_flow_rate, x)
# print('5', dr_t)
# number_of_cycles_per_app = cycles_number(dr_t)
# #print('6', number_of_cycles_per_app)
# cost_co2 = co2_consumption(mass_flow_rate, dr_t, number_of_cycles_per_app)
# electric_cost_per_year = electric_power_cost(mass_flow_rate, dr_t, cycles_number(dr_t))
# capex_for_surface = capex(cost, nessesary_app_number(diameter_list, number_of_cycles_per_app), cost_co2, electric_cost_per_year)
# print('capex_ check', capex_for_surface)
# #print('7', capex_for_surface)
# fig = plt.figure()
# ax = fig.add_subplot(projection='3d')
# ax.plot_surface(x, y, capex_for_surface)
# ax.set_xlabel('App_volume, m3')
# ax.set_ylabel('Residence time, s')
# ax.set_zlabel('Capex, rub')
#
#
# plt.show()
import cantera as ct
import numpy as np
from scipy.optimize import minimize

gas = ct.CarbonDioxide()

t_c = gas.critical_temperature  # Kelvin
p_c = gas.critical_pressure / 100000  # Pa
r_const = 83.14  # J / (mol  K)


a = 0.42748 * r_const** 2 * t_c ** 2.5 / p_c
b = 0.08662 * r_const * t_c / p_c
print('t_c, p_c = ', t_c, p_c)
print('a, b = ', a, b)


def redlich_P(v, t):
    p = r_const * t / (v - b) - (a / t**0.5) / (v * (v + b))
    return p



def redlihc_v1(p_1, t_1):
    v_1 = r_const * t_1 / p_1
    func = lambda x: abs(p_1 - redlich_P(x, t_1))
    initial_guesse = [v_1]

    bnds = [[0.00000000001, 10000000]]
    res = minimize(func, initial_guesse, method='Nelder-Mead', bounds=bnds)

    return res.x


def delta_entrophy(t_1, t_2, v_1, v_2, p_1, p_2):
    delta = ((2.95 * np.log(t_2) + 0.00495 * t_2) - (2.95 * np.log(t_1) + 0.00495 * t_1) -
             np.log(p_2 / p_1) +
             (np.log((v_2 - b) / v_2) + a / (2 * b * r_const) * (t_2 ** (- 3 / 2)) * (np.log(v_2 / (v_2 + b)))) -
             (np.log((v_1 - b) / v_1) + a / (2 * b * r_const) * (t_1 ** (- 3 / 2)) * (np.log(v_1 / (v_1 + b)))))

    return abs(delta)


def delta_entalpy(t_1, t_2, v_1, v_2, p_1, p_2):
    delta = 8.314 * (((p_2 * v_2 - r_const * t_2) / (r_const) + (3 * a / (2 * r_const * b * t_2 **0.5) * np.log(v_2 / (v_2 + b)))) -
                     ((p_1 * v_1 - r_const * t_1) / (r_const) + (3 * a / (2 * r_const * b * t_1 **0.5) * np.log(v_1 / (v_1 + b)))) +
                     (2.95 * t_2 + 0.002475 * t_2 **2) - (2.95 * t_1 + 0.002475 * t_1 **2))
    return delta


def compressor_main_calc(t_1, p_1, p_2):
    v_1 = redlihc_v1(p_1, t_1)
    # print('v1 and p1 = ', v_1, redlich_P(v_1, t_1))
    t_2 = t_1

    # func_s = lambda x: delta_entrophy(t_1, x, v_1, redlihc_v1(p_2, x), p_1, p_2)
    # initial_guesse = [t_1]
    # bnds = [[t_1, 1000]]
    # res = minimize(func_s, initial_guesse, method='Nelder-Mead', bounds=bnds)
    # print(res)
    # print(res.x, 44 / redlihc_v1(p_2, res.x))

    delta_t = 0.1
    for i in range(10000):
        v_2 = redlihc_v1(p_2, t_2)

        delta_s = delta_entrophy(t_1, t_2, v_1, v_2, p_1, p_2)
        # print(round(t_2, 2), v_2, delta_s, redlich_P(v_2, t_2), 44 / v_2)

        if delta_s < 0.01:
            break
        t_2 = t_2 + delta_t

    density = 44000 / v_2[0]

    delta_H = delta_entalpy(t_1, t_2, v_1, v_2, p_1, p_2)[0]

    # return in units: Kelvin, kg / m3, J / mol
    return t_2, density, delta_H

print(compressor_main_calc(273, 50, 120))
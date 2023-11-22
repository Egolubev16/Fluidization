import matplotlib.pyplot as plt

def Raschet(diameter, diameter_list, density_CO2, density_of_particle, dyn_viscosity_CO2, cross_sectional_area, massflow_start_list, massflow_end_list):

    for i in range(0, 30):
        diameter_list.append(diameter)
        diameter += 10

    for i in range(len(diameter_list)):
        Ar = 9.8 * (diameter_list[i]/1000000) ** 3 * density_CO2 ** 2 * (
                    density_of_particle - density_CO2) / dyn_viscosity_CO2 ** 2 / density_CO2
        Re_start = Ar / (1400 + 5.22 * Ar ** 0.5)
        velocity_start = Re_start * dyn_viscosity_CO2 / density_CO2 / (diameter_list[i]/1000000)
        massflow_start = velocity_start * cross_sectional_area * density_CO2 * 1000 * 3600
        massflow_start_list.append(massflow_start)

        Re_end = Ar/(18+0.0575*Ar**0.5)
        velocity_end = Re_end * dyn_viscosity_CO2 / density_CO2 / (diameter_list[i]/1000000)
        massflow_end = velocity_end * cross_sectional_area * density_CO2 * 1000 * 3600
        massflow_end_list.append(massflow_end)

def Visual(diameter_list, massflow_start_list, massflow_end_list):
    '''plt.title('Зависимость массового расхода начала псевдоожижения и уноса от диаметра частиц')
    plt.xlabel('Диаметр частиц, мкм')
    plt.ylabel('Массовый расход диоксида углерода, г/ч')
    plt.plot(diameter_list, massflow_start_list, label="Начало псевдоожижения")
    plt.plot(diameter_list, massflow_end_list, label="Начало уноса")
    plt.legend()
    plt.show()'''

    plt.figure()
    plt.subplot(1, 2, 1)
    plt.title('Зависимость массового расхода начала псевдоожижения от диаметра частиц')
    plt.xlabel('Диаметр частиц, м')
    plt.ylabel('Массовый расход диоксида углерода, г/ч')
    plt.plot(diameter_list, massflow_start_list, label="Начало псевдоожижения")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.title('Зависимость массового расхода начала уноса от диаметра частиц')
    plt.xlabel('Диаметр частиц, мкм')
    plt.ylabel('Массовый расход диоксида углерода, г/ч')
    plt.plot(diameter_list, massflow_end_list, label="Начало уноса")
    plt.legend()

    plt.show()

def main():
    density_CO2 = 801.7
    dyn_viscosity_CO2 = 7.17e-5
    true_density_of_particle = 2200
    porosity = 0.9
    density_IPS = 786
    cross_sectional_area = 4.9e-4

    density_of_particle = density_IPS * porosity + true_density_of_particle * (1 - porosity)

    massflow_start_list = []
    massflow_end_list = []
    diameter_list = []
    diameter = 100

    Raschet(diameter, diameter_list, density_CO2, density_of_particle, dyn_viscosity_CO2, cross_sectional_area, massflow_start_list, massflow_end_list)
    Visual(diameter_list, massflow_start_list, massflow_end_list)
main()

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np


def fluidization_flow_starts(diameter, density_of_particle, density_CO2, dyn_viscosity_CO2, app_diameter):
    """ Calculation of fluidization flow-rate start """
    cross_sectional_area = np.pi * (app_diameter ** 2) / 4
    Ar = 9.8 * diameter ** 3 * density_CO2 ** 2 * (
            density_of_particle - density_CO2) / dyn_viscosity_CO2 ** 2 / density_CO2
    Re_start = Ar / (1400 + 5.22 * Ar ** 0.5)
    velocity_start = Re_start * dyn_viscosity_CO2 / density_CO2 / diameter
    massflow_start = velocity_start * cross_sectional_area * density_CO2 * 1000 * 3600
    return massflow_start

def fluidization_flow_ends(diameter, density_of_particle, density_CO2, dyn_viscosity_CO2, app_diameter):
    """ Calculation of fluidization flow-rate ends """
    cross_sectional_area = np.pi * (app_diameter **2) / 4
    Ar = 9.8 * diameter ** 3 * density_CO2 ** 2 * (
            density_of_particle - density_CO2) / dyn_viscosity_CO2 ** 2 / density_CO2
    Re_end = Ar / (18 + 0.0575 * Ar ** 0.5)
    velocity_end = Re_end * dyn_viscosity_CO2 / density_CO2 / diameter
    massflow_end = velocity_end * cross_sectional_area * density_CO2 * 1000 * 3600
    return massflow_end


# properties of the system
density_CO2 = 801.7
dyn_viscosity_CO2 = 7.17e-5
true_density_of_particle = 2200
porosity = 0.9
density_IPS = 786
app_diameter = 0.025
density_of_particle = density_IPS * porosity + true_density_of_particle * (1 - porosity)

# bounds for calculation in 2d
diameter_start = 100 / 1000000
diameter_stop = 400 / 1000000
steps_number = 100

diameter_list = np.linspace(diameter_start, diameter_stop, steps_number)

fluidization_start_list = fluidization_flow_starts(diameter_list, density_of_particle, density_CO2, dyn_viscosity_CO2, app_diameter)
fluidization_end_list = fluidization_flow_ends(diameter_list, density_of_particle, density_CO2, dyn_viscosity_CO2, app_diameter)

# bounds for calculation in 3d
density_of_particle_start = 1000
density_of_particle_end = 3000
steps_number_density = 100

density_list = np.linspace(density_of_particle_start, density_of_particle_end, steps_number_density)
X, Y = np.meshgrid(diameter_list, density_list)

fluidization_start_list_for_surface = fluidization_flow_starts(X, Y, density_CO2, dyn_viscosity_CO2, app_diameter)
fluidization_end_list_for_surface = fluidization_flow_ends(X, Y, density_CO2, dyn_viscosity_CO2, app_diameter)

# 2d plot
plt.plot(diameter_list * 1000000, fluidization_start_list)
plt.plot(diameter_list * 1000000, fluidization_end_list)


# 3d plot
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.plot_surface(X, Y, fluidization_start_list_for_surface)
ax.set_xlabel('Diameter, ' + r'$\mu$' + 'm')
ax.set_ylabel('Particles density, kg/cub.m')
ax.set_zlabel('Fluidization flow-rate')

plt.show()


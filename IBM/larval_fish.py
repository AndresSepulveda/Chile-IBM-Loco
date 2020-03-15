import os
import numpy as np
import datetime
from opendrift.models.opendrift3D import \
    OpenDrift3DSimulation, Lagrangian3DArray
from opendrift.elements import LagrangianArray
import pysolar
import copy

# Defining the oil element properties
class LarvalFish(Lagrangian3DArray):
    """
    Extending Lagrangian3DArray with specific properties for larval and juvenile stages of fish
    """

    variables = LagrangianArray.add_variables([
        ('diameter', {'dtype': np.float32,
                      'units': 'm',
                      'default': 0.0014}),  # for NEA Cod
        ('neutral_buoyancy_salinity', {'dtype': np.float32,
                                       'units': '[]',
                                       'default': 31.25}),  # for NEA Cod
        ('density', {'dtype': np.float32,
                     'units': 'kg/m^3',
                     'default': 1028.}),
        ('age_seconds', {'dtype': np.float32,
                         'units': 's',
                         'default': 0.}),
        ('hatched', {'dtype': np.int64,
                     'units': '',
                     'default': 0}),
        ('age', {'dtype': np.float32,  # Added to track percentage of competency time completed
                 'units': '',
                 'default': 0.}),
        ('length', {'dtype': np.float32,
                    'units': 'mm',
                    'default': 10.0}),
        ('weight', {'dtype': np.float32,
                    'units': 'mg',
                    'default': 0.08}),
        ('Eb', {'dtype': np.float32,
                'units': 'ugEm2',
                'default': 0.}),
        ('light', {'dtype': np.float32,
                   'units': 'ugEm2',
                   'default': 0.}),
        ('growth_rate', {'dtype': np.float32,
                         'units': '%',
                         'default': 0.}),
        ('ingestion_rate', {'dtype': np.float32,
                            'units': '%',
                            'default': 0.}),
        ('stomach_fullness', {'dtype': np.float32,
                              'units': '%',
                              'default': 0.}),
        ('stomach', {'dtype': np.float32,
                     'units': '',
                     'default': 0.}),
        ('survival', {'dtype': np.float32,
                      'units': '',
                      'default': 1.})])


class PelagicPlanktonDrift(OpenDrift3DSimulation):
    """Buoyant particle trajectory model based on the OpenDrift framework.

        Developed at MET Norway

        Generic module for particles that are subject to vertical turbulent
        mixing with the possibility for positive or negative buoyancy

        Particles could be e.g. oil droplets, plankton, or sediments

    """

    ElementType = LarvalFish

    required_variables = ['x_sea_water_velocity', 'y_sea_water_velocity',
                          'sea_surface_wave_significant_height',
                          'x_wind', 'y_wind', 'land_binary_mask',
                          'sea_floor_depth_below_sea_level',
                          'ocean_vertical_diffusivity',
                          'sea_water_temperature',
                          'sea_water_salinity',
                          'surface_downward_x_stress',
                          'surface_downward_y_stress',
                          'turbulent_kinetic_energy',
                          'turbulent_generic_length_scale',
                          'upward_sea_water_velocity'
                          ]

    # Vertical profiles of the following parameters will be available in
    # dictionary self.environment.vertical_profiles
    # E.g. self.environment_profiles['x_sea_water_velocity']
    # will be an array of size [vertical_levels, num_elements]
    # The vertical levels are available as
    # self.environment_profiles['z'] or
    # self.environment_profiles['sigma'] (not yet implemented)
    required_profiles = ['sea_water_temperature',
                         'sea_water_salinity',
                         'ocean_vertical_diffusivity']
    required_profiles_z_range = [0, -200]  # The depth range (in m) which profiles should cover

    fallback_values = {'x_sea_water_velocity': 0,
                       'y_sea_water_velocity': 0,
                       'sea_surface_wave_significant_height': 0,
                       'x_wind': 0, 'y_wind': 0,
                       'sea_floor_depth_below_sea_level': 1000,
                       'ocean_vertical_diffusivity': 0.02,  # m2s-1
                       'sea_water_temperature': 10.,
                       'sea_water_salinity': 34.,
                       'surface_downward_x_stress': 0,
                       'surface_downward_y_stress': 0,
                       'turbulent_kinetic_energy': 0,
                       'turbulent_generic_length_scale': 0,
                       'upward_sea_water_velocity': 0
                       }

    # Default colors for plotting
    status_colors = {'initial': 'green', 'active': 'blue',
                     'hatched': 'red', 'eaten': 'yellow', 'died': 'magenta'}

    def __init__(self, *args, **kwargs):
        # Calling general constructor of parent class
        super(PelagicPlanktonDrift, self).__init__(*args, **kwargs)

        # IBM configugration options
        self._add_config('IBM:constant_ingestion', 'float(min=0.0, max=1.0, default=0.5)', comment='Ingestion constant')
        self._add_config('IBM:active_metab_on', 'float(min=0.0, max=1.0, default=1.0)', comment='Active metabolism')
        self._add_config('IBM:attenuation_coefficient', 'float(min=0.0, max=1.0, default=0.18)',
                         comment='Attenuation coefficient')
        self._add_config('IBM:fraction_of_timestep_swimming', 'float(min=0.0, max=1.0, default=0.15)',
                         comment='Fraction of timestep swimming')
        self._add_config('IBM:lower_stomach_lim', 'float(min=0.0, max=1.0, default=0.3)',
                         comment='Limit of stomach fullness for larvae to go down if light increases')

        self._add_config('IBM:vertical_behavior_fixed_range', 'boolean(default=False)',
                         comment='Fixed swim range for VB')
        self._add_config('IBM:vertical_behavior_dynamic_range', 'boolean(default=True)',
                         comment='Dynamic swim range for VB')
        self._add_config('IBM:total_time_free_drift_before_competency', 'float(min=0, max=372800, default=86400)',
                         comment='Time after spawn to drift')
        self._add_config('IBM:total_competency_duration', 'float(min=0, max=25920000, default=2592000)',
                         comment='Time of competence')
        self._add_config('IBM:passive_drift_during_competence_period', 'boolean(default=False)',
                         comment='Drift during competence')

        self.complexIBM = False

    def calculate_maximum_daily_light(self):

        dd = (self.start_time + datetime.timedelta(seconds=self.elements.age_seconds[0]))
        current_date = datetime.datetime(year=dd.year,
                                         month=dd.month,
                                         day=dd.day,
                                         hour=dd.hour,
                                         second=dd.second,
                                         tzinfo=datetime.timezone.utc)

        # Calculate the daily variation of irradiance based on time of day using pysolar
        for ind in range(len(self.elements.lat)):

            if self.elements.lat[ind] < 0:
                lat = 360 - self.elements.lat[ind]
            else:
                lat = self.elements.lat[0]

            altitude_deg = pysolar.solar.get_altitude(lat, self.elements.lon[ind], current_date)
            self.elements.light[ind] = pysolar.radiation.get_radiation_direct(current_date, altitude_deg)


    def update_vertial_position_fixed_range(self, length, old_light, current_light, current_depth):

        mm2m = 1. / 1000.
        swim_speed = 0.5 * length * mm2m * self.time_step.total_seconds()
        max_hourly_move = swim_speed * (self.time_step.total_seconds() / 3600.)

        lowDepth = -40
        highDepth = -10

        if old_light <= current_light:  # and stomach_fullness >= lower_stomach_lim): #If light increases and stomach is sufficiently full, go down
            depth = max(lowDepth, current_depth - max_hourly_move)
        else:  # If light decreases or stomach is not sufficiently full, go up
            depth = min(highDepth, current_depth + max_hourly_move)
        return depth

    def update_vertial_position_dynamic_range(self, length,
                                              old_light,
                                              current_light,
                                              current_depth):

        # Update the vertical position of the current larva using length (in mm) to calculate
        # ma hourly move in meters
        mm2m = 1./1000.
        swim_speed = 0.5 * length * mm2m * self.time_step.total_seconds()
        max_hourly_move = swim_speed * (self.time_step.total_seconds() / 3600.)

        if old_light <= current_light:  # and stomach_fullness >= lower_stomach_lim): #If light increases and stomach is sufficiently full, go down
            depth = min(0.0, current_depth - max_hourly_move)
        else:  # If light decreases or stomach is not sufficiently full, go up
            depth = min(0, current_depth + max_hourly_move)
     #   print(current_depth,depth,max_hourly_move)
        return depth

    def update_larval_fish_development(self):
        """
        Calculates the growth rate in micrometer for each individual larvae depending 
        on their ambient temperature (Garavelli et al. 2016, PLoS ONE).
        """
        dt = self.time_step.total_seconds()
        T = self.environment.sea_water_temperature
        beta = 4.587
        PLD = np.exp(beta - 1.34 * np.log(T / 15.) - (0.28 * (np.log(T / 15.)) ** 2))
        GR = ((1900 - 250) / PLD) * (dt / 86400.)
        self.elements.growth_rate = GR
        self.elements.weight += GR * dt

        # Update the lengthg (mm) using DOI:10.1371/journal.pone.0146418
        mm2micrometer = 0.001

        # self.elements.length = (self.elements.length*mm2micrometer + GR * dt)*(1./mm2micrometer)

        # Update days of competency stage completed
        self.elements.age += dt

        # TODO: Need a function that relates growth to length to update length for each time step

    def update_larval_fish(self):
        """
        This is where we can include higher level complexity in the calculations of 
        growth, survial, development, and behavior of each individual 
        """
        # SETTINGS
        constant_ingestion = self.get_config('IBM:constant_ingestion')
        active_metab_on = self.get_config('IBM:active_metab_on')
        att_coeff = self.get_config('IBM:attenuation_coefficient')
        total_competency_duration = self.get_config('IBM:total_competency_duration')
        dt_drift = self.get_config('IBM:total_time_free_drift_before_competency')

        # LIGHT UPDATE
        # Save the light from previous timestep to use for vertical behavior
        last_light = self.elements.light.copy()
        self.calculate_maximum_daily_light()
        # Light at depth of larvae assuming constant attenuation (can be changed to dependent on chlorophyll)
        self.elements.Eb = self.elements.light * np.exp(att_coeff * self.elements.z)

        # FISH UPDATE
        self.update_larval_fish_development()

        # VERTICAL POSITION UPDATE
        for ind in range(len(self.elements.lat)):
            if (self.elements.age_seconds[ind] <= dt_drift) \
                    or (self.elements.age_seconds[ind] >= (total_competency_duration + dt_drift)):
                if self.get_config('IBM:vertical_behavior_fixed_range') is True:
                    self.elements.z[ind] = self.update_vertial_position_fixed_range(self.elements.length[ind],
                                                                                    last_light[ind],
                                                                                    self.elements.light[ind],
                                                                                    self.elements.z[ind])
                if self.get_config('IBM:vertical_behavior_dynamic_range') is True:
                    self.elements.z[ind] = self.update_vertial_position_dynamic_range(self.elements.length[ind],
                                                                                      last_light[ind],
                                                                                      self.elements.light[ind],
                                                                                      self.elements.z[ind])

    def update(self):

        """
        MAIN: 
        
        Update positions and properties of buoyant particles.
        Here you can turn on or off which physical properties you want to include:
        vertical advection
        horizontal advection 
        vertical mixing
        terminal velocty (sinking / buoyancy of eggs/larvae)
        vertical behavior (in update_larval_fish)
        """

        # Update element age
        self.elements.age_seconds += self.time_step.total_seconds()

        # Turn off terminal velocity (sinking) before calculating vertical mixing
        # Turn on mixing through 'processes:turbulentmixing' in run_ibm.py
        self.elements.terminal_velocity = 0.0
        self.vertical_mixing()

        # Update the growth and vertical position of each individual
        self.update_larval_fish()

        # Horizontal advection

        dt_drift = self.get_config('IBM:total_time_free_drift_before_competency')
        dt_competence = self.get_config('IBM:total_time_free_drift_before_competency')
        passive_drift_during_competence_period = self.get_config('IBM:passive_drift_during_competence_period')

        if not passive_drift_during_competence_period:
            for ind in range(len(self.elements.lat)):
                # If the age of the fish is less than the initial drift
                # time after release and younger than the total time spent
                # for cokmpetency then we move the fish to the seafloor where currents are assumed to be non-existent
                if dt_drift < self.elements.age_seconds[ind] < dt_drift + dt_competence:
                    self.elements.z[ind] = 'seafloor'

        self.advect_ocean_current()

        # Vertical advection
        if self.get_config('processes:verticaladvection') is True:
            self.vertical_advection()

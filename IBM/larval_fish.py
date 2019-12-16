import os
import numpy as np
from datetime import datetime, timedelta
from opendrift.models.opendrift3D import \
    OpenDrift3DSimulation, Lagrangian3DArray
from opendrift.elements import LagrangianArray
#import IBM.light as light
import IBM.calclight as calclight

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
        ('competency_duration', {'dtype': np.float32,   #Added to track percentage of competency time completed
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
        
        #IBM configugration options
        self._add_config('biology:constant_ingestion', 'float(min=0.0, max=1.0, default=0.5)', comment='Ingestion constant')
        self._add_config('biology:active_metab_on', 'float(min=0.0, max=1.0, default=1.0)', comment='Active metabolism')
        self._add_config('biology:attenuation_coefficient', 'float(min=0.0, max=1.0, default=0.18)', comment='Attenuation coefficient')
        self._add_config('biology:fraction_of_timestep_swimming', 'float(min=0.0, max=1.0, default=0.15)', comment='Fraction of timestep swimming')
        self._add_config('biology:lower_stomach_lim', 'float(min=0.0, max=1.0, default=0.3)', comment='Limit of stomach fullness for larvae to go down if light increases')
       
        self.complexIBM=False
      
    def calculate_maximum_daily_light(self):
        """LIGHT == Get the maximum light at the current latitude, and the current surface light at the current time.
        These values are used in calculateGrowth and  predation.FishPredAndStarvation, but need only be calcuated once per time step. """

        tt = self.time.timetuple()
      
        num=np.shape(self.elements.lat)[0]
        day_of_year = float(tt.tm_yday); month=float(tt.tm_mon); hour_of_day = float(tt.tm_hour); days_in_year=365.0
        radfl0=np.zeros((num)); max_light=np.zeros((num)); 
        cawdir=np.zeros((num)); clouds=0.0; 
        sun_height=np.zeros((num)); surface_light=np.zeros((num))

        """Calculate the maximum and average light values for a given geographic position
        for a given time of year. Notice we use radfl0 instead of maximum values maxLight
        in light caclualtions. Seemed better to use average values than extreme values.
        NOTE: Convert from W/m2 to umol/m2/s-1"""
        radfl0,max_light,cawdir = calclight.calclight.qsw(radfl0,max_light,cawdir,clouds,self.elements.lat*np.pi/180.0,day_of_year,days_in_year,num)
        max_light = radfl0/0.217
        
        """Calculate the daily variation of irradiance based on hour of day - store in self.elements.light"""
        for ind in range(len(self.elements.lat)):
          sun_height, surface_light = calclight.calclight.surlig(hour_of_day,float(max_light[ind]),day_of_year,float(self.elements.lat[ind]),sun_height,surface_light)
          self.elements.light[ind]=surface_light
        #  print("{} light {} time {}".format(ind,self.elements.light[ind],tt))
        
    def calculate_maximum_daily_light_python(self):
        """
        NOT WORKING:
        LIGHT calculations
        Get the maximum surface light at the current latitude and the time of day. This assumes that masimum yearly 
        surface light is known (simplification to use Python light module)
        """
        self.elements.light[:]= light.surface_light(self.time.timetuple(), self.elements.lat[:])

   
    def update_larval_fish_development(self):
        """
        Calculates the growth rate in micrometer for each individual larvae depending 
        on their ambient temperature (Garavelli et al. 2016, PLoS ONE).
        """
        dt=self.time_step.total_seconds()
        T=self.environment.sea_water_temperature
        beta=4.587
        PLD=np.exp(beta-1.34*np.log(T/15.)-(0.28*(np.log(T/15.))**2))
        GR=((1900-250)/PLD)*(dt/86400.)
        self.elements.growth_rate=GR
        self.elements.weight+=GR*dt
        
        # Update days of competency stage completed
        self.elements.competency_duration+=dt/86400.
        
        # TODO: Need a function that relates growth to length to update length for each time step
        
    def update_vertial_position(self,length,old_light,current_light,current_depth,stomach_fullness,dt):
        """
        Update the vertical position of the current larva
        """
        
        swim_speed=0.1*length # 0.1 Body length per second
        fraction_of_timestep_swimming = self.get_config('biology:fraction_of_timestep_swimming')
        max_hourly_move = swim_speed*dt # TODO : add ? *fraction_of_timestep_swimming
        max_hourly_move =  round(max_hourly_move/1000.,1) # depth values are negative
        
        if (old_light <= current_light): # and stomach_fullness >= lower_stomach_lim): #If light increases and stomach is sufficiently full, go down
          depth = min(0.0,current_depth - max_hourly_move)
        else: #If light decreases or stomach is not sufficiently full, go up
          depth = min(0,current_depth + max_hourly_move)
        return depth

    def update_vertial_position_fixed_range(self,length,old_light,current_light,current_depth,stomach_fullness,dt):
        """
        Update the vertical position of the current larva
        """
        swim_speed=30.0/86400.0*0.5
        max_hourly_move = swim_speed*dt
        
        if (old_light <= current_light): # and stomach_fullness >= lower_stomach_lim): #If light increases and stomach is sufficiently full, go down
          depth = min(0.0,current_depth - max_hourly_move)
        else: #If light decreases or stomach is not sufficiently full, go up
          depth = min(0,current_depth + max_hourly_move)
        return depth
        
    def update_larval_fish(self):
        """
        This is where we can include higher level complexity in the calculations of 
        growth, survial, development, and behavior of each individual 
        """
        # SETTINGS
        constant_ingestion = self.get_config('biology:constant_ingestion')
        active_metab_on = self.get_config('biology:active_metab_on')
        att_coeff = self.get_config('biology:attenuation_coefficient')
        total_competency_duration = self.get_config('biology:total_competency_duration')
        dt_drift=self.get_config('IBM:total_time_free_drift_before_competency') 
       
        # LIGHT UPDATE
        # Save the light from previous timestep to use for vertical behavior
        last_light=np.zeros(np.shape(self.elements.light))
        last_light[:]=self.elements.light[:]
        self.calculate_maximum_daily_light()
        # Light at depth of larvae assuming constant attenuation (can be changed to dependent on chlorophyll)
        self.elements.Eb=self.elements.light*np.exp(att_coeff*(self.elements.z))

        # FISH UPDATE
        self.update_larval_fish_development()
        
        # VERTICAL POSITION UPDATE
        dt=self.time_step.total_seconds()

        for ind in range(len(self.elements.lat)):
          if (self.elements.competency_duration[ind]>=total_competency_duration+dt_drift):
              
            if self.get_config('IBM:vertical_behavior_fixed_range') is True:
                self.elements.z[ind] = self.update_vertial_position_fixed_range(self.elements.length[ind],
                    last_light[ind],
                    self.elements.light[ind],
                    self.elements.z[ind],
                    self.elements.stomach_fullness[ind],
                    dt)
            if self.get_config('IBM:vertical_behavior_dynamic_range') is True:
                self.elements.z[ind] = self.update_vertial_position(self.elements.length[ind],
                last_light[ind],
                self.elements.light[ind],
                self.elements.z[ind],
                self.elements.stomach_fullness[ind],
                dt)


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
        self.elements.terminal_velocity=0.0 
        self.vertical_mixing() 
        
        # Update the growth and vertical position of each individual
        self.update_larval_fish()
        
        # Horizontal advection
        dt_drift=self.get_config('IBM:total_time_free_drift_before_competency') 
        dt_competence=self.get_config('IBM:total_time_free_drift_before_competency') 
        passive_drift_during_competence_period=self.get_config('IBM:passive_drift_during_competence_period') 
        
        if not passive_drift_during_competence_period:
          if (self.elements.age_seconds[ind] < dt_drift or self.elements.age_seconds[ind] > dt_drift+dt_competence):
              # TODO: Should make the larvae move to the bottom depth during dt_competence duration - how to find bottom depth?  
              self.advect_ocean_current()
        else:
              self.advect_ocean_current() 
       
        # Vertical advection
        if self.get_config('processes:verticaladvection') is True:
            self.vertical_advection()

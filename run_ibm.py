from datetime import datetime, timedelta
import numpy as np
from opendrift.readers import reader_basemap_landmask
from IBM.larval_fish import PelagicPlanktonDrift
from opendrift.readers import reader_netCDF_CF_generic

# seed the pseudorandom number generator
import random

# seed the pseudorandom number generator
from random import seed
from random import random
import logging
import os
from netCDF4 import Dataset, date2num,num2date
from numpy.random import RandomState
import matplotlib.pyplot as plt
import time
import config_loco as confm
import IBM.tools_loco as tools_loco
import random

__author__ = 'Trond Kristiansen'
__email__ = 'me (at) trondkristiansen.com'
__created__ = datetime(2019, 11, 19)
__modified__ = datetime(2019, 11, 19)
__version__ = "1.0"
__status__ = "Development, modified on 19.11.2019"

def setup_configuration(o,confobj):
    #######################
    # PHYSICS configuration
    #######################
    o.set_config('processes:turbulentmixing', False)
    o.set_config('processes:verticaladvection', False)
    o.set_config('turbulentmixing:diffusivitymodel','windspeed_Sundby1983')

    o.set_config('turbulentmixing:TSprofiles', False)
    o.set_config('drift:scheme', 'runge-kutta4')
    o.set_config('drift:max_age_seconds', confobj.maximum_life_span_seconds)

    o.set_config('general:coastline_action', 'previous') #Prevent stranding, jump back to previous position
  #  o.set_config('general:basemap_resolution', 'i')
    
    #######################
    # IBM configuration   
    #######################
    o.set_config('IBM:constant_ingestion', 0.75)
    o.set_config('IBM:active_metab_on', 1)
    o.set_config('IBM:attenuation_coefficient',0.18)
    
    # Define vertical behavior
    if confobj.experiment==1:
        o.set_config('IBM:vertical_behavior_fixed_range', True)
        o.set_config('IBM:vertical_behavior_dynamic_range', False)
    if confobj.experiment==2:
        o.set_config('IBM:vertical_behavior_fixed_range', False)
        o.set_config('IBM:vertical_behavior_dynamic_range', True)
        
    o.set_config('IBM:total_time_free_drift_before_competency', confobj.total_time_free_drift_before_competency)
    o.set_config('IBM:total_competency_duration', confobj.total_competency_duration)
    o.set_config('IBM:passive_drift_during_competence_period', confobj.passive_drift_during_competence_period)
    o.set_config('IBM:lower_stomach_lim',0.3) #Min. stomach fullness needed to actively swim down
    o.set_config('drift:max_age_seconds', confobj.maximum_life_span_seconds)
   
def createAndRunSimulation(confobj):

    """
    Setup a new simulation
    """

    o = PelagicPlanktonDrift(loglevel=0)
    o.complexIBM=confobj.complexIBM
    setup_configuration(o,confobj)

    """ 
    Read in the physical ocean forcing 
    """
    print("Trying to read file {}".format(confobj.basedir+confobj.pattern))
    reader_physics = reader_netCDF_CF_generic.Reader(confobj.basedir+confobj.pattern)
    o.add_reader([reader_physics ]) 
    # TODO: need to add wind forcing e.g. ERA5
    
    # For each station longitude-latitude we release particles for
    # 30 days at each depth level defined in depthlevels and we track each particle for
    # 1 day (drift:max_age_seconds', 86400)
    print("----------")
    print("Seed setup for {}".format(confobj.species))
    for day in range(confobj.totaldays_to_seed):
        print("=> Releasing {} particles within a radius of {} m on {} for each lat/lon location".format(confobj.releaseParticles,
                                                                                    confobj.releaseRadius,
                                                                                    confobj.startdate+timedelta(days=day)))
        o.seed_elements(lon=confobj.st_lons, 
                            lat=confobj.st_lats, 
                            number=confobj.releaseParticles, 
                            time=confobj.startdate+timedelta(days=day),
                            # TODO: maimum life_span_seconds
                            # TODO:  z="seafloor+0.5") need to add reader for variable 
                            # `sea_floor_depth_below_sea_level
                            z=-30+(1.0*random.randint(0,10))) 
    confobj.startdate += timedelta(days=1)
    print("----------")
    
    enddate_from_simulations=confobj.startdate+timedelta(days=confobj.totaldays_to_seed)+timedelta(seconds=confobj.maximum_life_span_seconds)
    if (enddate_from_simulations < confobj.enddate):
        print("End date for simulation is {}".format(enddate))
        enddate=enddate_from_simulations
    else:
        print("End date is hardcoded and will be shorter than expected from setup ({} vs {})".format(enddate_from_simulations,
                                                                                                     confobj.enddate))
        enddate=confobj.enddate
        
    o.run(end_time=enddate, 
        time_step=timedelta(minutes=30), 
        time_step_output=timedelta(minutes=30),
        outfile=confobj.outputFilename,
        # TODO: add 'sea_floor_depth_below_sea_level' when you have reader for it
        export_variables=['temp','z','x_sea_water_velocity', 'y_sea_water_velocity'])
    if not os.path.exists('Figures'): os.mkdir('Figures')
    
    pre, ext = os.path.splitext(os.path.basename(confobj.outputFilename))
    plotfile_name='Figures/'+pre[0:-1]+'_plot.png'
    o.plot(background=['x_sea_water_velocity', 'y_sea_water_velocity'],filename=plotfile_name)
    animfile_name='Figures/'+pre[0:-1]+'_animation.mp4'
   # o.animation(background=['x_sea_water_velocity', 'y_sea_water_velocity'], filename=animfile_name)
  
    o.plot_vertical_distribution(show_wind=False)
            
if __name__ == "__main__":
    start_time = time.time()

    confobj=confm.loco_conf()
    
    experiments = [2] # [1,2] 
    
    for experiment in experiments:
        confobj.experiment=experiment
        tools_loco.createOutputFilenames(confobj)
        print("Result files will be stored as:\nnetCDF=> {}".format(confobj.outputFilename))
        createAndRunSimulation(confobj)

    print("---  It took %s seconds to run the script ---" % (time.time() - start_time)) 
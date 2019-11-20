from datetime import datetime, timedelta
import numpy as np
from opendrift.readers import reader_basemap_landmask
from IBM.LarvalFish import LarvalFish

from opendrift.readers import reader_netCDF_CF_generic

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

def setup_configuration(o):
    #######################
    # PHYSICS configuration
    #######################
    
    o.set_config('processes:turbulentmixing',  False)
    o.set_config('processes:verticaladvection', False)
    o.set_config('turbulentmixing:diffusivitymodel','windspeed_Sundby1983')

    o.set_config('turbulentmixing:TSprofiles', False)
    o.set_config('drift:scheme', 'runge-kutta4')
    o.set_config('drift:max_age_seconds', confobj.maximum_life_span_seconds)

    o.set_config('general:coastline_action', 'previous') #Prevent stranding, jump back to previous position
    o.set_config('general:basemap_resolution', 'i')
    
    #######################
    # IBM configuration   
    #######################
    o.set_config('biology:constant_ingestion', 0.75)
    o.set_config('biology:active_metab_on', 1)
    o.set_config('biology:species', 'loco')
    o.set_config('biology:attenuation_coefficient',0.18)
    if confobj.verticalBehavior:
        o.set_config('biology:fraction_of_timestep_swimming',0.15) # Pause-swim behavior
    else:
        o.set_config('biology:fraction_of_timestep_swimming',0.00) # Pause-swim behavior
    o.set_config('biology:lower_stomach_lim',0.3) #Min. stomach fullness needed to actively swim down
   
def createAndRunSimulation(confobj):

    """
    Setup a new simulation
    """
    print("TRS 1");
    o = LarvalFish(loglevel=0)
    o.complexIBM=confobj.complexIBM
    print("TRS 2");
    setup_configuration(o)

    reader_basemap = reader_basemap_landmask.Reader(
        llcrnrlon=confobj.xmin, 
        llcrnrlat=confobj.ymin,
        urcrnrlon=confobj.xmax, 
        urcrnrlat=confobj.ymax,
        resolution='i', 
        projection='merc')
                       
    o.add_reader([reader_basemap]) 
    
    """ 
    Read in the physical ocean forcing 
    """
    print("Trying to read file {}".format(confobj.basedir+confobj.pattern))
    reader_physics = reader_netCDF_CF_generic.Reader(confobj.basedir+confobj.pattern)
    o.add_reader([reader_physics ]) 
   
    # For each station longitude-latitude we release particles for
    # 30 days at each depth level defined in depthlevels and we track each particle for
    # 1 day (drift:max_age_seconds', 86400)
    for day in range(confobj.totaldays):
        
        print('Seeding {} elements within a radius of {} m'.format(confobj.releaseParticles, 
        confobj.releaseRadius))

        print("Releasing {} particles between {} and {}".format(confobj.species,confobj.startdate,confobj.enddate))
        o.seed_elements(lon=confobj.st_lons, 
                            lat=confobj.st_lats, 
                            number=confobj.releaseParticles, 
                            time=confobj.startdate,
                            terminal_velocity=confobj.select_sinking_velocity,
                            z="seafloor+0.5")
    confobj.startdate += timedelta(days=1)
    print('Elements scheduled for {} : {}'.format(confobj.species,o.elements_scheduled))
    enddate=confobj.enddate+timedelta(days=confobj.totaldays)

    o.run(end_time=enddate, 
        time_step=timedelta(minutes=30), 
        time_step_output=timedelta(minutes=30),
        outfile=confobj.outputFilename,
        export_variables=['sea_floor_depth_below_sea_level','temp','z','x_sea_water_velocity', 'y_sea_water_velocity'])


if __name__ == "__main__":
    start_time = time.time()

    confobj=confm.loco_conf()
    
    experiments = [1]
    
    for experiment in experiments:
        confobj.experiment=experiment
        tools_loco.createOutputFilenames(confobj)
        print("Result files will be stored as:\nnetCDF=> {}".format(confobj.outputFilename))
        createAndRunSimulation(confobj)

    print("---  It took %s seconds to run the script ---" % (time.time() - start_time)) 
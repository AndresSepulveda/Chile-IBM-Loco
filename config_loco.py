#
#
# Config object for MarMine
import time, calendar
from datetime import datetime, timedelta
import numpy as np
import glob

__author__ = 'Trond Kristiansen'
__email__ = 'me (at) trondkristiansen.com'
__created__ = datetime(2019, 11, 19)
__modified__ = datetime(2019, 11, 19)
__version__ = "1.0"
__status__ = "Development, modified on 19.11.2019"


class loco_conf():

    def load_release_points(self):
        basedir_pointlocations='release_positions/'
       
        for filename in glob.glob(basedir_pointlocations+'*.txt'):
            with open(filename,'r') as f:
                lines = f.readlines()
                for line in lines:
                    l = line.split()
                    print("Release point: lon {} lat {}".format(float(l[0]),float(l[1])))
                    self.st_lons.append(float(l[0]))
                    self.st_lats.append(float(l[1]))
                f.close()
        return self.st_lons, self.st_lats
    
    def user_defined_inits(self):
        # Plotting options
        self.experiment=1
        self.plot_type='heatmap'
        self.requiredResolution=30 # km between bins
        self.xmin=-22.0
        self.xmax=23.5
        self.ymin=65.0
        self.ymax=78.0
        self.cmapname='RdYlBu_r'
        self.selectyear='all'
        
        # General options
        self.releaseParticles=10
        self.releaseRadius=150
        self.lowDepth=-200
        self.highDepth=0
        self.verticalBehavior=True
        self.loglevel=0
        self.complexIBM=False
        self.maximum_life_span_seconds=86400*30*3 # seconds in day * days * months
        
        if self.experiment == 1: 
            self.startdate=datetime(2019,11,1,0,0,0)
            self.enddate=datetime(2019,11,3,0,0,0)

        self.basedir='/Users/trondkr/Dropbox/NIVA/ChileIBM/Data/' 
        years=(np.linspace(self.startdate.year% 10,self.enddate.year% 10, (self.enddate.year-self.startdate.year)+1,endpoint=True)).astype(int)
        self.pattern= 'global-analysis-forecast-phy-001-024_1574195737035.nc' #'roms_nordic4.an.24h.201[{}-{}]*'.format(years[0],years[-1])

        self.species='loco'
        # LOCO - seed locations
        self.st_lons, self.st_lats = self.load_release_points()
        self.total_competency_duration=30

    def __init__(self):
        print('\nStarted ' + time.ctime(time.time()))

        self.paths=None
        self.mymap=None
        self.ax=None
        self.deltaX = None
        self.deltaY = None
        self.dx=None
        self.dy=None
        self.cmap=None
        self.outputFilename=None
        self.results_startdate=None
        self.results_enddate=None
        self.total_competency_duration=None
        self.loglevel=None
        self.complexIBM=None
        self.st_lons=[]
        self.st_lats=[] 
        self.user_defined_inits()
    


import time
from datetime import datetime, timedelta
import numpy as np
import glob

#
# Config file for Chile Loco
#
__author__ = 'Trond Kristiansen'
__email__ = 'me (at) trondkristiansen.com'
__created__ = datetime(2019, 11, 19)
__modified__ = datetime(2020, 3, 4)
__version__ = "1.0"
__status__ = "Development, modified on 19.11.2019, 19.12.2019, 04.03.2020"


class LocoConf:

    def load_release_points(self):
        basedir_pointlocations = 'release_positions/'

        for filename in glob.glob(basedir_pointlocations + '*.txt'):
            with open(filename, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line_split = line.split()
                    print("Release point: lon {} lat {}".format(float(line_split[0]), float(line_split[1])))
                    self.st_lons.append(float(line_split[0]))
                    self.st_lats.append(float(line_split[1]))
                f.close()
        return self.st_lons, self.st_lats

    def __init__(self):
        print('\nStarted ' + time.ctime(time.time()))

        self.paths = None
        self.mymap = None
        self.ax = None
        self.deltaX = None
        self.deltaY = None
        self.dx = None
        self.dy = None
        self.cmap = None
        self.outputFilename = None
        self.results_startdate = None
        self.results_enddate = None
        self.total_competency_duration = None
        self.loglevel = None
        self.complexIBM = None
        self.st_lons = []
        self.st_lats = []

        # General options
        self.experiment = 1
        # Number of particles released for each seed location and time
        self.releaseParticles = 4
        # The radius around the seed location for particles to be seeded
        self.releaseRadius = 1000

        self.verticalBehavior = True
        self.loglevel = 0
        self.complexIBM = False
        self.maximum_life_span_seconds = 86400 * 30 * 3  # seconds in day * days * months

        if self.experiment == 1 or self.experiment == 2:
            self.startdate = datetime(2008, 6, 1, 0, 0, 0)
            self.enddate = datetime(2008, 6, 20, 0, 0, 0)

        self.basedir = '/Users/trondkr/Dropbox/NIVA/ChileIBM/Data/'
        years = (
            np.linspace(self.startdate.year % 10, self.enddate.year % 10, (self.enddate.year - self.startdate.year) + 1,
                        endpoint=True)).astype(int)
        self.pattern = 'croco_avg.nc'  # 'global-analysis-forecast-phy-001-024_1574195737035.nc'  # 'roms_nordic4.an.24h.201[{}-{}]*'.format(years[0],years[-1])

        self.species = 'loco'
        # LOCO - seed locations
        self.st_lons, self.st_lats = self.load_release_points()
        # Total time at teh bottom prior to starting vertical behavior
        self.total_competency_duration = 3. * 24.0 * 3600.0  # days in seconds
        # Total time free drift before settlement to bottom for competency_duration
        self.total_time_free_drift_before_competency = 1. * 24 * 3600.  # days in seconds
        self.totaldays_to_seed = 30  # days
        self.passive_drift_during_competence_period = True

        # Plotting options
        self.plot_type = 'heatmap'
        self.requiredResolution = 30  # km between bins
        # min longitude
        self.xmin = 260.0
        # max longitude
        self.xmax = 300.0
        # min latitude
        self.ymin = -40.0
        # max latitude
        self.ymax = -20.0
        self.cmapname = 'RdYlBu_r'
        self.selectyear = 'all'

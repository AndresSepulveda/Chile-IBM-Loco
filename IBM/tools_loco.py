
from datetime import datetime, timedelta
import numpy as np
import os
import time
import config_loco as confm

__author__ = 'Trond Kristiansen'
__email__ = 'me (at) trondkristiansen.com'
__created__ = datetime(2019, 11, 19)
__modified__ = datetime(2019, 11, 19)
__version__ = "1.0"
__status__ = "Development, modified on 19.11.2019"


def createOutputFilenames(confobj):
    startDate=''
    if confobj.startdate.day<10:
        startDate+='0%s'%(confobj.startdate.day)
    else:
        startDate+='%s'%(confobj.startdate.day)

    if confobj.startdate.month<10:
        startDate+='0%s'%(confobj.startdate.month)
    else:
        startDate+='%s'%(confobj.startdate.month)

    startDate+='%s'%(confobj.startdate.year)

    endDate=''
    if confobj.enddate.day<10:
        endDate+='0%s'%(confobj.enddate.day)
    else:
        endDate+='%s'%(confobj.enddate.day)

    if confobj.enddate.month<10:
        endDate+='0%s'%(confobj.enddate.month)
    else:
        endDate+='%s'%(confobj.enddate.month)

    endDate+='%s'%(confobj.enddate.year)
 
    # File naming
    if confobj.verticalBehavior:
        outputFilename='results/%s_opendrift_%s_to_%s_vertical.nc'%(confobj.species,startDate,endDate)
    else:
        outputFilename='results/%s_opendrift_%s_to_%s_novertical.nc'%(confobj.species,startDate,endDate)
    if not os.path.exists('results'):
        os.makedirs('results')
    if os.path.exists(outputFilename):
        os.remove(outputFilename)
        
    confobj.outputFilename=outputFilename
import math, datetime
import config_loco

"""
Functions to estimate maximum surface light as a function of day of the year and latitude. 
Based on the surface light and depth, and size of the larvae we calculate the perception distance of fish.

Functions in module:

1. [umol s-1 m-2]=surface_light(julian, lat, hour)
2. [mm]=getPerceptionDistance(k,Ke,Ap,Eb)

"""  
__author__   = 'Trond Kristiansen'
__email__    = 'trond.kristiansen@niva.no'
__created__  = datetime.datetime(2019, 11, 18)
__modified__ = datetime.datetime(2019, 11, 18)
__version__  = "1.1"
__status__   = "Production"

def surface_light(timetup, lat):
    
    """
    Max light at sea surface
    """
    MAXLIG = 500.0
    
    print("Calculating light for {}".format(timetup))
      
    D = float(timetup.tm_yday)
    H = float(timetup.tm_min)
    
    P = math.pi
    TWLIGHT = 0.76
    grdSTATION.ratioOfMaxLight = (MAXLIG * 0.1 + MAXLIG * abs(math.sin(math.pi*(D*1.0)/365.0))) / MAXLIG
    
    MAXLIG = MAXLIG * 0.1 + MAXLIG * abs(math.sin(math.pi*(D*1.0)/365.0))
    
    """
    Originally the calculation of light as a function of lat, time of day, and time of year was setup for
    sind, cosd of degrees. I converted all to radians using math.radians to suit the python standard.
       
    Test suite: 2440000 should give 1968, 05, 23, 00, 00, 00
    for k in range(24):
        surface_light(2440000+k/24.,42.0)
        print 2440000+k/24.
        
    print(julian_day(1968,05,23,00))
    """

    DELTA = 0.3979*math.sin(math.radians(0.9856*(D-80)+ 1.9171*(math.sin(math.radians(0.9856*D))-0.98112)))
    H12 = DELTA*math.sin(math.radians(lat*1.))- math.sqrt(1.-DELTA**2)*math.cos(math.radians(lat*1.))*math.cos(math.radians(15.0*12.0))
    HEIGHT = DELTA*math.sin(math.radians(lat*1.))- math.sqrt(1.-DELTA**2)*math.cos(math.radians(lat*1.))*math.cos(math.radians(15.0*H))
      
    V = math.asin(HEIGHT)
  
    if (V > 0.0):                 
        s_light = MAXLIG*(HEIGHT/H12) + TWLIGHT
    elif (V >= -6):
        s_light = ((TWLIGHT - 0.048)/6.)*(6.+V)+.048
    elif (V >= -12):
        s_light = ((0.048 - 1.15e-4)/6.)*(12.+V)+1.15e-4
    elif (V >= -18):
        s_light = (((1.15e-4)-1.15e-5)/6.)*(18.+V)+1.15e-5
    else:
        s_light = 1.15e-5
        
    print("Day of year {}  hour {} date {} ".format(tt[7], tt[3], gtime, s_light, Lat))
    return s_light
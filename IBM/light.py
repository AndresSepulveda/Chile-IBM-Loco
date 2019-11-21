import datetime
import numpy as np
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
    
    P = np.pi
    TWLIGHT = 0.76
    ratioOfMaxLight = (MAXLIG * 0.1 + MAXLIG * abs(np.sin(P*(D*1.0)/365.0))) / MAXLIG
    
    MAXLIG = MAXLIG * 0.1 + MAXLIG * abs(np.sin(P*(D*1.0)/365.0))
    
    """
    Originally the calculation of light as a function of lat, time of day, and time of year was setup for
    sind, cosd of degrees. I converted all to radians using np.radians to suit the python standard.
       
    Test suite: 2440000 should give 1968, 05, 23, 00, 00, 00
    for k in range(24):
        surface_light(2440000+k/24.,42.0)
        print 2440000+k/24.
        
    print(julian_day(1968,05,23,00))
    """
  
    DELTA = 0.3979*np.sin(np.radians(0.9856*(D-80)+ 1.9171*(np.sin(np.radians(0.9856*D))-0.98112)))
    H12 = DELTA*np.sin(np.radians(lat*1.))- np.sqrt(1.-DELTA**2)*np.cos(np.radians(lat*1.))*np.cos(np.radians(15.0*12.0))
    HEIGHT = DELTA*np.sin(np.radians(lat*1.))- np.sqrt(1.-DELTA**2)*np.cos(np.radians(lat*1.))*np.cos(np.radians(15.0*H))
      
    V = np.arcsin(HEIGHT)
    s_light=V.copy()
    print("test")
    
    s_light[V>=-24] = 1.15e-5
    s_light[V>=-18] = (((1.15e-4)-1.15e-5)/6.)*(18.+s_light[V>=-18])+1.15e-5
    s_light[V>=-12] = ((0.048 - 1.15e-4)/6.)*(12.+s_light[V>=-12])+1.15e-4
    s_light[V>=-6] = ((TWLIGHT - 0.048)/6.)*(6.+s_light[V>=-6])+.048
    
    s_light[V>0.0] = MAXLIG*(HEIGHT[V>0.0]/H12[V>0.0]) + TWLIGHT
  
    print("Day of year {}  hour {} date {} ave. light {} ".format(timetup[7], timetup[3], timetup, s_light))
    return s_light
#!/usr/bin/env python

import matplotlib
matplotlib .use ('Agg')
import sys
import os

# Asignar la ruta en donde esta instalado opendrift.
sys.path.append ('/home/mosa/opendrift/')

import os
from datetime import datetime ,timedelta
import numpy as np
import time

from opendrift.readers import reader_ROMS_native
from opendrift.models .oceandrift import OceanDrift

import pandas as pd

#
# Release point
#
inputfile='./release_points/PuntosCostaAncud.txt'
inputdf=pd.read_csv(inputfile, sep=" ")
ubic=np.array(inputdf)
alats=ubic[:,1]
alons=ubic[:,0]
depths=-40       # Release depth

lats=alats[::3]  # Every j-th location....
lons=alons[::3]

ene=len(lats)
print(ene)

auxj=sys.argv[1]
j=int(auxj)

#time.sleep(5)

#particles=1*lats.size*lons.size # size(lats)*size(lons)
radii     = 1500  #  in [m]
nparts    = 100   #  Total = nparts * num_steps
initime   = 1
num_steps = 360   #  15days * 24hours
time_step = timedelta ( hours = 1 )

#
# Velocity field
#
filename_nc ='../../IFOP_LosRios/hourly/croco_his.nc.2';

#
# Liberacion en el tiempo
#
###for j in range( ene ):

o =OceanDrift (loglevel = 0 )
mosa_native=reader_ROMS_native.Reader(filename_nc )
mosa_native.interpolation ='linearND'
o.add_reader ([mosa_native ])
stime = mosa_native.start_time
o.set_config('general:coastline_action', 'previous')

print("Punto "+str(j)+": Latitud  "+str(lats[j])+" Longitud "+str(lons[j]))

for i in range ( 1,num_steps + 1 ):
    o.seed_elements (lons[j], lats[j], z=depths, radius = radii, number = nparts, time = stime + i * time_step  )

rname =  "./results_depth/onebyone_Ancud_site_{0}_z{1}.nc".format(j,depths)
if j < 100:
   rname =  "./results_depth/onebyone_Ancud_site_0{0}_z{1}.nc".format(j,depths)
if j < 10:
   rname =  "./results_depth/onebyone_Ancud_site_00{0}_z{1}.nc".format(j,depths)
#
# Simulacion
#
# 4320 = 30*24*6
o.run(steps=4320, time_step=timedelta(minutes=10), time_step_output=timedelta(hours=1), outfile=rname)

fname =  "./Figures/onebyone_Ancud_site_{0}_z{1}.png".format(j,depths)
if j < 100:
   fname =  "./Figures/onebyone_Ancud_site_0{0}_z{1}.png".format(j,depths)
if j < 10:
   fname =  "./Figures/onebyone_Ancud_site_00{0}_z{1}.png".format(j,depths)
print(fname)
time.sleep(2)
o.plot(filename =fname)
    #o.animation (filename ='./Animations/many_v3.mp4')

o.reset()
cmd="rm "+rname
os.system(cmd)

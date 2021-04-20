#!/bin/bash

for i in {1..319..3}
   do
	echo "Simulando sitio $i"
	python3 many_onebyone.py $i
#	python3 many_short.py $i
   done

"""
tryspice.py

Created by Klaus-Michael Aye on 2011-02-26.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

from matplotlib.pylab import *
import numpy as np
from spice import *
import datetime
import sys

furnsh('bepic.mk')
radii = bodvrd('MERCURY','RADII',3)

def get_et_array_from_dates(dates, interval):
    et1 = utc2et(dates[0])
    et2 = utc2et(dates[1])
    return arange(et1,et2,interval)

def get_spkpos_distance(et):
	pos = spkpos('mercury',et,'iau_mercury','none','mpo')
	return vnorm(pos[0])-radii[1][0]

def get_pnt_distance(et):
	pnt = subpnt('nearpoint:ellipsoid','mercury',et,'iau_mercury','lt+s','mpo')
	return vnorm(pnt[0])

vec_spkpos_distance = np.vectorize(get_spkpos_distance)	
vec_pnt_distance = np.vectorize(get_pnt_distance)

if __name__ == '__main__':
	dateranges = []
	dateranges.append(['2021 JAN 30 12:00:00.000', '2021 JAN 31 12:00:00.000'])
	dateranges.append(['2021 MAY 29 12:00:00.000', '2021 MAY 30 12:00:00.000'])

	times = []
	for dates in dateranges:
		times.append(get_et_array_from_dates(dates,60)) # 60 -> per minute

	distances = []
	for t_array in times:
	    distances.append(vec_spkpos_distance(t_array))
	    # distances.append(vec_pnt_distance(t_array))

	# gradients = []
	# for elem in distances:
	#     gradients.append(gradient(elem)/60.)
	
	# times = array(times[0],times[1])
	# distances = array(distances[0],distances[1])
	plot(times[0][:-1],distances[0][:-1]/distances[1])
	show()
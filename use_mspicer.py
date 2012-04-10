from __future__ import division
from mars_spice import MarsSpicer
from spice import vsep
import numpy as np
from matplotlib.pyplot import figure, show
import datetime as dt

 # default time is now:
mspice = MarsSpicer()
mspice.set_spoint_by(lat=85, lon = 0)

# tilt the surface normal by 30 degree to the north (north = default)
mspice.get_tilted_normal(30)

# rotate the tilted vector around the local surface normal to create an aspect angle
# mspice.rotate_tnormal(20)

mspice.time -= dt.timedelta(200)
start_time = mspice.time

bigtimes = []
energies_30 = []
while (mspice.l_s < 180):
    
    ls_start = mspice.l_s
    print(ls_start)
    bigtimes.append(ls_start)
    times = []
    data = []
    while (mspice.l_s - ls_start) < 10:
        times.append(mspice.l_s)
        diff_angle = vsep(mspice.tnormal, mspice.sun_direction)
        if np.degrees(diff_angle) > 90:
            to_append = 0
        else:
            to_append = mspice.solar_constant*3600*np.cos(diff_angle)
            # to_append = mspice.solar_constant*np.cos(diff_angle)
        data.append(to_append)
        mspice.advance_time_by(3600)
    energies_30.append(np.sum(data))
    
    
mspice.time = start_time
energies_0 = []
mspice.get_tilted_normal(5)

while (mspice.l_s < 180):
    ls_start = mspice.l_s
    print(ls_start)
    times = []
    data = []
    while (mspice.l_s - ls_start) < 10:
        times.append(mspice.l_s)
        diff_angle = vsep(mspice.tnormal, mspice.sun_direction)
        if np.degrees(diff_angle) > 90:
            to_append = 0
        else:
            to_append = mspice.solar_constant*3600*np.cos(diff_angle)
            # to_append = mspice.solar_constant*np.cos(diff_angle)
        data.append(to_append)
        mspice.advance_time_by(3600)
    energies_0.append(np.sum(data))

mspice.time = start_time
energies_asp_90 = []

mspice.get_tilted_normal(30)
mspice.rotate_tnormal(90)
while (mspice.l_s < 180):
    ls_start = mspice.l_s
    print(ls_start)
    times = []
    data = []
    while (mspice.l_s - ls_start) < 10:
        times.append(mspice.l_s)
        diff_angle = vsep(mspice.trnormal, mspice.sun_direction)
        if np.degrees(diff_angle) > 90:
            to_append = 0
        else:
            to_append = mspice.solar_constant*3600*np.cos(diff_angle)
            # to_append = mspice.solar_constant*np.cos(diff_angle)
        data.append(to_append)
        mspice.advance_time_by(3600)
    energies_asp_90.append(np.sum(data))

fig = figure()
ax = fig.add_subplot(111)
ax.plot(bigtimes,energies_30,label = 'inc: 30 deg')
ax.plot(bigtimes,energies_0,label = 'inc: 5 deg')
ax.plot(bigtimes,energies_asp_90,label = 'inc: 30 deg, asp: 90 deg')
ax.legend(loc='best')
show()
from __future__ import division
from mars_spice import MarsSpicer
from spice import vsep
import numpy as np
from matplotlib.pyplot import figure, show
import datetime as dt

def inner_loop(ls_res, vector,time_res=3600):
    """
    This is the inner loop that samples over <ls_res> L_s values and returns
    the integral for that time interval.
    
    Parameters:
        ls_res - Resolution of L_s over which to sample
        vector - attribute string for the vector to use as normal. Choice
                 between (surface normal: snormal, tilted normal: tnormal, 
                 tilted and rotated normal: trnormal)
        time_res - seconds over which to sample the energy, default is 1 hour
    """
    ls_start = mspice.l_s
    times = []
    data = []
    while (mspice.l_s - ls_start) < ls_res:
        times.append(mspice.l_s)
        diff_angle = vsep(getattr(mspice,vector), mspice.sun_direction)
        if np.degrees(diff_angle) > 90:
            to_append = 0
        else:
            to_append = mspice.solar_constant * time_res * np.cos(diff_angle)
            # to_append = mspice.solar_constant*np.cos(diff_angle)
        data.append(to_append)
        mspice.advance_time_by(time_res)
    return (times, data)

def outer_loop(stop_ls, ls_res, vector, time_res = 3600):
    bigtimes = []
    energies = []
    while not np.allclose([mspice.l_s],[stop_ls],atol=ls_res):
        ls_start = mspice.l_s
        print(ls_start)
        bigtimes.append(ls_start)
        times, data = inner_loop(ls_res, vector, time_res)
        energies.append(np.sum(data))
    return (bigtimes, energies)
    

 # default time is now:
mspice = MarsSpicer()

# set up location
mspice.set_spoint_by(lat=85, lon = 0)

# set up starting time of analysis
mspice.time -= dt.timedelta(200)

# stopping l_s value
end_ls = 360

# l_s resolution
ls_res = 10

# save this time for multiple runs for resetting mspice each time
start_time = mspice.time

# container for all energy arrays
energies = []

# labels for the plotting
labels = []

# tilt the surface normal by 30 degree to the north (north = default)
# this creates an instance variable called 'tnormal'
mspice.get_tilted_normal(30)

# first time, save the bigtimes array
bigtimes, energies_t30 = outer_loop(end_ls, ls_res, 'tnormal')
energies.append(energies_t30)
labels.append('t30')

# rotate the tilted vector around the local surface normal to create an aspect 
# angle
# this creates an instance variable called 'trnormal'
mspice.rotate_tnormal(90)

mspice.time = start_time
energies.append(outer_loop(end_ls, ls_res, 'trnormal')[1])
labels.append('t30_a90')

mspice.time = start_time
energies.append(outer_loop(end_ls, ls_res, 'snormal')[1])
labels.append('flat')


mspice.rotate_tnormal(180)
mspice.time = start_time
energies.append(outer_loop(end_ls, ls_res, 'trnormal')[1])
labels.append('t30,a180')

fig = figure()
ax = fig.add_subplot(111)
for energy,label in zip(energies,labels):
    ax.plot(bigtimes,energy, label = label)
ax.legend(loc='best')
show()
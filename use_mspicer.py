from __future__ import division
from mars_spice import MarsSpicer
from spice import vsep
import numpy as np
from matplotlib.pyplot import figure, show
import datetime as dt

 # default time is now:
mspice = MarsSpicer()
mspice.set_spoint_by(lat=85, lon = 0)


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


# set up starting time of analysis
mspice.time -= dt.timedelta(200)
# save this time for multiple runs for resetting mspice each time
start_time = mspice.time


def outer_loop(stop_ls, ls_res, vector, time_res = 3600):
    bigtimes = []
    energies = []
    while (mspice.l_s < stop_ls):
        ls_start = mspice.l_s
        print(ls_start)
        bigtimes.append(ls_start)
        times, data = inner_loop(ls_res, vector, time_res)
        energies.append(np.sum(data))
    return (bigtimes, energies)
    

# container for all energy arrays
energies = []
# labels for the plotting
labels = []
# tilt the surface normal by 30 degree to the north (north = default)
# this creates an instance variable called 'tnormal'
mspice.get_tilted_normal(30)

bigtimes, energies_t30 = outer_loop(180, 10, 'tnormal')
energies.append(energies_t30)
labels.append('t30')

# rotate the tilted vector around the local surface normal to create an aspect 
# angle
# this creates an instance variable called 'trnormal'
mspice.rotate_tnormal(90)

mspice.time = start_time
energies.append(outer_loop(180, 10, 'trnormal')[1])
labels.append('t30_a90')

mspice.time = start_time
energies.append(outer_loop(180, 10, 'snormal')[1])
labels.append('flat')


# mspice.time = start_time
# mspice.get_tilted_normal(5)
# 
# while (mspice.l_s < 180):
#     ls_start = mspice.l_s
#     print(ls_start)
#     times = []
#     data = []
#     while (mspice.l_s - ls_start) < 10:
#         times.append(mspice.l_s)
#         diff_angle = vsep(mspice.tnormal, mspice.sun_direction)
#         if np.degrees(diff_angle) > 90:
#             to_append = 0
#         else:
#             to_append = mspice.solar_constant*3600*np.cos(diff_angle)
#             # to_append = mspice.solar_constant*np.cos(diff_angle)
#         data.append(to_append)
#         mspice.advance_time_by(3600)
#     energies_0.append(np.sum(data))
# 
# mspice.time = start_time
# energies_asp_90 = []
# 
# mspice.get_tilted_normal(30)
# mspice.rotate_tnormal(90)
# while (mspice.l_s < 180):
#     ls_start = mspice.l_s
#     print(ls_start)
#     times = []
#     data = []
#     while (mspice.l_s - ls_start) < 10:
#         times.append(mspice.l_s)
#         diff_angle = vsep(mspice.trnormal, mspice.sun_direction)
#         if np.degrees(diff_angle) > 90:
#             to_append = 0
#         else:
#             to_append = mspice.solar_constant*3600*np.cos(diff_angle)
#             # to_append = mspice.solar_constant*np.cos(diff_angle)
#         data.append(to_append)
#         mspice.advance_time_by(3600)
#     energies_asp_90.append(np.sum(data))

fig = figure()
ax = fig.add_subplot(111)
for energy,label in zip(energies,labels):
    ax.plot(bigtimes,energy, label = label)
ax.legend(loc='best')
show()
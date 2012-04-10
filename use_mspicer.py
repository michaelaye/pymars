from __future__ import division
from mars_spice import MarsSpicer
from spice import vsep
import numpy as np
from matplotlib.pyplot import figure, show, grid
import datetime as dt

def inner_loop(mspice, ls_res, vector,time_res=3600):
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
    start_ls = mspice.l_s
    old_ls = 0
    data = []
    # while summing up within required ls_res and not crossing 360
    while (mspice.l_s < start_ls + ls_res) and (mspice.l_s > old_ls):
        old_ls = mspice.l_s
        diff_angle = vsep(getattr(mspice,vector), mspice.sun_direction)
        if (mspice.illum_angles.dsolar > 90) or (np.degrees(diff_angle) > 90):
            to_append = 0
        else:
            to_append = mspice.solar_constant * time_res * np.cos(diff_angle)
            # to_append = mspice.solar_constant*np.cos(diff_angle)
        data.append(to_append)
        mspice.advance_time_by(time_res)
    # create the best possible value for the integration by summing:
    energy = (np.sum(data[:-1]) + np.sum(data[1:]))/2.0
    return energy, (old_ls - start_ls)

def outer_loop(mspice, end_ls, ls_res, vector, time_res = 3600):
    bigtimes = []
    energies = []
    old_ls = 0
    # while l_s not jumping over 360 and l_s smaller than end criterium:
    while (mspice.l_s > old_ls) and (mspice.l_s < end_ls):
        print(mspice.l_s)
        old_ls = mspice.l_s
        bigtimes.append(mspice.l_s + ls_res/2 )
        energy, delta = inner_loop(mspice, ls_res, vector, time_res)
        energies.append(energy * 10.0/delta)
    return (bigtimes, energies)
    

def main():
     # default time is now:
    mspice = MarsSpicer()

    # set up location
    mspice.set_spoint_by(lat=85, lon = 0)

    # set up starting time of analysis, l_s = 0
    mspice.utc = '2011-09-13T14:24:33.733548'

    # mspice.time += dt.timedelta(30)
    # ls1 = mspice.l_s
    # utc1 = mspice.utc
    # mspice.time += dt.timedelta(1)
    # ls2 = mspice.l_s
    # mspice.utc = utc1
    
    # stopping l_s value
    end_ls = 360

    # l_s resolution
    # ls_res = 0.02
    ls_res = 5.0

    # time resolution
    time_res = 3600
    
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
    bigtimes, energies_t30 = outer_loop(mspice, end_ls, ls_res, 'tnormal',time_res=time_res)
    energies.append(energies_t30)
    labels.append('t30')

    # rotate the tilted vector around the local surface normal to create an aspect 
    # angle
    # this creates an instance variable called 'trnormal'
    mspice.rotate_tnormal(90)

    mspice.time = start_time
    energies.append(outer_loop(mspice, end_ls, ls_res, 'trnormal',time_res=time_res)[1])
    labels.append('t30_a90')

    mspice.time = start_time
    energies.append(outer_loop(mspice, end_ls, ls_res, 'snormal',time_res=time_res)[1])
    labels.append('flat')


    mspice.rotate_tnormal(180)
    mspice.time = start_time
    energies.append(outer_loop(mspice, end_ls, ls_res, 'trnormal',time_res=time_res)[1])
    labels.append('t30,a180')

    fig = figure()
    ax = fig.add_subplot(111)
    grid()
    for energy,label in zip(energies,labels):
        ax.plot(bigtimes,energy, '-*', label=label)
    ax.set_xlabel('L_s [deg]')
    ax.set_ylabel('Insolation per 10 L_s [MJ]')
    ax.set_title('Insolation of t_ilted and a_spected (rotated) surfaces at 85 N')
    ax.legend(loc='best')
    show()
    return (energies, labels)
    
if __name__ == '__main__':
    energies, labels = main()
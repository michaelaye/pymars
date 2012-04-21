from __future__ import division
from mars_spice import MarsSpicer
import datetime as dt
import numpy as np
import pprint
from spice import vsep
import math
from matplotlib.pyplot import plot, show, semilogy

def create_arrays(mspicer, N, dt):
    ets = []
    energies = []
    for _ in range(N):
        ets.append(mspicer.et)
        energies.append(mspicer.F_flat)
        mspicer.time += dt
    return np.array((ets, energies))

def create_trnormal_arrays(mspicer, N, dt):
    ets = []
    energies = []
    for _ in range(N):
        ets.append(mspicer.et)
        diff_angle = vsep(mspicer.trnormal, mspicer.sun_direction)
        if (mspicer.illum_angles.dsolar > 90) or (np.degrees(diff_angle) > 90):
            to_append = 0
        else:
            to_append = mspicer.solar_constant * dt.seconds * math.cos(diff_angle)
        energies.append(to_append)
        mspicer.time += dt
    return np.array((ets, energies))
  
def save_data_to_file(data, fname, start, dt):
    with open(fname,'w') as f:
        f.write('# Start: {1}, dt: {0} s, Intensities in J/(dt*m**2)\n'.format(dt.seconds,start.isoformat()))
        np.savetxt(f, data.T)
        
# location setup
mspicer = MarsSpicer()
mspicer.set_spoint_by(lat=85,lon=0)

# timing setup
mspicer.goto_ls_0()
mspicer.time -= dt.timedelta(days=10,hours=12)

# dt, the time step
my_dt = dt.timedelta(hours=1)

# saving for restart later
start_time = mspicer.time
    
out_flat = create_arrays(mspicer, 50, my_dt)
save_data_to_file(out_flat[1], 'insolation_flat.txt', start_time, my_dt)

mspicer.get_tilted_normal(30)
mspicer.rotate_tnormal(180)

mspicer.time = start_time
out_ta = create_trnormal_arrays(mspicer, 50, my_dt)
save_data_to_file(out_ta[1], 'insolation_t30_a180.txt', start_time, my_dt)

# print(np.divide(out_ta[1],out_flat[1]))
# semilogy(np.divide(out_ta[1],out_flat[1]),'-*')
# show()
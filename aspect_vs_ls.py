from __future__ import division
import numpy as np
from matplotlib.pyplot import figure, show, cm, grid
from use_mspicer import outer_loop
from mars_spice import MarsSpicer
    
 # default time is now:
mspice = MarsSpicer()

# set up location
mspice.set_spoint_by(lat=85, lon = 0)

# set up starting time of analysis, l_s = 0
mspice.utc = '2011-09-13T14:24:33.733548'

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

aspects = np.arange(0,180,30)
tilts = [5,30]
img = np.zeros((len(aspects), 36, 2))

for i,tilt in enumerate(tilts):
    mspice.time = start_time
    mspice.get_tilted_normal(tilt)
    for j,aspect in enumerate(aspects):
        print('aspect = {0}'.format(aspect))
        mspice.rotate_tnormal(aspect+15) # go to middle of aspect block
        bigtimes, energy = outer_loop(mspice, end_ls, ls_res, 'trnormal')
        energies.append(energy)
        labels.append('t'+str(tilt)+'_a'+str(aspect))
        img[j,:,i] = energy


img[ img < 1 ] = np.nan
img5 = img[:,:,0]
img30 = img[:,:,1]
palette = cm.jet
palette.set_bad('gray')
grid()
fig = figure()
ax = fig.add_subplot(111)
ax.imshow(img[:,:,0],origin='lower')
show()

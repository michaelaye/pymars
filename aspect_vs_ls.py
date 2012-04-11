from __future__ import division
import numpy as np
from matplotlib.pyplot import figure, show, cm, grid, subplots
from matplotlib.ticker import MultipleLocator
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

aspects = np.arange(0,180,5)
tilts = [5,30]
img = np.zeros((len(aspects), 36, 2))

for i,tilt in enumerate(tilts):
    mspice.get_tilted_normal(tilt)
    for j,aspect in enumerate(aspects):
        mspice.time = start_time
        print('aspect = {0}'.format(aspect))
        mspice.rotate_tnormal(aspect+15) # go to middle of aspect block
        bigtimes, energy = outer_loop(mspice, end_ls, ls_res, 'trnormal')
        energies.append(energy)
        labels.append('t'+str(tilt)+'_a'+str(aspect))
        img[j,:,i] = energy


img[ img < 1 ] = np.nan
img5 = img[:,:,0]
img30 = img[:,:,1]
images = [img5,img30]
palette = cm.jet
palette.set_bad('gray')
fig, axes = subplots(2,1,sharex=True, sharey=True)
ext = [0,360,0,180]
max = np.nanmax(img5)
xmajorLocator = MultipleLocator(30)
xminorLocator = MultipleLocator(10)
ymajorLocator = MultipleLocator(30)
yminorLocator = MultipleLocator(10)
for ax,image in zip(axes,images):
    im = ax.imshow(image, cmap=palette, vmax=max, origin='lower',extent=ext)
    ax.set_ylabel('Aspect [deg]')
    ax.xaxis.set_major_locator(xmajorLocator)
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.grid()
axes[0].annotate(r'5$^o$ slope',xy=(220,90),backgroundcolor='white',fontsize='large')
axes[1].annotate(r'30$^o$ slope',xy=(220,90),backgroundcolor='white',fontsize='large')
cb = fig.colorbar(im,ax=ax, orientation='horizontal', use_gridspec=True,fraction=0.1,aspect=40)
cb.set_label(r'Insolation [MJ / 10 $L_s$]')
axes[0].set_xlabel('L_s [deg]')
show()

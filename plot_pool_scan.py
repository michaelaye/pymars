#!/usr/bin/env python
# encoding: utf-8

from matplotlib.pylab import *
from hirise_tools import *
import os

root = '/Users/maye/results/from_hirise_server'
dirs = os.listdir(root)

def get_obsid(s):
    return s[11:15]

def get_blocksize(s):
    sl =s.split('_')
    return sl[3]
    
means_0985 = []
means_0945 = []
errors_0945 = []
errors_0985 = []
obsids_0985 = []
obsids_0945 = []
for d in dirs:
    if get_blocksize(d) != '256': continue
    os.chdir(os.path.join(root,d))
    blobs = np.load('blobs.npy')
    if get_obsid(d) == '0945':
        means_0945.append(blobs.mean())
        errors_0945.append(blobs.std())
        obsids_0945.append(int(d[4:10]))
    elif get_obsid(d) == '0985':
        means_0985.append(blobs.mean())
        errors_0985.append(blobs.std())
        obsids_0985.append(int(d[4:10]))
plot(obsids_0945,means_0945,'ob',label='Ithaca')
plot(obsids_0985, means_0985,'or',label='Inca City')
plot(obsids_0945,means_0945,'b')
plot(obsids_0985, means_0985,'r')
xlabel('Orbit number')
ylabel('Fraction of ground covered with blobs/jets')
legend()
show()

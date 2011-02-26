#!/Library/Frameworks/EPD64.framework/Versions/Current/bin/python
# encoding: utf-8
"""
tryspice.py

Created by Klaus-Michael Aye on 2011-02-26.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

from matplotlib.pylab import *
from spice import *
import datetime

furnsh('bepic.mk')

radii = bodvrd('MERCURY','RADII',3)
print radii
daterange=['2021 JAN 30 12:00:00.000', '2022 MAY 02 03:42:42.623']

et1 = utc2et(daterange[0])
et2 = utc2et(daterange[1])
print et2utc(et2,'ISOC',5)
times = arange(et1,et2-80,600)
print et2utc(times[-1],'ISOC',5)

distances = []
for t in times:
    pos = spkpos('mercury',t,'j2000','none','mpo')
    distances.append(vnorm(pos[0]))
    
plot(times,array(distances)-radii[1][0])
show()
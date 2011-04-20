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
import sys

furnsh('bepic.mk')

radii = bodvrd('MERCURY','RADII',3)
daterange=['2021 JAN 30 12:00:00.000', '2021 JAN 31 12:00:00.000']

et1 = utc2et(daterange[0])
et2 = utc2et(daterange[1])
print et2utc(et2,'ISOC',5)
times = arange(et1,et2,60)
print et2utc(times[-1],'ISOC',5)

distances = []
for t in times:
    print et2utc(t,'ISOC',5)
    try:
        pos = spkpos('mercury',t,'j2000','none','mpo')
    except SpiceException:
        print 'caught error'
        sys.exit(1)
    distances.append(vnorm(pos[0]))
    
plot(times-et1,array(distances)-radii[1][0])
plot(times-et1,array(distances)-radii[1][0],'*')
show()
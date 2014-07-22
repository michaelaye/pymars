from spice import *

furnsh('mars.mk')

utc = '2006 JAN 30 12:00:00.000'

et = utc2et(utc)

print et

print subpnt('Near point:ellipsoid','Mars',et,'IAU_MARS','LT+S','MGS')
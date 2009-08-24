'''
Created on Aug 16, 2009

@author: aye
'''
try:
    from osgeo import gdal
    from osgeo.gdalconst import *
    gdal.TermProgress = gdal.TermProgress_nocb
except ImportError:
    import gdal
    from gdalconst import *

try:
    import numpy as Numeric
    Numeric.arrayrange = Numeric.arange
except ImportError:
    import Numeric

try:
    from osgeo import gdal_array as gdalnumeric
except ImportError:
    import gdalnumeric

import sys,os
import matplotlib
print "using matplotlib version ", matplotlib.__version__
#matplotlib.use("WXAgg") # do this before pylab so you don'tget the default back end.
import pylab

os.chdir('/processed_data/PSP_009978_2265')

cube = gdal.Open('PSP_009978_2265_BG.cal.norm.map.equ.mos.cub', GA_ReadOnly )

xPos = 3835
yPos = 22756

size = int(sys.argv[1])

xOff = xPos - size/2
yOff = yPos - size/2

array = cube.ReadAsArray(xOff, yOff, size, size)


pylab.imshow(array, interpolation = None) 
pylab.colorbar()
pylab.grid(True)
pylab.show()

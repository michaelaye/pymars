#!/usr/bin/python

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
#matplotlib.use("WXAgg") # do this before pylab so you don't get the default back end.
import pylab as plt
import tkFileDialog as fd

try:
    fname = fd.askopenfilename(initialdir='/processed_data/maye')
except:
    fname = fd.askopenfilename()
    
cube = gdal.Open(fname, GA_ReadOnly )

try:
    size = int(sys.argv[1])
except:
    size = 300

xOff = size/2
yOff = size/2

array = cube.ReadAsArray(xOff, yOff, size, size)

plt.imshow(array, interpolation = None) 
plt.colorbar()
plt.grid(True)
plt.show()

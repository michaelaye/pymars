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
import pylab
import tkFileDialog as fd

fname = fd.askopenfilename(initialdir='/processed_data/maye')

cube = gdal.Open(fname, GA_ReadOnly )

array = cube.ReadAsArray()


pylab.imshow(array, interpolation = None) 
pylab.colorbar()
pylab.grid(True)
pylab.show()

'''
Created on Aug 25, 2009

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
#matplotlib.use("WXAgg") # do this before pylab so you don't get the default back end.
import pylab as plt
import tkFileDialog as fd
print 'should have imported everything'

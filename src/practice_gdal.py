'''
Created on Aug 16, 2009

@author: aye
'''
import site

site.addsitedir('/Library/Frameworks/GDAL.framework/Versions/1.6/Resources')

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
import matplotlib.pylab as pylab
import wx

app = wx.App(redirect=False)
dlg = wx.FileDialog(None, 
                    message="Choose a file to open",
                    defaultDir = '/Users/aye/Desktop/cut_jpeg2000/')

retCode = dlg.ShowModal()
if retCode == wx.ID_OK:
    paths = dlg.GetPaths()
    fName = paths[0]
elif retCode == wx.ID_CANCEL: 
    print 'canceled file dialog. exiting'
    sys.exit(-1)
else: 
    print 'unknown error. exiting'
    sys.exit(-1)

cube = gdal.Open(str(fName), GA_ReadOnly )
print "have gdal.Open done"
size = 400

xSize = cube.RasterXSize
ySize = cube.RasterYSize

xOff = xSize/2 - size/2 -1
yOff = ySize/2 - size/2 -1

array = cube.ReadAsArray(xOff, yOff, size, size)


pylab.imshow(array, interpolation = None) 
pylab.colorbar()
pylab.grid(True)
pylab.show()

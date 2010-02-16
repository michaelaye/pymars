#!/usr/bin/python

from gdal_imports import *
import numpy as np
import sys
#from scipy import optimize
#from numpy import *

if sys.platform == 'darwin':
    base = '/Users/aye/Data/hirise/'
else:
    base = '/processed_data/'

fname = base + 'PSP_003092_0985/PSP_003092_0985_RED.cal.norm.map.equ.mos.cub'

cube = gdal.Open(fname, GA_ReadOnly)

print cube.GetDescription()


xOff = 6849
xEnd = 7826
yOff = 18426
yEnd = 18957

xSize = xEnd - xOff
ySize = yEnd - yOff

print "reading {0} at {1},{2} offset".format(fname, xOff, yOff)
arr_big = cube.ReadAsArray(xOff, yOff, xSize, ySize)

print "minimum of array: ", arr_big.min()
arr_big[np.where(arr_big < 0.0)] = np.nan
print "minimum of array after NaN determination: ", arr_big.min()

arr = arr_big[:200, :200]


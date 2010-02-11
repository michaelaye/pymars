#!/usr/bin/python

from gdal_imports import *
import numpy as np

#from scipy import optimize
#from numpy import *


filename1 = '/processed_data/PSP_002622_0945/PSP_002622_0945_RED.cal.norm.map.equ.mos.cub'
size = 400
subframe_coord1 = [14040, 17690, size]
 
filename2 = '/processed_data/PSP_002675_0945/PSP_002675_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord2 = [25167, 29020, size]
 
filename3 = '/processed_data/PSP_002820_0945/PSP_002820_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord3 = [27449, 33025, size]
 
filename4 = '/processed_data/PSP_003176_0945/PSP_003176_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord4 = [9350, 9520, size]

filename5 = '/processed_data/PSP_003308_0945/PSP_003308_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord5 = [11650, 11690, size]

filename6 = '/processed_data/PSP_003309_0945/PSP_003309_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord6 = [14090, 9770, size]

filename7 = '/processed_data/PSP_003453_0945/PSP_003453_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord7 = [12637, 13206, size]

filename8 = '/processed_data/PSP_003466_0945/PSP_003466_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord8 = [10660, 11800, size]

filename9 = '/processed_data/PSP_003677_0945/PSP_003677_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord9 = [14470, 17279, size]

filename10 = '/processed_data/PSP_003730_0945/PSP_003730_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord10 = [11440, 11223, size]
 
filename11 = '/processed_data/PSP_003756_0945/PSP_003756_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord11 = [8814, 9178, size]

filename12 = '/processed_data/PSP_003822_0945/PSP_003822_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord12 = [11755, 13778, size]

filename13 = '/processed_data/PSP_004033_0945/PSP_004033_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord13 = [14643, 17861, size]

filename14 = '/processed_data/PSP_004178_0945/PSP_004178_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord14 = [9540, 10363, size]

filename15 = '/processed_data/PSP_004666_0945/PSP_004666_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord15 = [ 11059, 13377, size]

filename16 = '/processed_data/PSP_004891_0945/PSP_004891_0945_RED.cal.norm.map.equ.mos.cub'
subframe_coord16 = [ 14874, 11710, size]

filenames = [filename1, filename2, filename3, filename4, filename5, filename6,
             filename7, filename8, filename9, filename10, filename11,
             filename12, filename13, filename14, filename15, filename16]
          
subframes = [subframe_coord1, subframe_coord2, subframe_coord3,
             subframe_coord4, subframe_coord5, subframe_coord6,
            subframe_coord7, subframe_coord8, subframe_coord9,
            subframe_coord10, subframe_coord11, subframe_coord12,
            subframe_coord13, subframe_coord14, subframe_coord15,
            subframe_coord16]

import time
t1 = time.time()

for fname, coords in zip(filenames, subframes):
    print fname
    x = coords[2]
    y = x
    x0 = coords[0]   
    y0 = coords[1]
    print x0, x0 + x, y0, y0 + y   
    cube = gdal.Open(fname, GA_ReadOnly)
    image = cube.ReadAsArray(x0, y0, x, y)
    print image.mean()

t2 = time.time()
print 'test with python: ', t2 - t1

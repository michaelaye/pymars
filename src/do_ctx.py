#!/usr/bin/env python
# encoding: utf-8
"""
do_ctx.py

Created by Klaus-Michael Aye on 2010-11-03.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

from __future__ import division
from osgeo import gdal
from matplotlib.pylab import *
import roi
import hirise_tools as ht
import glob
import os

myroi = roi.ROI_Data('ctx_inca_city.csv')

mydict = myroi.dict

keys = mydict.keys()

def get_ctx_fname(obsid):
    """create full path for ctx file from obsid and ccd.
    
    ccd in this case is the mode of ctx operation. i call it
    ccd here because it is at the same place in the file name
    """
    if obsid.startswith('P'):
        phase = 'PSP'
    else:
        phase = 'ESP'
    ccd = mydict[obsid]['CCDColour']
    dname = ht.DEST_BASE + phase + obsid[3:]
    searchpath = dname + os.sep + '*' + ht.mosaic_extensions
    fname = glob.glob(searchpath)[0]
    return fname
 
gray()
   
for key in keys:
    fPath = get_ctx_fname(key)
    f = gdal.Open(fPath)
    x = int(mydict[key]['Map_Sample_Offset'])
    y = int(mydict[key]['Map_Line_Offset'])
    data = f.ReadAsArray(x+500,y+500,1200,1000)
    print('plotting {0}'.format(key))
    ht.save_plot(data,key,key)
    

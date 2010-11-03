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
import numpy as np
import roi
import hirise_tools as ht
import glob
import os
import csv
import sys

myroi = roi.ROI_Data('ctx_inca_city.csv')

mydict = myroi.dict

keys = mydict.keys()
keys.sort()

dictreader = csv.DictReader(open(ht.DEST_BASE + 'ctx_inca_city_metadata.csv'))

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
   
for row in dictreader:
    obsid = row[' PRODUCT_ID'][:16].strip()
    fPath = get_ctx_fname(obsid)
    f = gdal.Open(fPath)
    x = int(mydict[obsid]['Map_Sample_Offset'])
    y = int(mydict[obsid]['Map_Line_Offset'])
    if x < 0 or y < 0: 
        print('{0} has negative pixel location'.format(obsid))
        continue
    data = f.ReadAsArray(x+500,y,1000,500)
    angle = float(row[' INCIDENCE_ANGLE'])
    if angle > 90.0: 
        print("cannot correct {0} for angle > 90.".format(obsid))
        continue
    data = data/np.cos(deg2rad(angle))
    print('plotting {0}'.format(obsid))
    ht.save_plot(data,obsid,obsid)
    

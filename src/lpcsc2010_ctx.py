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
from matplotlib import colors
import numpy as np
import roi
import hirise_tools as ht
import glob
import os
import csv
import sys
from scipy import ndimage as nd

def get_areas(data, labels, n):
    slices = nd.find_objects(labels)
    areas = []
    for i in range(n):
        area = data[slices[i]].sum()*36 #36 is for CTX's 6 m/pix resolution
        areas.append(area)
    return areas

myroi = roi.ROI_Data('ctx_ic_2.csv')

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
    try:
        fname = glob.glob(searchpath)[0]
    except IndexError, e:
        print searchpath
        raise e    
    return fname
 
gray()
l_s = []
counts=[] 
summed_areas=[]
dx = 300
dy = 300
shiftx = 0
shifty = 0
season = 'P'
for row in dictreader:
    obsid = row[' PRODUCT_ID'][:16].strip()
    angle = float(row[' INCIDENCE_ANGLE'])
    if angle > 90.0: 
        print("cannot correct {0} for angle > 90.".format(obsid))
        continue
    x = int(mydict[obsid]['Map_Sample_Offset'])
    y = int(mydict[obsid]['Map_Line_Offset'])
    if x < 0 or y < 0: 
        print('{0} has negative pixel location'.format(obsid))
        continue
    fPath = get_ctx_fname(obsid)
    if not os.path.basename(fPath).startswith(season): continue
    current_l_s = float(row[' SOLAR_LONGITUDE'])
    # if current_l_s > 260: break
    # if current_l_s < 180: continue
    print("processing {0}".format(obsid))
    f = gdal.Open(fPath)
    if obsid.startswith('P07_003928'):
        data = f.ReadAsArray(x+10+shiftx-dx//2,y-41+shifty-dy//2,dx,dy) # correct shift for this one
    else:
        data = f.ReadAsArray(x+shiftx-dx//2,y+shifty-dy//2,dx,dy)

    data = data/np.cos(deg2rad(angle))
#     # data = nd.median_filter(data,size=2)
#     n, bins = histogram(data,40)
#     diff = np.diff(n)
#     thres = bins[diff.argmax()]
#     print thres
#     t = data<thres
#     # for iters in arange(1,30,3):
#     #     for elem in arange(iters):
#     t = nd.binary_closing(t,iterations=1)
#     t = nd.binary_opening(t,iterations=2)
#     labeled, no = nd.label(t)
#     counts.append(no)
#     l_s.append(current_l_s)
#     summed_areas.append(sum(get_areas(data,labeled, no)))
#     # imshow(data)
#     # break
# #     imshow(labeled, interpolation='nearest')
#     title('{0} features found'.format(no))
    ht.save_plot(data,
                obsid + ', L_s: {0}, incidence: {1}'.format(current_l_s,angle),
                'inca_ctx_' + obsid)

# plot(l_s, summed_areas)
# show()
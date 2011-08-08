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
from scipy.stats import scoreatpercentile

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
 
# color palette
gray()

l_s = []
counts=[] 
summed_areas=[]
dx = 50
dy = 50
season = 'B'
picked = ['B05_011702',
          'B06_011913',
          'B07_012480',
          'B08_012678',
          'B08_012757',
          'B08_012889']
frameholder = []
my_l_s = []
for row in dictreader:
    shiftx = 3
    shifty = -5
    obsid = row[' PRODUCT_ID'][:16].strip()
    #!!!!
    if not obsid[:10] in picked: 
        continue
    #!!!!
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
        # correct shift for this one
        shiftx = shiftx + 10
        shifty = shifty - 41
        # data = f.ReadAsArray(x+10+shiftx-dx//2,y-41+shifty-dy//2,dx,dy)
    elif obsid[:10] in ['B05_011702','B06_011913']:
        shiftx = shiftx - 8
        shifty = shifty + 4
    data = f.ReadAsArray(x+shiftx-dx//2,y+shifty-dy//2,dx,dy)

    data2 = data/np.cos(deg2rad(angle))
    # fp = ones((3,3))
    # fp = [[0,1,0],[1,1,1],[0,1,0]]
    # data = nd.grey_closing(data,footprint=fp)
    # data = nd.spline_filter(data)
    data2 = nd.gaussian_filter(data2,0.5)
    # ht.save_plot(data2,
    #                 obsid + ', L_s: {0}, incidence: {1}'.format(current_l_s,angle),
    #                 'inca_ctx_' + obsid)
    # if obsid[:10] in ['B05_011702','B06_011913']:
    data2 = (data2 - data2.min())*(0.43-0.27)/(data2.max()-data2.min())+0.27
    # data2 = (data2-scoreatpercentile(data2.flatten(),5)) * \
    #             255/scoreatpercentile(data2.flatten(),95)
    print data2.min(),data2.max()
    frameholder.append(data2)
    my_l_s.append(int(current_l_s))
    # ht.save_hist(data2,'inca_ctx_' + obsid + '_hist.png')

end = hstack(frameholder)
bone() # color palette
imshow(end)
xticks(range(25,310,50),tuple(my_l_s),fontsize=12)
yticks([])
tick_params(direction='out',top='off')
title('Reappearing halo in Inca City, L$_s$: {0}-{1}$^\circ$\
        '.format(my_l_s[0],my_l_s[-1]),fontsize=12)
savefig('inca_ctx_end.pdf',dpi=100,bbox_inches='tight')


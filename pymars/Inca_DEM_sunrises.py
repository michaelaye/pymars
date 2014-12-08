#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function
from pymars import kmaspice
import pandas as pd
from pymars import mars
from pymars import pdstools
import subprocess
import os
import sys
import glob
from multiprocessing import Pool
import subprocess
from os.path import join as pjoin


def execute_sub(arg):
    print(arg)
    subprocess.call(arg, shell=True)
    

labels = pdstools.PDSLabel('/Users/maye/data/hirise/inca/ESP_022607_0985_RED.LBL')
dem = mars.ImgData('/Users/maye/data/hirise/inca_city_dem/'
                   'latest_download/ESP_022699_0985_RED_A_01_ORTHO.JP2')

surf = kmaspice.MarsSpicer(labels.time)
surf.set_spoint_by(lat=dem.center.lat, lon=dem.center.lon)

surf.advance_time_by(-3600*24*250)
surf.utc = '2010-10-06T06:44:21.402000'

times = []
dsolar = []
azis = []
Ls = []
localtime = []
n=0
print("Spicing...")
# while n < 5000:
#     if surf.illum_angles.dsolar < 90:
#         times.append(surf.time)
#         dsolar.append(surf.illum_angles.dsolar)
#         p2lon, p2lat = surf.point_towards_sun(pixel_res=1)
#         p2 = mars.Point(lat=p2lat, lon=p2lon)
#         p2.lonlat_to_pixel(dem.center.geotrans, dem.center.proj)
#         azis.append(dem.center.calculate_azimuth(p2,zero='top'))
#         Ls.append(surf.l_s)
#         localtime.append('{0}_{1}'.format(*surf.local_soltime[:2]))
#         n+=1
#     surf.advance_time_by(600)
# 
# # convert collected data to a pandas DataFrame
# df = pd.DataFrame({'times':times,'inc':dsolar,'azimuth':azis, 'Ls':Ls, 'loctime':localtime})
# # index the dataframe by the times
# df.set_index('times', drop=True,inplace=True)
df = pd.read_hdf('notebooks/inca_metadata.h5','df')
# pick Ls range for producing images
ls_range = 161
date = sys.argv[1]
subdf = df[date]

root = '/Users/maye/data/hirise/inca_city_dem/latest_download'
if not os.path.exists(root):
    os.makedirs(root)

inpath = pjoin(root,'DTEPC_022699_0985_022607_0985_A01.IMG')
cmd_root = ['gdaldem','hillshade']
cmds = []
for key, value in subdf.T.iteritems():
    outdir = pjoin(root,str(ls_range))
    outpath = pjoin(outdir,'Ls_{0:03.0f}_Inc_{1:05.2f}_LT_{2}_large.png'.\
                                format(value['Ls'], 90 - value['inc'], value['loctime']))
    cmd_end = [inpath, outpath, '-of png', '-az {0}'.format(value['azimuth']),
                                '-alt {0}'.format(90 - value['inc'])]
    cmds.append([' '.join(cmd_root+cmd_end)])

print("GDALing...")  
p = Pool(4)
p.map(execute_sub, cmds)

cmds = []
i = 0
for key, value in subdf.T.iteritems():
    inbasename = 'Ls_{0:03.0f}_Inc_{1:05.2f}_LT_{2}_'.format(value['Ls'], 
                                                           90 - value['inc'],
                                                           value['loctime'],)
    inpath = pjoin(root, str(ls_range), inbasename+'large.png')
    outpath =pjoin(root, str(ls_range), '{2}_{0}_{1}.png'.format(str(i).zfill(3),
                                                             inbasename[:-1],
                                                             '_'.join(str(date).split('-'))))
    cmd = ['convert', inpath, '-resize 1920', outpath]
    cmds.append(' '.join(cmd))
    i += 1

print("Converting...")    
p = Pool(4)
p.map(execute_sub, cmds)
print("Done.")




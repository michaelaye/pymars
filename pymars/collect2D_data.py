#!/usr/bin/env python
# encoding: utf-8
"""
plot_polar.py

Created by K.-Michael Aye on 2011-09-11.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
from __future__ import division
import matplotlib.pyplot as plt
import pickle
from LabelPlotter import read_atlas_report
import time
import numpy as np
import sys

class DataCollector(object):
    """class to collect data at 2D indices. 
    
    The idea of this class is to enable the following:
    dc = DataCollector(rows,columns)
    for x,y,value in zip(xdata,ydata,data):
        dc.add(x,y,value)
    img = dc.get_mean_image()
    
    So basically, collect the data at 2D coordinates and return
    an image array with the requested way of combining the data"""
    def __init__(self, rows,columns):
        super(DataCollector, self).__init__()
        self.rows = rows
        self.columns = columns
        self.sum = np.zeros((rows,columns))
        self.counter = np.zeros((rows,columns),dtype=np.int)
    def add(self, x,y,value):
        try:
            self.sum[x][y]+=value
            self.counter[x][y]+=1
        except IndexError:
            print x,y
            sys.exit(-1)
    def get_mean_image(self):
        img = self.sum[:]
        for row in np.arange(self.rows):
            for column in np.arange(self.columns):
                if self.counter[row][column] != 0:
                    img[row][column]=self.sum[row][column]/self.counter[row][column]
        return img
        
                
def main():
    datadir = '/Users/maye/Data/ctx/'
    atlas_data = read_atlas_report(datadir + 'atlas_report.csv')
    with open(datadir + 'std_data.pkl') as f:
        std_data = pickle.load(f)
    stds = []
    l_s = []
    longitudes = []
    latitudes = []
    miss_counter=0
    for obsid, std in std_data.iteritems():
        std = float(std)
        if std > 1e10: # some conversion to ISIS fails.
            continue
        try:
            d = atlas_data[obsid]
        except KeyError:
            miss_counter+=1
            continue
        l_s.append(float(d['SOLAR_LONGITUDE']))
        longitudes.append(float(d['CENTER_LONGITUDE']))
        latitudes.append(float(d['CENTER_LATITUDE']))
        stds.append(float(std))
    d = {}
    ls_binning = 20
    for i in range(180//ls_binning,381//ls_binning): # l_s bins, in steps of 20 degrees
        d[i]=DataCollector(5,8)
    maxstd = 0
    minstd = 10
    for lsubs, std, lon,lat in zip(l_s,stds,longitudes,latitudes):
        d[lsubs//ls_binning].add((-lat-80)//2,lon//45,std)
    extent=[0,360,-90,-80]
    for l_s in d.keys():
        print 'doing',l_s
        plt.clf()
        plt.imshow(d[l_s].get_mean_image(),extent=extent,vmin=0.0006,vmax=0.066)
        plt.jet()
        plt.colorbar()
        plt.title(str(l_s*ls_binning)+'-'+str(l_s*ls_binning+ls_binning))
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.savefig(str(l_s*ls_binning)+'.pdf')
    # plt.show()
    
if __name__ == '__main__':
    main()


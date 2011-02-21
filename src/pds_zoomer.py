#!/usr/bin/env python
'''
Created on Aug 16, 2009

@author: aye
'''

from gdal_imports import *
import matplotlib
matplotlib.use('Tkagg')
from matplotlib.pylab import *
import sys
import pickle
import tkFileDialog as fd
from matplotlib.widgets import RectangleSelector
from hirise_tools import rebin
from LabelPlotter import get_labels

class Zoom:
    dSize = (512, 512)
    def __init__(self, fname):
        # labels = get_labels(fname)
        # self.labels = labels
        # try:
        #     self.offset = float(labels['IMAGE']['OFFSET'])
        #     print self.offset
        #     self.scaling_factor = float(labels['IMAGE']['SCALING_FACTOR'])
        #     print self.scaling_factor
        # except KeyError:
        #     self.offset = float(labels['UNCOMPRESSED_FILE']
        #                         ['IMAGE']['OFFSET'])
        #     print self.offset
        #     self.scaling_factor = float(labels['UNCOMPRESSED_FILE']
        #                                 ['IMAGE']['SCALING_FACTOR'])
        #     print self.scaling_factor
        ds = gdal.Open(fname)
        band = ds.GetRasterBand(1)
        self.data = band.ReadAsArray()
        self.x = self.data.shape[0]
        self.y = self.data.shape[1]
        self.binned = rebin(self.data, self.dSize)
        fig = figure()
        ax = fig.add_subplot(111)
        im = ax.imshow(self.binned)
        LS = RectangleSelector(ax, self.line_select_callback,
                   drawtype='box', useblit=True,
                   minspanx=5, minspany=5, spancoords='pixels')
        self.fig = fig
        self.ax = ax
        self.im = im
        show()
    
        
    def line_select_callback(self, event1, event2):
        'event1 and event2 are the press and release events'
        x1, y1 = event1.xdata, event1.ydata
        x2, y2 = event2.xdata, event2.ydata
        x = array([x1, x2])
        y = array([y1, y2])
        print x.astype(int)
        print y.astype(int)
    #    print "(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2)
    #    print " The button you used were: ", event1.button, event2.button
        allX = self.dSize[0]
        allY = self.dSize[1]
        newX = (x / allX * self.x).astype(int)
        newY = (y / allY * self.y).astype(int)
        print newX, newY
        self.binned = rebin(self.data[newY[0]:newY[1], newX[0]:newX[1]],
                            self.dSize) * self.scaling_factor + self.offset
        with open('binned.pkl', 'w') as f:
            pickle.dump(self.binned, f)
        fig = figure()
        ax = fig.add_subplot(111)
        im = ax.imshow(self.binned)
        colorbar(im)
        fig.show()
        


def main():
    
    opts = [('mosaic cubes', '.mos.cub'),
            ('all cubes', '.cub'),
            ('PDS no label', '.img'),
            ('PDS w/ label', '.lbl'),
            ('All files', '.*')]

    opts.insert(0, opts.pop()) # put last element to be first
    
    if sys.platform == 'darwin':
        options = {}
        options['filetypes'] = opts
        fname = fd.askopenfilename(initialdir='/Users/aye/Data/mola', **options)
#        fname = '/Users/aye/Data/hirise/PSP_003092_0985/PSP_003092_0985_RED.cal.norm.map.equ.mos.cub'
    else:
        options = {}
        options['filetypes'] = opts
        fname = fd.askopenfilename(initialdir='/processed_data', **options)
    
    zoom = Zoom(fname)
    
if __name__ == '__main__':
    main()

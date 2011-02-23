#!/usr/bin/env python
# encoding: utf-8
"""
display_mola.py

Created by K.-Michael Aye on 2010-07-17.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import sys
from osgeo import gdal
from matplotlib.pyplot import figure, show
from ctx_and_mola import get_coords_from_pixels
from ctx_and_mola import get_pixels_from_coords
from mpl_toolkits.axes_grid.anchored_artists import AnchoredSizeBar
import numpy as np

class MOLA():
    """docstring for MOLA"""
    def __init__(self, 
                 fname='/Users/aye/Data/mola/megr_s_512_1.cub',
                 testing = False,
                 ):
        self.fname = fname
        self.dataset = gdal.Open(self.fname)
        self.ds = self.dataset
        if testing is True:
            self.do_all()
            
    def get_sample_data(self,width=500):
        """docstring for get_sample_data"""
        ds = self.dataset
        xSize = ds.RasterXSize
        ySize = ds.RasterYSize
        self.data = ds.ReadAsArray(xSize/2 - width/2,
                              ySize/2 - width/2,
                              width, width)
        return self.data
 
    def from_corners(self,ulSample,ulLine,lrSample,lrLine):
        """docstring for get_data_from_sample_line"""
        self.corners = [ulSample,ulLine,lrSample,lrLine]
        self.ulSL= [ulSample,ulLine]
        self.lrSL = [lrSample,lrLine]
        ds = self.dataset
        self.data = ds.ReadAsArray(ulSample,ulLine,lrSample-ulSample,lrLine-ulLine)
        return self.data
        
    def get_extent(self):
        self.ulX,self.ulY = get_coords_from_pixels(self.ds,self.ulSL[0],self.ulSL[1])
        self.lrX,self.lrY = get_coords_from_pixels(self.ds,self.lrSL[0],self.lrSL[1])
        self.extent = [self.ulX,self.lrX,self.lrY,self.ulY]
        return self.extent

    def show(self,loc = 3):
        fig = figure()
        ax = fig.add_subplot(111)
        extent = self.get_extent()
        ax.imshow(self.data,extent=extent,origin='image')
        diffx = abs(extent[1]-extent[0])
        diffy = abs(extent[3]-extent[2])
        diff = max(diffx,diffy)
        # get closed magnitude to 10 % of image extent
        scalebarLength = 10**int(round(np.log10(diff/10)))
        d = dict([(10,'10 m'), (100,'100 m'), (1000,'1 km'), (10000,'10 km'),
                    (100000,'100 km'), (1000000,'1000 km')])
        asb = AnchoredSizeBar(ax.transData,
                              scalebarLength,
                              d[scalebarLength],
                              loc=loc)
        ax.add_artist(asb)
        show()

    def do_all(self):
        self.from_corners(0,0,1000,500)
        self.show()
        
def main(argv=None):
    """docstring for main"""
    from enthought.mayavi import mlab
    if argv==None:
        argv=sys.argv
     
    x1 = x2 = y1 = y2 = 0
    fname = ''   
    try:
        fname = argv[1]
        x1,x2,y1,y2 = [int(i) for i in argv[2:]]
    except:
        print 'Usage: {0} fname x1 x2 y1 y2'.format(argv[0])

    print x1,x2,y1,y2
    ds = gdal.Open(fname)
    band = ds.GetRasterBand(1)
    STORED_VALUE = band.ReadAsArray(x1,y1,x2-x1,y2-y1)
    ds = 0
    
    # PDS label infos:
    SCALING_FACTOR               = 0.25
    OFFSET                       = -8000
    topo = (STORED_VALUE * SCALING_FACTOR) + OFFSET
    mlab.surf(topo,warp_scale=1/115.,vmin=1700)
    mlab.colorbar(orientation='vertical',title='Height [m]',label_fmt='%4.0f')
    mlab.show()
    
    
if __name__ == "__main__":
	sys.exit(main())

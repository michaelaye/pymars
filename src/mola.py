#!/usr/bin/env python
# encoding: utf-8
"""
display_mola.py

Created by K.-Michael Aye on 2010-07-17.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import sys
from osgeo import gdal
from matplotlib.pyplot import imshow, figure, show

def get_dataset():
    """docstring for get_dataset"""
    ds = gdal.Open('/Users/aye/Data/mola/megr_s_512_1.cub')
    return ds
    
def get_sample_data(width=500):
    """docstring for get_sample_data"""
    ds = get_dataset()
    xSize = ds.RasterXSize
    ySize = ds.RasterYSize
    return ds.ReadAsArray(xSize/2 - width/2,
                          ySize/2 - width/2,
                          width, width)
                          
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

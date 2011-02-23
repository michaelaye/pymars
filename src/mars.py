#!/usr/bin/env python
# encoding: utf-8
"""
mars.py $Id: mars.py,v c749f7f7a441 2011/02/23 19:43:18 aye $

Some tools to work with Mars data.
Abbreviations:
ul = Upper Left
lr = LowerRight

Copyright (c) 2011 Klaus-Michael Aye. All rights reserved.
"""

from osgeo import gdal
from matplotlib.pyplot import figure, show
import matplotlib.pyplot as plt
import sys
import matplotlib.cm as cm
from mpl_toolkits.axes_grid.anchored_artists import AnchoredSizeBar
import numpy as np

"""
"""

class Point():
    """Little Point class to manage pixel and map points.
    
    Requires: gdal to enable sample/line<-> map coords tra'fo's
    """
    def __init__(self, sample=None, line=None, 
                       x=None, y=None,
                       lat=None,lon=None):
        self.x = x
        self.y = y
        self.sample = sample
        self.line = line
        self.isPixel = isPixel
        self.isMap = isMap
        self.isLatLon = isLatLon
        
    def convert_to_map(self, dataset):
        """provide point in map projection coordinates.
    
        Input: gdal Dataset
        Return: list [x,y] coordinates in the projection of the dataset
        >>> from osgeo import gdal
        >>> ds = gdal.Open('/Users/aye/Data/mola/megt_s_128_1.tif')
    
        Asking for the (0,1) pixel as measured in (sample,line), one gets the 
        coordinate of the current projection measured in meters from the origin of
        that projection.
        Have to test (0,1) and not (0,0) because a wrong order of arguments would 
        not be detected by the test because of the symmetry.
        >>> convert_to_map(ds,0,1)
        [-2355200.0, 2354740.0]
        """
        if not (self.x and self.y): 
            datasetTransform = dataset.GetGeoTransform()
            self.x, self.y = gdal.ApplyGeoTransform(datasetTransform, sample, line)
        return (self.x,self.y)

    def convert_to_pixels(self, dataset):
        """provide pixel coords from x,y coords.
    
        Input: gdal Dataset
        Return: list [line,sample] of the dataset for given coordinate
        >>> from osgeo import gdal
        >>> ds = gdal.Open('/Users/aye/Data/mola/megt_s_128_1.tif')
    
        Asking the pixels for the center coordinate of a south pole centered
        quadratic dataset should return half the samples and lines, because (0,0)
        in pixels is the upper left of the array. This file as 10240 lines and 
        samples, so we expect 5120 to get back as pixel entry for the center of 
        the projection: (testing slightly off-center to avoid errors hidden by 
        symmetric parameters)
        >>> convert_to_pixel(ds,0,1)
        [5120.0, 5119.997826086957]
        """
        if not(self.sample and self.line):
            datasetTransform = dataset.GetGeoTransform()
            success, tInverse = gdal.InvGeoTransform(datasetTransform)
            self.sample, self.line = gdal.ApplyGeoTransform(tInverse, x, y)
        return (self.sample, self.line)

class Window():
    """class to manage a window made of corner Points (objects of Point())
    
    when using width, only quadratic windows supported currently
    """
    def __init__(self, ulPoint=None, width=None, lrPoint=None, 
                        centerPoint=None):
        self.ul = ulPoint
        self.width = width
        self.lr= lrPoint
        self.center = centerPoint
        if not (ulPoint and lrPoint):
            if centerPoint and width: self.get_corners_from_center()
            elif ulPoint and width: self.get_lr_from_width()
            else:
                print("Either upper left and lower right or upper left/"
                     " centerPoint with width needs to be provided.") 
                sys.exit(1)
                
    def get_corners_from_center():
        """docstring for get_corners_from_center
    
        create symmetric window around given sample/line point and return
        to Point objects for each corner point of the window
        >>> get_corners_from_center(500,400,100)
        (450, 350, 550, 450)
        """
        ulSample = self.center.sample - self.width//2
        ulLine = self.center.line - width//2
        self.ul = Point(sample=ulSample,line=ulLine)
        lrSample = self.center.sample + width//2
        lrLine = self.center.line + width//2
        self.lr = Point(sample=lrSample,line=lrLine)
        return (self.ul, self.lr)

class Base():
    """docstring for Base"""
    def __init__(self):
        gdal.UseExceptions()

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
        """"""
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
            
class MOLA(Base):
    """docstring for MOLA"""
    def __init__(self, 
                 fname='/Users/aye/Data/mola/megr_s_512_1.cub',
                 testing = False,
                 ):
        super(MOLA, self).__init__()
        self.fname = fname
        self.dataset = gdal.Open(self.fname)
        self.ds = self.dataset
        if testing is True:
            self.do_all()
            
    def do_all(self):
        self.from_corners(0,0,1000,500)
        self.show()

class CTX(Base):
    """docstring for CTX"""
    def __init__(self,
                 fname='Users/aye/Data/ctx/inca_city/ESP_011412/'\
                 'B05_011412_0985_XI_81S063W.cal.des.cub.map.cub.png'):
        super(CTX, self).__init__()
                
def combine_ctx_and_mola(ctxFilename, ctxSample, ctxLine, ctxWidth):
    """combine CTX and MOLA data.
    
    MOLA and CTX data will be combined with these tools.
    User shall provide line,sample center coordinate of CTX file ROI to 
    define distance in meters from southpole.
    """
        
    ctx = CTX(ctxFilename)
    mola = MOLA()
    ctxULsample,ctxULline,ctxLRsample,ctxLRline = \
        get_corners_from_center(ctxSample,ctxLine,ctxWidth) 
    ulX,ulY = get_coords_from_pixels(ctxDS, ctxULsample, ctxULline)
    lrX,lrY = get_coords_from_pixels(ctxDS, ctxLRsample, ctxLRline)
                                     
    molaULsample,molaULline = get_pixels_from_coords(molaDS,ulX,ulY)
    molaLRsample,molaLRline = get_pixels_from_coords(molaDS,lrX,lrY)
    print ctxULsample, ctxULline, ctxLRsample, ctxLRline
    print molaULsample, molaULline,molaLRsample, molaLRline
    print ulX,ulY,lrX,lrY
    ctxData = ctxDS.ReadAsArray(ctxULsample,ctxULline,ctxWidth,ctxWidth)
    molaData = molaDS.ReadAsArray(int(molaULsample)+1,int(molaULline),
                                  int(molaLRsample - molaULsample),
                                  int(molaLRline - molaULline))

    molaData = molaData - molaData.mean()                    

    # x = np.arange(ulX,lrX)
    # y = np.arange(lrY,ulY)
    # X, Y = np.meshgrid(x,y)
    # plotting
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111)
    plt.gray()
    ax.imshow(ctxData, extent=(min(ulX,lrX),max(ulX,lrX),min(ulY,lrY),
                                     max(ulY,lrY)))
    CS = ax.contour(molaData, 20, cmap = cm.jet,
                     extent=(min(ulX,lrX),
                             max(ulX,lrX),
                             min(ulY,lrY),
                             max(ulY,lrY)),
                     origin='image' )
    plt.clabel(CS,fontsize=9, inline=1)
    plt.show()

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

#!/usr/bin/env python
# encoding: utf-8
"""
mars.py $Id: mars.py,v 8793b6c14e0c 2011/02/24 18:34:18 aye $

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

gdal.UseExceptions()

class Point():
    """Little Point class to manage pixel and map points.
    
    Requires: gdal to enable sample/line<-> map coords tra'fo's
    >>> p = Point(0,1)
    
    Need a dataset to try, so I get a MOLA dataset:
    >>> mola = MOLA()
    >>> '%4.2f, %4.2f' % p.convert_to_map(mola.dataset)
    '-707109.70, 706994.61'
    >>> p = Point(x=0,y=1)
    >>> '%4.2f, %4.2f' % p.convert_to_pixels(mola.dataset)
    '6144.00, 6143.99'
    >>> p2 = Point(x=3,y=3)
    >>> newP = p + p2
    >>> print newP.x, newP.y
    3 4
    """
    def __init__(self, sample=None, line=None,
                       x=None, y=None,
                       lat=None,lon=None):
        self.sample = sample
        self.line = line
        self.x = x
        self.y = y
        self.lat = lat
        self.lon = lon
    
    def __add__(self, other):
        newPoint = Point(0,0)
        if all([coord != None for coord in [self.sample,other.sample]]):
            newPoint.sample =self.sample + other.sample
            newPoint.line = self.line + other.line
        if all([coord != None for coord in [self.x,other.x]]):
            newPoint.x = self.x + other.x
            newPoint.y = self.y + other.y
        if all([coord != None for coord in [self.lat,other.lat]]):
            newPoint.lat = self.lat + other.lat
            newPoint.lon = self.lon + other.lon
        return newPoint
        
    def convert_to_map(self, dataset):
        """provide point in map projection coordinates.
        
        Input: gdal Dataset
        Return: tuple (x,y) coordinates in the projection of the dataset
        >>> p = Point(0,0)
        >>> mola = MOLA()
        >>> '%6.2f, '*2 % p.convert_to_map(mola.dataset)
        '-707109.70, 707109.70, '
        """
        if not (self.x and self.y):
            datasetTransform = dataset.GetGeoTransform()
            self.x, self.y = gdal.ApplyGeoTransform(datasetTransform,
                                                    self.sample, self.line)
        return (self.x,self.y)
    
    def convert_to_pixels(self, dataset):
        """provide pixel coords from x,y coords.
        
        Input: gdal Dataset
        Return: list [line,sample] of the dataset for given coordinate
        >>> p = Point(x=5e5, y=6e5)
        >>> mola = MOLA()
        >>> '%6.2f ,'*2 % p.convert_to_pixels(mola.dataset)
        '10488.45 ,930.66 ,'
        """
        if not(self.sample and self.line):
            datasetTransform = dataset.GetGeoTransform()
            success, tInverse = gdal.InvGeoTransform(datasetTransform)
            self.sample, self.line = gdal.ApplyGeoTransform(tInverse,
                                                            self.x,
                                                            self.y)
        return (self.sample, self.line)

class Window():
    """class to manage a window made of corner Points (objects of Point())
    
    when using width, only quadratic windows supported currently
    >>> p1 = Point(0, 1)
    >>> p2 = Point(10,20)
    """
    def __init__(self, ulPoint=None, lrPoint=None,
                       centerPoint=None, width=None):
        if  not any([lrPoint,centerPoint,width]):
            self.usage()
        else:
            self.ul = ulPoint
            self.lr = lrPoint
            self.center = centerPoint
        self.width = width
        if not (ulPoint and lrPoint):
            if centerPoint and width: self.get_corners_from_center()
            elif ulPoint and width: self.get_lr_from_width()
            else:
                print("Either upper left and lower right or upper left/"
                     " centerPoint with width needs to be provided.")
                return
    
    def get_lr_from_width(self):
        lrSample = self.ul.sample+self.width
        lrLine = self.ul.line+self.width
        self.lr = Point(lrSample,lrLine)
        return self.lr
    
    def usage(self):
        print """Usage: win = Window(pointObject1, pointObject2)
        or
        win = Window(pointObject1, width_in_Pixel)
        or
        win = Window(centerPoint, width_in_Pixel)"""
        return
    
    def get_corners_from_center(self):
        """docstring for get_corners_from_center
        
        create symmetric window around given sample/line point and return
        to Point objects for each corner point of the window
        >>> win = Window(centerPoint=Point(100,100),width=50)
        >>> win.ul.sample, win.ul.line, win.lr.sample, win.lr.line
        (75, 75, 125, 125)
        """
        ulSample = self.center.sample - self.width//2
        ulLine = self.center.line - self.width//2
        self.ul = Point(ulSample,ulLine)
        lrSample = self.center.sample + self.width//2
        lrLine = self.center.line + self.width//2
        self.lr = Point(lrSample,lrLine)
        return (self.ul, self.lr)

    def get_gdal_window(self):
        """provide window coordinates in gdal format.
        
        thats [ulSample, ulLine, samplewidth,linewidth]
        >>> win = Window(Point(10,150),Point(100,200))
        >>> win.get_gdal_window()
        [10, 150, 90, 50]
        """
        return [self.ul.sample,self.ul.line,
                self.lr.sample-self.ul.sample,
                self.lr.line-self.ul.line]
                
    def get_extent(self, dataset):
        """provide window coordinates in matplotlib extent format
        
        this is needed to get the imshow image plot in the right coordinates
        the strange looking string print out for getting the extent is only 
        done to make up for floating point differences that can happen when 
        this code executes on other machines
        >>> win = Window(Point(10,150),Point(100,200))
        >>> mola = MOLA()
        >>> '%6.2f, '*4 % tuple(win.get_extent(mola.dataset))
        '-705958.80, -695600.75, 684091.80, 689846.28, '
        """
        self.ul.convert_to_map(dataset)
        self.lr.convert_to_map(dataset)
        return [self.ul.x,self.lr.x,
                self.lr.y,self.ul.y]
                
                
class ImgData():
    """docstring for ImgData"""
    def get_sample_data(self,width=500):
        """Get some sample data from the center of the dataset
        
        Input: width of square data array, default 500
        >>> mola= MOLA()
        >>> data = mola.get_sample_data()
        >>> data.shape
        (500, 500)
        >>> data.min()
        3382217.5
        >>> mola.data.max()
        3382383.8
        """
        ds = self.dataset
        xSize = ds.RasterXSize
        ySize = ds.RasterYSize
        self.data = ds.ReadAsArray(xSize/2 - width/2,
                              ySize/2 - width/2,
                              width, width)
        return self.data
    
    def read_window(self, ul_or_win, lrPoint=None):
        """get data for Window object or 2 Point objects
        
        user can either provide one Window object or 2 Point objects as input
        >>> mola = MOLA()
        >>> data = mola.read_window(Point(100,200),Point(300,400))
        >>> data.shape
        (200, 200)
        >>> data.min()
        3380594.5
        >>> data.max()
        3380967.0
        >>> data = mola.read_window(Window(Point(100,200),Point(400,500)))
        >>> data.shape
        (300, 300)
        >>> data.min()
        3380329.8
        """
        if isinstance(ul_or_win,Window):
            self.window = ul_or_win
        else:
            self.window = Window(ul_or_win, lrPoint)
        self.data = self.dataset.ReadAsArray(*self.window.get_gdal_window())
        return self.data
        
    def show(self,loc = 3):
        fig = figure()
        ax = fig.add_subplot(111)
        extent = self.window.get_extent(self.dataset)
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

class MOLA(ImgData):
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
    
    def do_all(self):
        self.read_ul_lr(0,0,1000,500)
        self.show()

class CTX(ImgData):
    """docstring for CTX"""
    def __init__(self,
                 fname='/Users/aye/Data/ctx/inca_city/ESP_011412_0985/'\
                 'B05_011412_0985_XI_81S063W.cal.des.cub.map.cub'):
        self.fname = fname
        self.dataset = gdal.Open(self.fname)
                

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

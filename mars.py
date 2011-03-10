#!/usr/bin/env python
# encoding: utf-8
"""
mars.py $Id: mars.py,v 750818c897ed 2011/03/10 18:08:51 aye $

Some tools to work with Mars data.
Abbreviations:
ul = Upper Left
lr = LowerRight

Copyright (c) 2011 Klaus-Michael Aye. All rights reserved.
"""

from __future__ import division
from osgeo import gdal,osr
from matplotlib.pyplot import figure, show
import matplotlib.pyplot as plt
import sys
import os.path
import matplotlib.cm as cm
from mpl_toolkits.axes_grid.anchored_artists import AnchoredSizeBar
import numpy as np

"""
"""

gdal.UseExceptions()

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class MapNotSetError(Error):
    """Exception raised for errors in the input of transformations.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class Point():
    """Little Point class to manage pixel and map points.
    
    Requires: gdal to enable sample/line<-> map coords tra'fo's
    >>> p = Point(0,1)
    
    Need a dataset to try, so I get a MOLA dataset:
    >>> mola = MOLA()
    >>> '%4.2f, %4.2f' % p.pixel_to_meter(mola.dataset.GetGeoTransform())
    '-707109.70, 706994.61'
    >>> p = Point(x=0,y=1)
    >>> '%4.2f, %4.2f' % p.meter_to_pixel(mola.dataset.GetGeoTransform())
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
        self.centered = False

    def shift_to_center(self, geotransform):
        # if i'd shift, the centerpoint does not show center coordinates
        # so that seems wrong. am i overlooking something?
        # self.x += geotransform[1] / 2.0
        # self.y += geotransform[5] / 2.0
        # self.centered = True
        pass
        
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

    def __call__(self):
        print('Pixel: ({0},{1})'.format(self.sample,self.line))
        print('Map: ({0},{1})'.format(self.x,self.y))
        print('Geo: ({0},{1})'.format(self.lon,self.lat))
        
    def pixel_to_meter(self, geotransform):
        """provide point in map projection coordinates.
        
        Input: gdal Dataset
        Return: tuple (x,y) coordinates in the projection of the dataset
        >>> p = Point(0,0)
        >>> mola = MOLA()
        >>> '%6.2f, '*2 % p.pixel_to_meter(mola.dataset.GetGeoTransform())
        '-707109.70, 707109.70, '
        """
        self.geotransform = geotransform
        self.x, self.y = gdal.ApplyGeoTransform(geotransform,
                                                self.sample, self.line)
        self.shift_to_center(geotransform)
        return (self.x,self.y)
    
    def meter_to_pixel(self, geotransform):
        """provide pixel coords from x,y coords.
        
        Input: gdal Dataset
        Return: list [line,sample] of the dataset for given coordinate
        >>> p = Point(x=5e5, y=6e5)
        >>> mola = MOLA()
        >>> '%6.2f ,'*2 % p.meter_to_pixel(mola.dataset.GetGeoTransform())
        '10488.45 ,930.66 ,'
        """
        if (self.x == None) or (self.y == None):
            raise MapNotSetError((self.x,self.y),
                'Map coordinates not set for transformation.')
        success, tInverse = gdal.InvGeoTransform(geotransform)
        self.sample, self.line = gdal.ApplyGeoTransform(tInverse,
                                                        self.x,
                                                        self.y)
        return (self.sample, self.line)
    
    def pixel_to_lonlat(self, geotransform, projection):
        self.pixel_to_meter(geotransform)
        self.meter_to_lonlat(projection)
        return (self.lon, self.lat)
        
    def lonlat_to_pixel(self, geotransform, projection):
        self.lonlat_to_meter(projection)
        self.meter_to_pixel(geotransform)
        return (self.sample,self.line)
        
    def meter_to_lonlat(self, projection):
        srs = osr.SpatialReference(projection)
        if int(srs.GetProjParm('scale_factor')) == 0:
            srs.SetProjParm('scale_factor',1)
        srsLatLon = srs.CloneGeogCS()
        ct = osr.CoordinateTransformation(srs, srsLatLon)
        self.lon, self.lat, height = ct.TransformPoint(self.x,self.y)
        return (self.lon,self.lat)
        
    def lonlat_to_meter(self, projection):
        srs = osr.SpatialReference(projection)
        if int(srs.GetProjParm('scale_factor')) == 0:
            srs.SetProjParm('scale_factor',1)
        srsLatLon = srs.CloneGeogCS()
        ct = osr.CoordinateTransformation(srsLatLon,srs)
        # height not used so far!
        self.x, self.y, height = ct.TransformPoint(self.lon,self.lat)
        return (self.x,self.y)
        

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
    
    def copy(self):
        win = Window(Point(self.ul.sample,self.ul.line,
                           x = self.ul.x, y = self.ul.y,
                           lon = self.ul.lon, lat = self.ul.lat),
                     Point(self.lr.sample,self.lr.line,
                           x = self.lr.x, y = self.lr.y,
                           lon = self.lr.lon, lat = self.lr.lat))
        return win
        
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
        """provide window pixel coordinates in gdal format.
        
        thats [ulSample, ulLine, samplewidth,linewidth]
        >>> win = Window(Point(10,150),Point(100,200))
        >>> win.get_gdal_window()
        [10, 150, 90, 50]
        """
        return [int(self.ul.sample)-1,int(self.ul.line)-1,
                int(self.lr.sample-self.ul.sample),
                int(self.lr.line-self.ul.line)]
                
    def get_extent(self, dataset, lonlat=False):
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
        if lonlat==False:
            self.ul.pixel_to_meter(dataset.GetGeoTransform())
            self.lr.pixel_to_meter(dataset.GetGeoTransform())
            return [self.ul.x/1000,self.lr.x/1000,self.lr.y/1000,self.ul.y/1000]
        elif lonlat == True:
            self.ul.pixel_to_lonlat(dataset.GetGeoTransform(),
                                    dataset.GetProjection())
            self.lr.pixel_to_lonlat(dataset.GetGeoTransform(),
                                    dataset.GetProjection())
            return [self.ul.lon,self.lr.lon,self.lr.lat,self.ul.lat]                  
                
                
class ImgData():
    """docstring for ImgData"""
    def __init__(self, fname=None):
        self.fname = fname
        self.dataset = gdal.Open(self.fname)
        self.ds = self.dataset
        self.geotransform = self.dataset.GetGeoTransform()
        self.projection = self.dataset.GetProjection()
        
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
        self.get_center_from_dataset()
        self.window = Window(centerPoint=self.center,width=width)
        self.data = ds.ReadAsArray(*self.window.get_gdal_window())
        return self.data
  
    def get_center_from_dataset(self, dataset=None):
        if not dataset:
            dataset = self.dataset
        xSize = dataset.RasterXSize
        ySize = dataset.RasterYSize
        self.center = Point(xSize//2,ySize//2)
        return self.center
        
    def read_window(self, ul_or_win, lrPoint=None):
        """get data for Window object or 2 Point objects
        
        user can either provide one Window object or 2 Point objects as input
        Point.sample and Point.line have to be filled.
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

    def read_center_window(self, width=300):
        self.window = Window(centerPoint=self.get_center_from_dataset(),width=width)
        self.read_window(self.window)
        
    def window_coords_to_meter(self):
        self.window.ul.pixel_to_meter(self.geotransform)
        self.window.lr.pixel_to_meter(self.geotransform)
        
    def window_coords_to_lonlat(self):
        self.window.ul.pixel_to_lonlat(self.geotransform,self.projection)
        self.window.lr.pixel_to_lonlat(self.geotransform,self.projection)
    
    def window_coords_to_pixel(self):
        self.window.ul.lonlat_to_pixel(self.geotransform,self.projection)
        self.window.lr.lonlat_to_pixel(self.geotransform,self.projection) 
        
    def show(self, lonlat=False):
        fig = figure()
        ax = fig.add_subplot(111)
        extent = self.window.get_extent(self.dataset,lonlat)
        ax.imshow(self.data,extent=extent)#,origin='image')
        self.ax = ax
        show()

    def add_scalebar(self, loc=3):
        extent = self.window.get_extent(self.dataset)
        diffx = abs(extent[1]-extent[0])*1000
        diffy = abs(extent[3]-extent[2])*1000
        diff = max(diffx,diffy)
        # get closed magnitude to 10 % of image extent
        scalebarLength = 10**int(round(np.log10(diff/10)))
        scalebarLength /= 1000
        d = dict([(1, '1 km'),(10,'10 m'), (100,'100 m'), (1000,'1 km'), (10000,'10 km'),
                    (100000,'100 km'), (1000000,'1000 km')])
        asb = AnchoredSizeBar(self.ax.transData,
                              scalebarLength,
                              d[scalebarLength],
                              loc=loc)
        self.ax.add_artist(asb)
        self.ax.get_figure().canvas.draw()
        
class MOLA(ImgData):
    """docstring for MOLA"""
    def __init__(self,
                 fname='/Users/aye/Data/mola/megr_s_512_1.cub'):
        ImgData.__init__(self,fname)

class CTX(ImgData):
    """docstring for CTX"""
    def __init__(self,
                 fname='/Users/aye/Data/ctx/inca_city/ESP_011412_0985/'\
                 'B05_011412_0985_XI_81S063W.cal.des.cub.map.cub'):
        ImgData.__init__(self,fname)

    def add_mola_contours(self):
        self.window_coords_to_lonlat()
        mola = MOLA()
        mola.window = self.window.copy()
        mola.window_coords_to_pixel()
        mola.read_window(mola.window)
        mola.data = mola.data - mola.data.mean()
        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(111)
        plt.gray()
        ax.imshow(self.data, extent=self.window.get_extent(self.dataset))
        CS = ax.contour(mola.data, 8, cmap = cm.jet,
                         extent=self.window.get_extent(self.dataset),
                         origin='image' )
        plt.clabel(CS,fontsize=13, inline=1)
        ax.set_xlabel('Polar stereographic X [km]')
        ax.set_ylabel('Polar stereographic Y [km]')
        ax.set_title('CTX: ' +os.path.basename(self.fname))
        self.ax = ax
        plt.show()
        
class HiRISE(ImgData):
    """docstring for HiRISE"""
    def __init__(self,
                 fname='/Users/aye/Data/hirise/'\
                            'PSP_002380_0985_RED.cal.norm.map.equ.mos.cub'):
        ImgData.__init__(self,fname)
                

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
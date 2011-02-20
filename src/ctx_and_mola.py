#!/usr/bin/env python
# encoding: utf-8
"""
ctx_and_mola.py

Created by Klaus-Michael Aye on 2011-02-16.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
from __future__ import division
import matplotlib
# matplotlib.use('MacOSX')
import sys
import os
from osgeo import gdal,osr
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

molaFile = '/Users/aye/Data/mola/megr_s_512_1.cub'

def Usage():
    """docstring for Usage"""
    print 'Usage: {0} ctxdata samples lines width'.format(sys.argv[0])
    sys.exit(1)
    
def get_coords_from_pixels(dataset,sample, line):
    """provide coordinates in the data's projection from the pixel coordinates.
    
    Input: gdal Dataset
    Return: list [x,y] coordinates in the projection of the dataset
    >>> from osgeo import gdal
    >>> ds = gdal.Open('/Users/aye/Data/mola/megt_s_128_1.tif')
    
    Asking for the (0,1) pixel as measured in (sample,line), one gets the 
    coordinate of the current projection measured in meters from the origin of
    that projection.
    Have to test (0,1) and not (0,0) because a wrong order of arguments would 
    not be detected by the test because of the symmetry.
    >>> get_coords_from_pixels(ds,0,1)
    [-2355200.0, 2354740.0]
    """
    datasetTransform = dataset.GetGeoTransform()
    return gdal.ApplyGeoTransform(datasetTransform, sample, line)

def get_pixels_from_coords(dataset,x,y):
    """provide pixel coords from x,y coords.
    
    Input: gdal Dataset
    Return: list [line,sample] of the dataset for given coordinate
    >>> from osgeo import gdal
    >>> ds = gdal.Open('/Users/aye/Data/mola/megt_s_128_1.tif')
    
    Asking the pixels for the center coordinate of a south pole centered
    quadratic dataset should return half the samples and lines, because (0,0)
    in pixels is the upper left of the array. This file as 10240 lines and 
    samples, so we expect 5120 to get back as pixel entry for the center of 
    the projection:
    >>> get_pixels_from_coords(ds,0,1)
    [5120.0, 5119.997826086957]
    """
    datasetTransform = dataset.GetGeoTransform()
    success, tInverse = gdal.InvGeoTransform(datasetTransform)
    return gdal.ApplyGeoTransform(tInverse, x, y)

def main():
    """combine CTX and MOLA data.
    
    MOLA and CTX data will be combined with these tools.
    User shall provide line,sample center coordinate of CTX file ROI to 
    define distance in meters from southpole.
    """
    
    try:
        ctxData = sys.argv[1]
        ctxSample, ctxLine, ctxWidth = [int(i) for i in sys.argv[2:5]]
    except (IndexError,ValueError):
        Usage()
    ctxDS = gdal.Open(ctxData)
    molaDS = gdal.Open(molaFile)
    print 'Rastersize: ',ctxDS.RasterXSize, ctxDS.RasterYSize
    ctxULsample = ctxSample - ctxWidth//2
    ctxULline = ctxLine - ctxWidth//2
    ctxLRsample = ctxSample + ctxWidth//2
    ctxLRline = ctxLine + ctxWidth//2
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
    im = ax.imshow(ctxData, extent=(min(ulX,lrX),max(ulX,lrX),min(ulY,lrY),
                                     max(ulY,lrY)))
    # ax2 = fig.add_subplot(111)
    # im2 = ax2.imshow(molaData, extent=(min(ulX,lrX),max(ulX,lrX),min(ulY,lrY),
    #                                  max(ulY,lrY)))
    # cb2 = fig.colorbar(im2,orientation='vertical')
    # 
    
    CS = ax.contour(molaData, 20, cmap = cm.jet,
                     extent=(min(ulX,lrX),
                             max(ulX,lrX),
                             min(ulY,lrY),
                             max(ulY,lrY)),
                     origin='image' )
    plt.clabel(CS,fontsize=9, inline=1)
    plt.show()
 
def _test():
    import doctest, ctx_and_mola
    return doctest.testmod(ctx_and_mola)   

if __name__ == '__main__':
    _test()
    main()

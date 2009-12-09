#!/usr/bin/python

from gdal_imports import *
#import matplotlib
#matplotlib.use('WxAgg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def main():    
    fname1 = '/processed_data/PSP_003092_0985/PSP_003092_0985_RED.cal.norm.map.equ.mos.cub'
    fname2 = '/processed_data/PSP_003158_0985/PSP_003158_0985_RED.cal.norm.map.equ.mos.cub'

    xOff = 6849
    xEnd = 7826
    yOff = 18426
    yEnd = 18957
    
    xSize = xEnd - xOff
    ySize = yEnd - yOff

    xOff2 = 7443
    yOff2 = 19801
    inDs1 = gdal.Open(fname1, GA_ReadOnly)
    inDs2 = gdal.Open(fname2, GA_ReadOnly)
    inBand1 = inDs1.GetRasterBand(1)
    inBand2 = inDs2.GetRasterBand(1)
    data1 = inBand1.ReadAsArray(xOff, yOff, xSize, ySize)
    try:
        data2 = inBand2.ReadAsArray(xOff2, yOff2, xSize, ySize)
    except ValueError:
        print('probably out of range..')

    data1[np.where(data1 < 0)] = np.NaN
    data2[np.where(data2 < 0)] = np.NaN

    fig = plt.Figure()
    ax1 = fig.add_subplot(221)
    im1 = ax1.imshow(data1)
    ax2 = fig.add_subplot(222)
    im2 = ax2.imshow(data2)
    ax3 = fig.add_subplot(223)
    im3 = ax3.imshow(data1, cmap=cm.gray)
    im4 = ax3.imshow(data2, alpha=0.5)
    
    
    
    plt.show()


if __name__ == '__main__':
    main()

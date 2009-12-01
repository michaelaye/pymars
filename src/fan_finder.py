#!/usr/bin/python

from gdal_imports import *
import matplotlib.colors as colors
import scipy.ndimage as nd

def find_threshold(imgArray):
    #pdf, bins = np.histogram(imgArray, 30)
    # returning known value for now
    return 0.065

def load_cube_data():
    fname = '/Users/aye/Data/hirise/PSP_003092_0985_RED.cal.norm.map.equ.mos.cub'
    cube = gdal.Open(fname, GA_ReadOnly)
    print cube.GetDescription()
    # get subframe
    xOff = 6849
    xEnd = 7826
    yOff = 18426
    yEnd = 18957
    
    xSize = xEnd - xOff
    ySize = yEnd - yOff
    
    print "reading {0} at {1},{2} offset".format(fname, xOff, yOff)
    img = cube.ReadAsArray(xOff, yOff, xSize, ySize)
    
    print "minimum of array: ", img.min()
    img[np.where(img < 0.0)] = np.nan
    print "minimum of array after NaN determination: ", img.min()
    return img

def grey_processing(inputImg):
    return inputImg

def binary_processing(inputImg):
    return inputImg

def create_palette():
    palette = plt.cm.gray
    palette.set_under('g', 1.0)
    palette.set_bad('b', 1.0)
    palette.set_over('r', 1.0)
    return palette
    
def labeling():
    pass

def show_masked(myFigure, data, palette):
    ax = myFigure.add_subplot(111)
    im = ax.imshow(data, cmap=palette,
                   norm=colors.Normalize(vmin=data.min(),
                                         vmax=data.max(),
                                         clip=True))
    plt.colorbar(im, shrink=0.7)
    return ax
    
def main():
    arr_big = load_cube_data()
    arr_big = arr_big[:200, :200]
    
    arr_big = grey_processing(arr_big)
    
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(111)
    
    threshold = find_threshold(arr_big)
    
    palette = create_palette()
    
    arr_masked = plt.ma.masked_where(arr_big < threshold, arr_big)
#    im = ax1.imshow(arr_masked, cmap=palette,
#                    norm=colors.Normalize(vmin=arr_big.min(),
#                                          vmax=arr_big.max(),
#                                          clip=True))
#    
#    plt.colorbar(im, shrink=0.7)
    
    ax1 = show_masked(fig1, arr_masked, palette)
    
    arr_bin = plt.where(arr_big < threshold, 1, 0)
    struc8 = np.ones((3, 3))
    labels, n = nd.label(arr_bin, struc8)
    slices = nd.find_objects(labels)
        
    plt.figure(1)
    plt.title("I/F threshold at {0}, {1} fans found.".format(threshold, n))
    areas = []
    for i in range(n):
        y1 = slices[i][0].start
        y2 = slices[i][0].stop
        x1 = slices[i][1].start
        x2 = slices[i][1].stop
        area = arr_bin[slices[i]].sum()*0.25
        areas.append(area)
        x = (x2 - x1) / 2 + x1
        y = (y2 - y1) / 2 + y1
        print x, y
        ax1.annotate(str(i), xy=(x, y), xycoords='data')
#        ax1.annotate(str(i) + '\n' + str(area) + ' m^2', xy=(x, y), xycoords='data')
    
    plt.show()

if __name__ == '__main__':
    main()

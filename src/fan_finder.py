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

def preprocessing(inputImg):
    pass

def main():
    arr_big = load_cube_data()
    arr = arr_big[:200, :200]
    
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(111)
    palette = plt.cm.gray
    palette.set_under('g', 1.0)
    palette.set_bad('b', 1.0)
    palette.set_over('r', 1.0)
    threshold = find_threshold(arr_big)
    
    arr_masked = plt.ma.masked_where(arr_big < threshold, arr_big)
    im = ax2.imshow(arr_masked, cmap=palette,
                    norm=colors.Normalize(vmin=arr_big.min(),
                                            vmax=arr_big.max(),
                                            clip=True))
    
    plt.colorbar(im, shrink=0.7)
    
    arr_bin = plt.where(arr_big < threshold, 1, 0)
    struc8 = np.ones((3, 3))
    labels, n = nd.label(arr_bin, struc8)
    slices = nd.find_objects(labels)
    print len(slices)
    print slices[0]
    print slices[1]
    
    print labels[slices[0]]
    print arr_bin[slices[0]].sum()
    print arr_bin[slices[1]]
    print arr_bin[slices[1]].sum()
    print arr_bin[slices[2]]
    print arr_bin[slices[2]].sum()
    
    plt.figure(2)
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
        ax2.annotate(str(i) + '\n' + str(area) + ' m^2', xy=(x, y), xycoords='data')
    
    plt.figure(3)
    
    plt.hist(areas, 65)
    plt.show()

if __name__ == '__main__':
    main()

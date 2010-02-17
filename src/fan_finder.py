#!/Library/Frameworks/Python.framework/Versions/2.6/bin/python

from gdal_imports import *
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy.ma as ma
import scipy.ndimage as nd
import pickle
from canny import *

def find_threshold(imgArray):
    #pdf, bins = np.histogram(imgArray, 30)
    # returning known value for now
    return 0.065

def load_pickle():
    fname = '/Users/aye/Documents/hirise/fans/PSP_003092_0985_RED.cal.norm.map.equ.mos.cub.pickled_array'
    with open(fname) as f:
        data = pickle.load(f)
    return data
    
def load_cube_data():
    fname = '/Users/aye/Data/hirise/PSP_003092_0985/PSP_003092_0985_RED.cal.norm.map.equ.mos.cub'
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

def get_struc(coeff):
    arr = np.zeros(9)
    if coeff == 1:
        arr[4] = 1
    if coeff == 2:
        arr[1] = arr[7] = 1
    if coeff == 3:
        arr[1] = arr[4] = arr[7] = 1
    else:
        for i in range(coeff):
            arr[i] = 1
    return arr.reshape((3, 3))

def create_palette():
    palette = plt.cm.gray
    palette.set_under('g', 1.0)
    palette.set_bad('b', 1.0)
    palette.set_over('r', 1.0)
    return palette
    
def labeling(data):
    struc8 = np.ones((3, 3))
    labels, n = nd.label(data, struc8)
    return (labels, n)

def show_masked(data, palette):
    myFig = plt.figure()
    ax = myFig.add_subplot(111)
    im = ax.imshow(data, cmap=palette,
                   norm=colors.Normalize(vmin=data.min(),
                                         vmax=data.max(),
                                         clip=True))
    plt.colorbar(im, shrink=0.7)
    return (myFig, ax)
  
def show_data(data):
    myFig = plt.figure(figsize=(14, 10))
    ax = myFig.add_subplot(111)
    im = ax.imshow(data)
    return (myFig, ax)

def annotating(data, labels, n, myAx):
    slices = nd.find_objects(labels)
    areas = []
    for i in range(n):
        y1 = slices[i][0].start
        y2 = slices[i][0].stop
        x1 = slices[i][1].start
        x2 = slices[i][1].stop
        area = data[slices[i]].sum()*0.25
        areas.append(area)
        x = (x2 - x1) / 2 + x1
        y = (y2 - y1) / 2 + y1
        myAx.annotate(str(i), xy=(x, y), xycoords='data', color='white')
#        myAx.annotate(str(i) + '\n' + str(area) + ' m^2',
#                      xy=(x, y), xycoords='data', color='white')
    return areas
    
def binary_processing(inputImg):
    data = inputImg.copy()
    struc8 = np.ones((3, 3))
    struc4 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    struc1 = np.zeros((3, 3))
    struc1[1, 1] = 1
    struc25 = np.ones((5, 5))
    struc36 = np.ones((6, 6))
    data = nd.morphology.binary_opening(data, struc4)
    data = nd.morphology.binary_closing(data, struc4)

    return data
   
def grey_processing(inputImg):
    fp = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    return nd.filters.median_filter(inputImg, size=1)

def main():
    
    orig_img = load_pickle()
    preprocced_img = grey_processing(orig_img)
    threshold = find_threshold(preprocced_img)
    palette = create_palette()
#    arr_masked = ma.masked_where(preprocced_img < threshold, preprocced_img)

    fig1, ax1 = show_data(orig_img)
    
    arr_bin = np.where(preprocced_img < threshold, 1, 0)
#    arr_bin = (canny(preprocced_img, 0.05, 0))[2]
#    rois = []
#    totalArea = []
#    all_areas = []

    data = binary_processing(arr_bin)
    labels, n = labeling(data)
    fig2, ax2 = show_data(data)
    ax2.set_title('{0} fans found.'.format(n))
    areas = annotating(data, labels, n , ax2)
#    all_areas.append(areas)
#    totalArea.append(sum(areas))
#    rois.append(n)
        
#    fig = plt.figure()
#    fig.add_subplot(211)
#    plt.plot(structs, rois, 'ro', label='rois')
#    plt.legend()
#    fig.add_subplot(212)
#    plt.plot(structs, totalArea, 'bo', label='total')
#    plt.legend()
    
#    fig = plt.figure()
#    plt.hist(all_areas[5], 20)
    
    plt.show()

if __name__ == '__main__':
    main()

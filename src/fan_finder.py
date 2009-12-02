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

def get_struc(coeff):
    arr = np.zeros(9)
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
  
def show_binary(data):
    myFig = plt.figure()
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
#        print x, y
#        myAx.annotate(str(i), xy=(x, y), xycoords='data', color='white')
        myAx.annotate(str(i) + '\n' + str(area) + ' m^2',
                      xy=(x, y), xycoords='data', color='white')
    
def binary_processing(inputImg, neighbours, iterations=1):
    if neighbours > 8 or neighbours < -1:
        raise ValueError("neighbours between -1 and 8")
        sys.exit(-1)
    struc8 = np.ones((3, 3))
    struc4 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    if neighbours == 4:
        struc = struc4
    elif neighbours == 8:
        struc = struc8
    elif neighbours == -1:
        return inputImg
    else:
        struc = get_struc(neighbours)
        
    outputImg = nd.morphology.binary_opening(inputImg, struc, iterations)
    return outputImg

def main():
    orig_img = load_cube_data()
    small_img = orig_img[:200, :200]
    
    preprocced_img = grey_processing(small_img)
    
    threshold = find_threshold(preprocced_img)
    
    palette = create_palette()
    
    arr_masked = plt.ma.masked_where(preprocced_img < threshold, preprocced_img)

#    fig1, ax1 = show_masked(arr_masked, palette)
    
    arr_bin = plt.where(preprocced_img < threshold, 1, 0)

    for i in [-1, 4, 8]:
        data = binary_processing(arr_bin, i)
        labels, n = labeling(data)
        fig, ax = show_binary(data)
        ax.set_title('I/F threshold at {0}, {1} fans found.'.format(threshold, n))
        annotating(data, labels, n , ax)
    
    plt.show()

if __name__ == '__main__':
    main()

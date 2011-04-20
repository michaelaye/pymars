from __future__ import division
import matplotlib
from osgeo import gdal
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import numpy.ma as ma
import numpy as np
import scipy.ndimage as nd
import pickle
from canny import *
import roi
from hirise_tools import save_plot
import sys
import os

class DataFinder():
    """class to provide data from different sources"""
    def __init__(self, fname=None, foldername=None, noOfFiles=None):
        self.fname = fname
        self.foldername = foldername
        self.noOfFiles = noOfFiles
        self.set_system_root_path()
        if not np.any(fname,foldername,noOfFiles):
            self.fname = os.path.join(self.data_root,
                                      'hirise',
                                      'PSP_003092_0985',
                                      'PSP_003092_0985_RED.cal.norm.map.equ.mos.cub')
            self.data_type = 'single'
                                      
    def set_system_root_path(self):
        if sys.platform == 'darwin':
            self.data_root='/Users/aye/Data/'
        else:
            self.data_root='/processed_data/'

    def get_dataset(self):
        if self.data_type == 'single':
            ds = gdal.Open(self.fname)
            return ds
           
def get_dataset():
    df = DataFinder()
    return df.get_dataset()
    
def get_data():
    try:
        obsID = obsIDs[index]
    except TypeError:
        obsID = index
    except NameError:
        obsID = index
    fname = ''.join(['/Users/aye/Documents/hirise/fans/',
                     obsID,
                     '_RED.cal.norm.map.equ.mos.cub.pickled_array'])
    with open(fname) as f:
        data = pickle.load(f)
    return data
    
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

def annotating(data, labels, n):#, myAx):
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
#        myAx.annotate(str(i), xy=(x, y), xycoords='data', color='white')
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
#    iters = 3 # good for Ithaca
    iters = 1 # good for Inca City
    data = nd.morphology.binary_opening(data, struc8,iterations=iters)
    data = nd.morphology.binary_closing(data, struc8,iterations=iters)
    return data
   
def grey_processing(inputImg):
#    fp = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    fp = np.ones((3, 3))
    data = nd.median_filter(inputImg, size=7)
    data = nd.grey_closing(data, footprint=fp)
    data = nd.grey_opening(data,footprint=fp)
    return data

def hist_equal(data):
    "needs integer as input!!"
    # range is +2 to have the highest luminance to get into correct bin
    bins = numpy.arange(np.min(data), np.max(data) + 2)
    # first the histogram of luminances
    h, bins = numpy.histogram(data, bins=bins)
    # now get the cdf
    cdf = h.cumsum()
    # now get the unique luminance values
    uniques = numpy.unique(data)
    nPixel = data.size
    newcdf = numpy.round((cdf - cdf.min()) * 255 / (nPixel - 1))
    nData = data.copy()
    for lum in uniques:
#        nData[data == lum] = newcdf[bins[:-1] == lum][0]
        numpy.putmask(nData, data == lum, newcdf[bins[:-1] == lum][0])
    return nData

def calc_salience(data):
    # scale to 8 bit, as given in algorithm of LPSC paper,
    # maybe possible to change, have to check that
    img = numpy.array(data * 255 / data.max(), dtype=int)
    bins = numpy.arange(img.min(), img.max() + 2)
    h, bins = numpy.histogram(img, bins)
    s = img.copy()
    d = {}
    for lum in numpy.unique(img):
        s_i = 0
        for i, h_i in zip(bins[:-1], h):
            s_i += h_i * abs(lum - i)
        d[lum] = s_i
    for index in numpy.arange(s.size):
        s_i = 0
        i_p = img.ravel()[index]
        s.ravel()[index] = d[i_p]
    return s
 
def plot_n_save_salience(s, obsid):
    fig = plt.figure()
    ax = fig.add_subplot(211)
    im = ax.imshow(s)
    ax.set_title(obsid)
    plt.colorbar(im)
    ax = fig.add_subplot(212)
    ax.hist(s.ravel(), bins=30, log=True)
    plt.savefig(''.join([obsid, '.sal.png']))
    plt.close(fig)

def do_saliences(inputData = 'IncaCity_cleaned.csv'):
    roidata = roi.ROI_Data()
    roidata.read_in(inputData)
    roidict = roidata.dict
    for obsid in roidict:
        print obsid
        data = get_data(obsid)
        # normalize all images to top at 1.0
        # that way, an increase of range of pixel values also means an increase
        # of variance, and therefore more information, but still comparable 
        # within all data treated
        img = data / data.mean()
        s = calc_salience(img)
        print obsid, s.min(), s.max()
        plot_n_save_salience(s, obsid)
     
        
def main(argv=None):
    if argv == None:
        argv = sys.argv
    if argv[1] =='inca':
        f = 'IncaCity_cleaned.csv'
    elif argv[1] == 'ithaca':
        f = 'Ithaca_cleaned.csv'
    roidata = roi.ROI_Data()
    roidata.read_in(f)
    roidict = roidata.dict
    all_areas = []
    fan_counts = []
    total = []
    lsds = []
    actual_obs = []
    palette = create_palette()
    for obsID in roidict:
        if obsID.startswith('ESP'): continue
        print 'doing ', obsID
        orig_img = get_data(obsID)
        if orig_img.ndim == 0:
            print 'Image not loaded. Exiting'
            sys.exit(1)
        preprocced_img = grey_processing(orig_img)
        try:
            threshold = float(roidict[obsID]['Threshold'])
        except ValueError:
            continue
#        s = calc_salience(orig_img)
        threshold *= 1.03  # Inca City tuning
#        threshold *= 1.05 # Ithaca good tune
        arr_masked = ma.masked_where(preprocced_img < threshold, preprocced_img)
        fig1, ax1 = show_data(arr_masked)
        fig1.savefig(obsID+'_thresholded.png')
        plt.close(fig1)
        arr_bin = np.where(preprocced_img < threshold, 1, 0)
    #    arr_bin = (canny(preprocced_img, 0.05, 0))[2]
    
        data = binary_processing(arr_bin)
        labels, n = labeling(data)
        fig2, ax2 = show_data(data)
        ax2.set_title('{0} fans found.'.format(n))
        fig2.savefig(obsID+'binary.png')
        plt.close(fig2)
#===============================================================================
# changed!!! here and in annotating
#===============================================================================
        areas = annotating(data, labels, n)# , ax2)
        all_areas.append(areas)
        total.append(sum(areas))
        fan_counts.append(n)
        lsds.append(float(roidict[obsID]['L_s']))
        actual_obs.append(int(obsID.split('_')[1]))
        
    fig = plt.figure()
    ax = fig.add_subplot(211)
    plt.plot(lsds, fan_counts, 'ro', label='fans')
    ax.set_xlim(xmax=260)
    ax.set_xticks([])
    ax.set_ylabel('No of Fans')
    ax2 = fig.add_subplot(212)
    plt.plot(lsds, total, 'bo', label='total')
    ax2.set_xlim(xmax=260)
    ax2.set_ylim(ymax=40000)
    ax2.set_xlabel('L_s [deg]')
    ax2.set_ylabel('Total area of fans per subframe [m^2]')
    fig.savefig('Numbers_areas.pdf')
#    fig = plt.figure()
#    plt.hist(all_areas[5], 20)
    
    plt.show()

if __name__ == '__main__':
    main()

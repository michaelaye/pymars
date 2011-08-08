#!/Library/Frameworks/Python.framework/Versions/2.6/bin/python

from __future__ import division
import matplotlib
matplotlib.use('Agg')
from gdal_imports import *
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import numpy.ma as ma
import scipy.ndimage as nd
import pickle
from canny import *
import roi
from hirise_tools import save_plot
import sys
        
def get_data(index):
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
     
def fan_structure(median=11):
    """function to analyse fan sub structure by setting non-fan pixels to 0 and histo-equalizing the remaining img with only fans. Also
    median-filtering is done to reduce noise."""
    xcoords=[388, 449,497]
    ycoords =[142, 254, 118]
    x2 = [403,590]
    y2 = [286,254]
    x3 = [403,459]
    y3 = [286,375]
    x4 = [1372,1420]
    y4 = [610,680]
    x5 = [1372,1467]
    y5 = [610,590]
    x6 = [1321,1422]
    y6 = [612,750]
    x7 = [1321,1439]
    y7 = [612,585]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    data = get_data('ESP_011931_0945')
    data = nd.grey_erosion(data,footprint=np.ones((3,3)))
    data = nd.grey_erosion(data,footprint=np.ones((3,3)))
    data = nd.grey_dilation(data,footprint=np.ones((3,3)))
    data = nd.grey_dilation(data,footprint=np.ones((3,3)))
    threshold=0.045
    fans = data < threshold
    data = data*255/data.max()
    intfans = np.zeros(data.shape, dtype=np.uint16)
    intfans[fans] = np.round(data[fans])
    filtered = nd.median_filter(intfans,median)
    equ = hist_equal(filtered)
    im = ax.imshow(equ,cmap = cm.spectral,aspect='equal')
    ax.set_title('Fans within fans in Ithaca, filtered, opened and hist-equalized')
    ax.set_xlabel('0.5 m/pixel')
#    fig.savefig('Fans_within_fans.png')
#    cb =plt.colorbar(im,shrink=0.75)
#    cb.set_label('I/F')
    plt.plot(xcoords[:-1],ycoords[:-1],[xcoords[0],xcoords[2]],[ycoords[0],ycoords[2]],
            color='white',
            hold=True,
            scalex=False,scaley=False)
    plt.plot(x2,y2,color='white',hold=True,scalex=False,scaley=False)
    plt.plot(x3,y3,color='white',hold=True,scalex=False,scaley=False)
    plt.plot(x4,y4,color='white',hold=True,scalex=False,scaley=False)
    plt.plot(x5,y5,color='white',hold=True,scalex=False,scaley=False)

    plt.plot(x6,y6,color='white',hold=True,scalex=False,scaley=False)
    plt.plot(x7,y7,color='white',hold=True,scalex=False,scaley=False)

#    plt.close(fig)
    plt.show()

def test_fan_struc():
    """looping over fan_structures"""
    for size in range(3,16,2):
        fan_structure(size)    

def compare_sizes():
    """docstring for compare_sizes"""
    data1 = get_data(1)
    x = data1.shape[0]
    y = data1.shape[1]
    data2 = get_data('ESP_011931_0945')
    data2 = data2[:x,:y]
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    im1 = ax1.imshow(data1,aspect='equal')
    ax1.set_ylabel('Inca City fans')
    ax1.set_title('Size comparison between Inca City (L_s=206) and Ithaca (L_s=208) fans')
    plt.colorbar(im1,shrink=0.95)
    ax2 = fig.add_subplot(212)
    im2 = ax2.imshow(data2,aspect='equal')
    ax2.set_ylabel('Ithaca fans')
    ax2.set_xlabel('Resolution: 0.5 m/pixel')
    plt.colorbar(im2, shrink=0.95)
    plt.show()
    
def time_sequence(targetcode, part):
    """docstring for time_sequence"""
    obs = get_some_obs('_'+targetcode)
    lsdict = get_l_s(targetcode)
    fig = plt.figure()
    plotcode = 231
    for counter,obsid in enumerate(obs):
        if plotcode == 234: break
        if counter < part: continue
        ax = fig.add_subplot(plotcode)
        data = get_data(obsid)
        print data.shape
#        data = data[0:260, 1500:1950]
#        data = data[920:1060, 850:1250]
#        data = data[150:450, 600:976]
        data = data[700:1050, 0:448]
#        data = data[575:757, 1640:1856]
#        data = data[375:645, 1090:1420]
#       data = data[106:410, 304:636]
## Inca city ROIs
########################################
#        data = data[360:520,300:448]
#        data = data[330:410,426:500]
#        data = data[56:150,70:170]
#        data = data[250:320,345:500]
#        data = data[111:206,190:312]
#########################################
        title = "{0} L_s={1:.0f}".format(obsid,lsdict[obsid])
        im = ax.imshow(data,vmin=0.0,vmax=0.2)
        plt.colorbar(im)
        ax.set_title(title)
        ax.set_xticklabels([])
        ax = fig.add_subplot(plotcode+3)
        im = ax.imshow(data)
        plt.colorbar(im)
        plotcode += 1
#        save_plot(data,title,obsid,'png',vmax=None,vmin=None)

def make_roi_collections():
    """docstring for make_roi_collections"""
    pass    
    
def make_plots(no):
    """docstring for make_plots"""
    for i in range(0,16,3):
        time_sequence('0945',i)
        plt.savefig('Ithaca_sequence_'+str(no)+'_'+str(i)+'.pdf')
        
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

from __future__ import division
from osgeo import gdal
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as nd
from hirise_tools import save_plot
import mahotas
import sys
import os
from canny import canny
from hirise_tools import save_plot

ndimage = nd
numpy = np

blocks = ['768_5120',
        '768_5248',
        '896_3200',
        '896_3328',
        '896_5120',
        '896_5376',
        '896_5632',
        '128_3072',
        '256_3456']

blocksize=512

def get_fan_no(index):
    block = blocks[index]
    x,y = block.split('_')
    ds = get_dataset()
    data = ds.ReadAsArray(int(x),int(y),blocksize,blocksize)
    return data

def get_fname(aList):
    """get a string filename out of list of elements"""
    return '_'.join([str(i) for i in aList])
    
class DataFinder():
    """class to provide data from different sources"""
    def __init__(self, fname=None, foldername=None, noOfFiles=None):
        self.fname = fname
        self.foldername = foldername
        self.noOfFiles = noOfFiles
        self.set_system_root_path()
        if not np.any(fname,foldername,noOfFiles):
            self.fname = os.path.join(self.data_root,
                                      'PSP_003092_0985',
                                      'PSP_003092_0985_RED.cal.norm.map.equ.mos.cub')
            self.data_type = 'single'
                                      
    def set_system_root_path(self):
        if sys.platform == 'darwin':
            self.data_root='/Users/aye/Data/hirise/'
        else:
            self.data_root='/processed_data/'

    def get_dataset(self):
        if self.data_type == 'single':
            ds = gdal.Open(self.fname)
            return ds
           
def get_dataset():
    df = DataFinder()
    return df.get_dataset()
 
def labeling(data):
    struc8 = np.ones((3, 3))
    labels, n = nd.label(data, struc8)
    return (labels, n)
  
def get_fan_blocks():
    """deliver block coords"""
    for block in blocks:
        x,y = block.split('_')
        yield (int(x),int(y),blocksize,blocksize)

def get_data(dataset = None,breakpoint=1e8):
    """provide image data.
    
    If a dataset is provided loop through it in sizes of GDAL blocksize.
    If not, provide the data for blocks with fans as provided by get_fan_blocks
    """
    # this to get blocks with fans, a predefined set above
    if dataset == None:
        ds = get_dataset()
        band=ds.GetRasterBand(1)
        for t in get_fan_blocks():
            yield band.ReadAsArray(*t),t[0],t[1]
    else:
        #this is the standard loop through the big image
        xSize = dataset.RasterXSize
        ySize = dataset.RasterYSize
        band = dataset.GetRasterBand(1)
        blockSize = (blocksize,blocksize)
        for x in range(0,xSize,blockSize[0]):
            if x + blockSize[0] > xSize: continue
            if x > breakpoint: break
            for y in range(0,ySize,blockSize[1]):
                if y+blockSize[1]> ySize: continue
                data = band.ReadAsArray(x,y,blockSize[0],blockSize[1])
                if data.min() < -1e6: continue
                yield (data,x,y)


def get_uint_image(data):
    data *= np.round(255/data.max())
    return data.astype(np.uint)
 
def get_grad_mag(image):
    grad_x = ndimage.sobel(image, 0)
    grad_y = ndimage.sobel(image, 1)
    grad_mag = numpy.sqrt(grad_x**2+grad_y**2)
    return grad_mag
 
def test_min():
    ds = get_dataset()
    X= ds.RasterXSize
    Y= ds.RasterYSize
    blobs = np.zeros((Y/blocksize,X/blocksize),dtype=np.uint8)
    counter = 0
    kernel = [[0,1,0],
              [1,1,1],
              [0,1,0]]
    for db in get_data(ds):
        counter += 1
        data,x,y = db
        if np.mod(counter,10)== 0:
            print("{0:3d} %".format(x*100//X))
        data = nd.median_filter(data,3)
        
        # this is the first pixel selector, cropping with a
        # 'x' sigma exclusion criteria around the mean
        # with a 2 population pixel histogram, that's of course rude
        # really should do first search for minimum and if that doesn't
        # work such brutal 'x'-sigma from a mean'-approach
        cropped = data<data.mean()-3*data.std()
        cropped = nd.binary_closing(cropped,kernel,iterations=3)
        cropped = nd.binary_opening(cropped,kernel,iterations=3)
        fig = plt.figure()
        ax=fig.add_subplot(211)
        ax.imshow(data)
        ax.set_title(str(x)+'_'+str(y))
        ax2=fig.add_subplot(212)
        labeled,n = nd.label(cropped,np.ones((3,3)))
        blobs[y/blocksize,x/blocksize]=n 
        ax2.imshow(labeled)
        ax2.set_title(str(n)+' blobs found.')
        fig.savefig(get_fname(['local_histos/min',x,y,'.png']))
        plt.close(fig)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    im = ax.imshow(blobs)
    plt.colorbar(im)
    plt.savefig('local_histos/blobs.png')
    np.save('blobs',blobs)
  
def test_blob_array():
    ds = get_dataset()
    X= ds.RasterXSize
    Y= ds.RasterYSize
    bs = 128
    newblobs = np.zeros((Y//bs,X//bs))
    for xNow in range(0,X,bs):
        print xNow
        if xNow+bs > X: continue
        for yNow in range(0,Y,bs):
            if yNow+bs > Y: continue
            data = ds.ReadAsArray(xNow,yNow, bs, bs)
            myMax = data.max()
            if myMax < 0: continue
            newblobs[yNow//bs,xNow//bs]=myMax
    print newblobs
    fig = plt.figure()
    ax = fig.add_subplot(111)
    im = ax.imshow(newblobs,aspect='equal')
    plt.colorbar(im)
    plt.show()

      
def test_grey_morph():
    root = 'local_histos/'
    final_t = 0 # for get_new_t
    for datablock in get_data():
        data,x,y = datablock
        data = get_uint_image(data)
        print(x,y)
        for i in range(0,30,4):
            mdata = nd.grey_opening(data,(i,i))
            R = mahotas.thresholding.rc(mdata)
            gradient = get_grad_mag(mdata)
            fig = plt.figure(figsize=(12,12))
            ax1 = fig.add_subplot(211)
            ax1.imshow(gradient)
            ax1.set_title(str(i)+', R: '+str(R))
            ax2 = fig.add_subplot(212)
            ax2.hist(gradient.flatten(),50)
            plt.savefig(get_fname([root+'img',x,y,i,'.png']))
            plt.close(fig)

def test_gaussian_filters():
    for i,datablock in enumerate(get_data(ds)):
        data, x,y = datablock
        print(block)
        for sigma in range(5,10):
            fig = plt.figure()
            ax = fig.add_subplot(211)
            fdata = nd.gaussian_filter(data,sigma)
            fdata = (fdata * 256).astype(np.uint)
            T = mahotas.thresholding.otsu(fdata)
            R = mahotas.thresholding.rc(fdata)
            im = ax.imshow(fdata,interpolation='nearest')
            ax.set_title('Sigma: ' + str(sigma)+', T='+str(T)+', R='+str(R))
            plt.colorbar(im)
            ax2 = fig.add_subplot(212)
            # ax2.hist(fdata.flatten(),50)
            labels,n = nd.label(fdata<R,np.ones((3,3)))
            ax2.imshow(labels)
            ax2.set_title(str(n))
            plt.savefig('local_histos/gaussian_fan'+str(i)+'_sigma'+str(sigma)+'.png')
            plt.close(fig)
    
def test_local_thresholds():
    ds = get_dataset()
    band = ds.GetRasterBand(1)
    for coords in get_block_coords():
        data = band.ReadAsArray(*coords)
        if data.min() < -1e6: continue # no data values in the block
        data = data * 256
        data = data.astype(np.uint)
        print 'doing ', coords
        fig = plt.figure()
        ax = fig.add_subplot(111)
        T = mahotas.thresholding.rc(data)
        labels, n = labeling (data < T)
        # ax.imshow(data,cmap=cm.gray)
        ax.hist(data.flatten(),15,log=True)
        ax.set_title(str(T))
        plt.savefig(os.path.join('local_histos',
                                 'block_'+str(coords[0])+'_'+str(coords[1])+'.png'))
        plt.close(fig)


if __name__ == '__main__':
    # test_blob_array()
    test_min()
    # test_grey_morph()
    # test_gaussian_filters()
    # test_local_thresholds()
from __future__ import division
from osgeo import gdal
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as nd
import hirise_tools
from hirise_tools import save_plot,getStoredPathFromID, getObsIDFromPath
import mahotas
import sys
import os
from canny import canny
from hirise_tools import save_plot

np.seterr(all='raise')
ndimage = nd
numpy = np
save_rootpath=os.environ['HOME'] + '/results/fan_finder/'


default_fname = '/Users/maye/Data/hirise/PSP_002380_0985_RED.cal.norm.map.equ.mos.cub'    

####
debug = True
####


def get_fname(aList):
    """get a string filename out of list of elements"""
    return '_'.join([str(i) for i in aList])

class DataFinder():
    """class to provide data from different sources"""
    blocks = ['768_5120',
        '768_5248',
        '896_3200',
        '896_3328',
        '896_5120',
        '896_5376',
        '896_5632',
        '128_3072',
        '256_3456']

    def __init__(self, obsid=None,fname=None, foldername=None, noOfFiles=None, blocksize=256):
        if debug: print obsid,fname,foldername,noOfFiles
        self.fname = fname
        self.obsid = obsid
        self.foldername = foldername
        self.noOfFiles = noOfFiles
        self.blocksize=blocksize
        self.data_root = hirise_tools.DEST_BASE
        if not np.any([obsid,fname,foldername,noOfFiles]):
            self.fname = os.path.join(self.data_root,
                                      'PSP_003092_0985',
                                      'PSP_003092_0985_RED.cal.norm.map.equ.mos.cub')
            self.data_type = 'single'
        elif obsid:
            if debug: print('in obsid elif of DataFinder')
            self.fname = getStoredPathFromID(self.obsid)
        self.get_dataset()
    
    def get_dataset(self):
        # if self.data_type == 'single':
        if debug: print self.fname
        self.obsid = getObsIDFromPath(self.fname)
        self.ds = gdal.Open(self.fname)
        self.xSize = self.ds.RasterXSize
        self.ySize = self.ds.RasterYSize

    def get_fan_no(self,index):
        """get data blocks from the pre-defined coordinates, defined for the default 3092 image."""
        block = self.blocks[index]
        x,y = block.split('_')
        data = self.ds.ReadAsArray(int(x),int(y),blocksize,blocksize)
        return data

    def get_fan_blocks(self):
        """deliver block coords"""
        for block in self.blocks:
            x,y = block.split('_')
            yield (int(x),int(y),blocksize,blocksize)

    def get_data(self, predefined=False, breakpoint=1e8):
        """provide image data.
        
        in:breakpoint counts the number of pixels in x-axis to reach until this returns.
        No check for data quality is done, should be done at caller function.
        """
        # this to get blocks with fans, a predefined set above
        if predefined:
            band = self.ds.GetRasterBand(1)
            for t in self.get_fan_blocks():
                yield band.ReadAsArray(*t),t[0],t[1]
        else:
            #this is the standard loop through the big image
            band = self.ds.GetRasterBand(1)
            blockSize = (self.blocksize, self.blocksize)
            for x in range(0,self.xSize,blockSize[0]):
                if x + blockSize[0] > self.xSize: continue
                if x > breakpoint: break
                for y in range(0, self.ySize, blockSize[1]):
                    if y+blockSize[1] > self.ySize: continue
                    data = band.ReadAsArray(x,y,blockSize[0],blockSize[1])
                    yield (data,x,y)

def get_dataset(obsid=None,fname=None):
    df = DataFinder(obsid=obsid, fname=fname)
    return df.ds

def labeling(data):
    struc8 = np.ones((3, 3))
    labels, n = nd.label(data, struc8)
    return (labels, n)

def get_uint_image(data):
    data *= np.round(255/data.max())
    return data.astype(np.uint)

def get_grad_mag(image):
    grad_x = ndimage.sobel(image, 0)
    grad_y = ndimage.sobel(image, 1)
    grad_mag = numpy.sqrt(grad_x**2+grad_y**2)
    return grad_mag

class ImgHandler():
    def __init__(self,img,x,y,action_code=''):
        """action_code is a sequence of letters indicating the kind of filter
        to be applied and a digit that shall be used as parameter for that
        filter, e.g. c2 means closing with 2 iterations.
        So a combination of 2 closings and 3 openings would be encoded:
        'c2o3'
        """
        self.img = img
        self.x = x
        self.y = y
        self.action_code = action_code
        self.kernels = [[[0,1,0],
                         [1,1,1],
                         [0,1,0]],
                         np.ones((3,3))]
        myIter = iter(action_code)
        #make sure to call myIter.next() somewhere to advance to next character
        for code in myIter:
            if code == ' ' or code == '_': continue
            # param is used by several branches so i take it out here
            # some need another parameter and they advance the iterator further
            param = int(myIter.next())
            
            # median filtering
            if code == 'm':
                self.img = nd.median_filter(self.img, param)
            
            # stretching image to max: param
            elif code == 's':
                img = self.img
                img = param*(img-img.min())/(img.max()-img.min())
                self.img = img
            
            # morphological closing with param iterations
            elif code == 'c':
                kernel = int(myIter.next())
                self.binarized = nd.binary_closing(self.binarized,
                                                 self.kernels[kernel],
                                                 iterations=param)
            
            # morphological opening with param iterations
            # o31 means 3 iterations opening with the np.ones kernel (8-connected)
            # c20 means 2 iterations closing with the 4-connected kernel
            elif code == 'o':
                kernel = int(myIter.next())
                self.binarized = nd.binary_opening(self.binarized,
                                                 self.kernels[kernel],
                                                 iterations=param)
            
            # labeling the binarized (=binary) image with either 4- or 8-
            # connected-ness, controlled by param
            elif code == 'l':
                self.labels, self.n = nd.label(self.binarized,
                                               self.kernels[param])
                self.get_label_area()
            
            # create binarized image by exclusion of pixels that are
            # float(code.param)(e.g. 2.4) sigma away from mean value
            elif code.isdigit():
                # trick to have float factor for exclusion
                factor = float(code+'.'+str(param))
                img = self.img
                self.binarized = img < np.median(img) - factor * img.std()
            
            else:
                print('No defined action found for: ',code,param)
    
    def get_label_area(self,resolution=0.5):
        slices = nd.find_objects(self.labels)
        areas = []
        labeled_pixels = []
        for i in range(self.n):
            y1 = slices[i][0].start
            y2 = slices[i][0].stop
            x1 = slices[i][1].start
            x2 = slices[i][1].stop
            pixel_count = self.binarized[slices[i]].sum()
            area = pixel_count*resolution*resolution
            areas.append(area)
            labeled_pixels.append(pixel_count)
        self.area = sum(areas)
        self.labeled_pixels = sum(labeled_pixels)


def scanner(fname=None, do_plot = False, blocksize=256):
    df = DataFinder(fname=fname,blocksize=blocksize)
    X= df.ds.RasterXSize
    Y= df.ds.RasterYSize
    blobs = np.zeros((Y/df.blocksize,X/df.blocksize))
    orig = np.zeros((Y/df.blocksize,X/df.blocksize))
    # sigmas_orig = np.zeros((Y/blocksize,X/blocksize))
    # sigmas_stretched = np.zeros((Y/blocksize,X/blocksize))
    counter = 0
    kernel_half = [[0,1,0],
              [1,1,1],
              [0,1,0]]
    kernel = np.ones((3,3))
    
    # TODO: compare with median filtering
    # TODO: compare with and without stretching
    # TODO: compare 4 and 8 connected labeling/opening/closing
    
    action_codes = ['s1_23_o21_c11_l1',
                    # 's1_25_o21_c11_l1',
                    # 's1_27_o21_c11_l1'
                    ]
    
    # action_codes = ['s1_15_o31_l1',
    #                 's1_15_o31_c11_l1',
    #                 's1_20_o21_c11_l1']
    
    save_folder = save_rootpath + df.obsid + '_' +str(blocksize) +'_'+ '__'.join(action_codes)
    if not os.path.isdir(save_folder):
        os.mkdir(save_folder)
    # 2nd parameter (=breakpoint) is the coordinate value of x until to loop.
    for db in df.get_data():
        counter += 1
        data,x,y = db
        if np.mod(counter,100) == 0 or counter == 1:
            print("{0:3d} % of x-axis pixels.".format(x*100//X))
        
        if data.min() < -1e6: continue # black area around image data is NaN (-1e-38)
        
        orig[y/df.blocksize,x/df.blocksize]=data.mean()
        handlers = []
        for i,code in enumerate(action_codes):
            eval('handlers.append(ImgHandler(data.copy(),x,y,code))')
        blobs[y/df.blocksize,x/df.blocksize]=handlers[0].labeled_pixels/blocksize**2
        if do_plot == True:
            fig = plt.figure(figsize=(14,10))
            ax=fig.add_subplot(221)
            ax.imshow(data)
            ax.set_title(str(x)+'_'+str(y))
            for handler,subplot in zip(handlers,[222,223,224]):
                ax=fig.add_subplot(subplot)
                ax.imshow(handler.labels)
                ax.set_title(str(handler.n)+' blobs, '+handler.action_code+\
                           ' '+str(handler.area))
            save_fname = get_fname([save_folder+'/subframe',x,y,'.png'])
            fig.savefig(save_fname)
            plt.close(fig)
    np.save(save_folder+'/blobs',blobs)
    np.save(save_folder+'/orig',orig)

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
    # scanner(fname='/Users/maye/Data/hirise/PSP_002380_0985_RED.cal.norm.map.equ.mos.cub')
    scanner(fname=None)
    # test_grey_morph()
    # test_gaussian_filters()
    # test_local_thresholds()

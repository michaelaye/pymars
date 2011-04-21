from __future__ import division
import matplotlib
matplotlib.use('Agg')
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
import mahotas

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
 
def labeling(data):
    struc8 = np.ones((3, 3))
    labels, n = nd.label(data, struc8)
    return (labels, n)
  
def get_fan_blocks():
    """deliver block coords"""
    blocks = ['768_5120',
            '768_5248',
            '896_3200',
            '896_3328',
            '896_5120',
            '896_5376',
            '896_5632']
    for block in blocks:
        x,y = block.split('_')
        yield (int(x),int(y),128,128)

def get_block_coords(dataset = None):
    """provide coordinates for ReadAsArray.
    
    If a dataset is provided loop through it in sizes of GDAL blocksize.
    If not, provide the coords for blocks with fans as provided by get_fan_blocks
    """
    # this to get blocks with fans
    if dataset == None:
        for t in get_fan_blocks():
            yield t
    else:
        xSize = dataset.RasterXSize
        ySize = dataset.RasterYSize
        band = dataset.GetRasterBand(1)
        blockSize = band.GetBlockSize()
        for x in range(0,xSize,blockSize[0]):
            if x + blockSize[0] > xSize: continue
            if x > 1000: break
            for y in range(0,ySize,blockSize[1]):
                if y+blockSize[1]> ySize: continue
                yield (x,y,blockSize[0],blockSize[1])
    
    
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
        T = mahotas.thresholding.otsu(data)
        labels, n = labeling (data < T)
        ax.imshow(data,cmap=cm.gray)
        plt.savefig(os.path.join('local_histos',
                                 'block_'+str(coords[0])+'_'+str(coords[1])+'.png'))
        plt.close(fig)
            
if __name__ == '__main__':
    test_local_thresholds()
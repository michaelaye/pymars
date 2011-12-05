from __future__ import division
from osgeo import gdal
import numpy as np
import scipy.ndimage as nd
from traits.api import File, HasTraits, Str, Button, Array, Int,Enum
from traitsui.api import View, Item, UItem,HGroup
import os
from scipy.cluster import vq

class KMeans(HasTraits):
    fname = File()
    feedback = Str
    feedback2 = Str
    next = Button
    data = Array
    k_iter = Int(20)
    k = Int(2)
    framesize = Enum(128,256,512,1024)
    
    traits_view = View('framesize',
                       'k',
                       'k_iter',
                       'fname',
                       HGroup(
                           UItem('feedback',style='custom'),
                           UItem('feedback2',style='custom'),
                       ),
                       resizable=True,
                       buttons=['OK'],
                       )        
    
    def _data_changed(self):
        codebook, distortion = vq.kmeans(self.data, self.k, self.k_iter )
        self.feedback += str(codebook.min()) + '\n'
        self.feedback2 += str(distortion)
    
    def _framesize_changed(self):
        self._read_data()
        
    def _read_data(self):
        ds = gdal.Open(self.fname)
        self.XSize = ds.RasterXSize
        self.YSize = ds.RasterYSize
        self.data = ds.ReadAsArray(0,0,self.framesize,self.framesize).flatten()
        
    def _fname_changed(self):
        if not os.path.exists(self.fname):
            pass
        self._read_data()
        
kmeans = KMeans(fname='/Users/maye/Data/hirise/PSP_003092_0985/PSP_003092_0985_RED5.cal.norm.cub')
kmeans.configure_traits()
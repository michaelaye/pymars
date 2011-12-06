from __future__ import division
from osgeo import gdal
import numpy as np
import scipy.ndimage as nd
import os
from scipy.cluster import vq
# traits imports
from traits.api import File, HasTraits, Str, Button, Array, Int,Enum, \
        on_trait_change, Instance, DelegatesTo, Float,Range
from traitsui.api import View, Item, UItem,HGroup, RangeEditor
from enable.api import ComponentEditor, Component
# chaco imports
from chaco.api import ArrayPlotData, Plot, gray, HPlotContainer
from chaco.tools.image_inspector_tool import ImageInspectorTool, ImageInspectorOverlay

class KMeans(HasTraits):
    fname = File()
    next = Button
    data = Array
    k_iter = Enum(20,40,60,80,100)
    k = Int(2)
    framesize = Enum(128,256,512,1024)
    limit = Float
    distortion = Float
    plot = Instance(Component)
    traits_view = View(HGroup(
                        'framesize',
                        Item('k',
                             editor=RangeEditor(low=2, high=20, mode='spinner')),
                        'k_iter'
                       ),
                       'fname', 'limit','distortion',
                       UItem('plot',editor=ComponentEditor(size=(700,400)),
                                height=0.7),
                       resizable=True,
                       buttons=['OK'],
                       )        
    
    @on_trait_change( 'k, k_iter, data')
    def _data_changed(self):
        codebook, distortion = vq.kmeans(self.data.flatten(), self.k, self.k_iter )
        self.limit = codebook.min()
        self.distortion = distortion
        data = self.data < self.limit
        try:
            self.pd.set_data("imagedata", data)
        except AttributeError:
            pass
    
    def _framesize_changed(self):
        self._read_data()
     
    def _plot_default(self):
        data = self.data < self.limit
        pd = self.pd = ArrayPlotData(imagedata=data,orig=self.data)
        plot1 = Plot(pd, default_origin='top left')
        plot2 = Plot(pd, default_origin='top left')
        img_plot1 = plot1.img_plot("imagedata",colormap=gray,padding=0)[0]
        img_plot2 = plot2.img_plot("orig",colormap=gray,padding=0)[0]
        container = HPlotContainer(plot1,plot2)
        container.spacing=0
        plot1.padding_right=0
        plot2.padding_left=0
        plot2.y_axis.orientation= 'right'
        return container
        
    def _read_data(self):
        ds = gdal.Open(self.fname)
        self.XSize = ds.RasterXSize
        self.YSize = ds.RasterYSize
        self.data = ds.ReadAsArray(0,0,self.framesize,self.framesize)
        
    def _fname_changed(self):
        if not os.path.exists(self.fname):
            pass
        self._read_data()
        
kmeans = KMeans(fname='/Users/maye/Data/hirise/PSP_003092_0985/PSP_003092_0985_RED5.cal.norm.cub')
kmeans.configure_traits()
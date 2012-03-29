from __future__ import division
from osgeo import gdal
import numpy as np
import scipy.ndimage as nd
import os
from scipy.cluster import vq
# my mars data interface
import mars
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
    xoff = Int(0)
    yoff = Int(0)
    k_iter = Enum(20,40,60,80,100)
    k = Int(2)
    framesize = Enum(128,256,512,1024)
    limit = Float
    distortion = Float
    plot = Instance(Component)
    traits_view = View(HGroup(
                        'framesize',
                        Item('k',
                             editor=RangeEditor(low=2, high=30, mode='spinner')),
                        'k_iter',
                        'next'
                       ),
                       'fname',
                       HGroup('limit','distortion','xoff','yoff'),
                       UItem('plot',editor=ComponentEditor(size=(700,400)),
                                height=0.7),
                       resizable=True,
                       buttons=['OK'],
                       )        
    
    def _next_fired(self):
        if (self.xoff + 2*self.framesize) > self.XSize:
            self.xoff = 0
            self.yoff += self.framesize
        else:
            self.xoff += self.framesize
        self._read_data()
        self.pd.set_data('orig',self.data)
        
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
        img = mars.ImgData(self.fname)
        self.XSize = img.ds.RasterXSize
        self.YSize = img.ds.RasterYSize
        img.read_center_window(width=self.framesize)
        self.data = img.data
        
    def _fname_changed(self):
        if not os.path.exists(self.fname):
            pass
        self._read_data()

local_fname = '/Users/maye/Data/hirise/inca_city/PSP_003092_0985/PSP_003092_0985_RED5.cal.norm.cub'
if os.path.exists(local_fname):
    kmeans = KMeans(fname=local_fname)
else:
    kmeans = KMeans()
    print("Found no local file.")

kmeans.configure_traits()

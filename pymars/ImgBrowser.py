from __future__ import division
import numpy as np
import scipy.ndimage as nd
import os
from glob import glob
# my mars data interface
import mars
# traits imports
from traits.api import File, HasTraits, Button, Array, Int, Property, \
        on_trait_change, Instance, Range, List, Directory
from traitsui.api import View, Item, UItem,HGroup, RangeEditor
from enable.api import ComponentEditor, Component
# chaco imports
from chaco.api import ArrayPlotData, Plot, gray, HPlotContainer
from chaco.tools.image_inspector_tool import ImageInspectorTool, ImageInspectorOverlay

class Browser(HasTraits):
    fpath = File
    fname = Property(depends_on = 'fpath')
    fdir = Directory
    next = Button
    data = Array
    flist = List
    xoff = Int
    yoff = Int
    index = Int
    plot = Instance(Component)
    traits_view = View('fdir',
                       HGroup(
                        'next'
                       ),
                       'fname',
                       HGroup('xoff','yoff'),
                       UItem('plot',editor=ComponentEditor(size=(700,400)),
                                height=0.7),
                       resizable=True,
                       buttons=['OK'],
                       )        
    
    def _fdir_changed(self):
        flist = glob(os.path.join(self.fdir,'*.img'))
        self.index = 0
        if not len(flist) == 0:
            self.fpath = flist[self.index]
            self._read_data()

    def _read_data(self):
        img = mars.ImgData(self.fpath)
        self.data = img.data

    def _get_fname(self):
        return os.path.basename(self.fpath)

    def _next_fired(self):
        if (self.xoff + 2*self.framesize) > self.XSize:
            self.xoff = 0
            self.yoff += self.framesize
        else:
            self.xoff += self.framesize
        self._read_data()
        self.pd.set_data('orig',self.data)
        
    @on_trait_change( 'data')
    def _data_changed(self):
        
        data = self.data < self.limit
        try:
            self.pd.set_data("imagedata", data)
        except AttributeError:
            pass
    
    def _framesize_changed(self):
        self._read_data()
     
    # def _plot_default(self):
    #     data = self.data
    #     pd = self.pd = ArrayPlotData(imagedata=data,orig=self.data)
    #     plot1 = Plot(pd, default_origin='top left')
    #     img_plot1 = plot1.img_plot("imagedata",colormap=gray,padding=0)[0]
    #     return plot1
        
        

def main():
    browser = Browser(fdir='/Users/maye/Data/DAWN/')

    browser.configure_traits()


if __name__ == '__main__':
    main()
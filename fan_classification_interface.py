#!/usr/bin/env python
# encoding: utf-8
"""
training_traits.py

Created by K.-Michael Aye on 2011-11-12.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

from traits.api import HasTraits, Enum, Str, Instance, Button, Bool, DelegatesTo
from traitsui.api import View, HGroup, UItem, Group, Item
from numpy.random import randint
from chaco.api import ArrayPlotData, Plot
from enable.component_editor import ComponentEditor

class FeatureData(HasTraits):
    fanclass = Enum(['Line','Angular','Blotch'])
        
class ControlBar(HasTraits):
    hasBoulder = Bool
    isWhite = Bool
    featureData = Instance(FeatureData)
    fanclass = DelegatesTo('featureData')
    
    traits_view = View(Item('fanclass',style='custom'),
                             'hasBoulder','isWhite')
        
    def __init__(self):
        self.featureData = FeatureData()
        
class FanClassifier(HasTraits):
    imageID = Str('Image ID')
    plot = Instance(Plot)
    controlBar = Instance(ControlBar)
    hasBoulder = DelegatesTo('controlBar')
    isWhite = DelegatesTo('controlBar')
    
    controlGroup = Group(UItem('controlBar',style='custom'))
    plotGroup = Group(UItem('plot', editor=ComponentEditor(), resizable=True) )
    
    traits_view = View('imageID',
                    HGroup(controlGroup,plotGroup))
    
    def __init__(self):
        self.controlBar = ControlBar()

if __name__ == '__main__':
    window = FanClassifier()
    window.configure_traits()

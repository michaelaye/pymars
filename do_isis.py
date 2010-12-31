#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Klaus-Michael Aye on 2010-10-30.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

from __future__ import division
import sys
import os.path
from glob import glob
from pprint import pprint
from subprocess import check_call

class ISIS_Cube():
    """CTX processing steps"""
    def __init__(self, fname):
        self.fname = fname
        self.states=['UNK','IMG','cub','cal','des','map']
        self.states_dir={'cal.des.cub':'des',
                         'cal.cub':'cal',
                         'cub':'cub',
                         'IMG':'IMG',
                         'cal.des.map.cub':'map'}
        self.state=self.states[0]
        parts = self.fname.split('.')
        self.fRoot = parts[0]
        pointIndex = self.fname.find('.')
        self.state = self.states_dir[self.fname[pointIndex+1:]]
        print 'File status:',self.state
    def do_cube(self):
        if self.state != 'IMG':
            print 'Wrong state for cube production'
            return
        newFileName = self.fRoot + '.cub'
        cmd = ('mroctx2isis',
                'from='+self.fname,
                'to='+newFileName)
        print(cmd)
        check_call(cmd)
        cmd = ('spiceinit',
                'from='+newFileName)
        print(cmd)
        check_call(cmd)
        self.state = 'cub'
        self.fname = newFileName
    def do_cal(self):
        if self.state != 'cub':
            print 'Wrong state for calibration'
            return
        newFileName = self.fRoot + '.cal.cub'
        cmd = ('ctxcal',
                'from='+self.fname,
                'to='+newFileName)
        print(cmd)
        check_call(cmd)
        self.state ='cal'
        self.fname = newFileName
    def do_destripe(self):
        if self.state != 'cal':
            print 'Wrong state for destriping'
            return
        newFileName = self.fRoot + '.cal.des.cub'
        cmd = ('ctxevenodd',
                'from='+self.fname,
                'to='+newFileName)
        print(cmd)
        check_call(cmd)
        self.state ='des'
        self.fname = newFileName
    def do_map(self):
        if self.state != 'des':
            print 'Wrong state for mapping'
            return
        newFileName = self.fRoot + '.cal.des.map.cub'
        cmd = ('cam2map',
                'from='+self.fname,
                'to='+newFileName,
                'pixres=map',
                'map=ctx_polar_stereo.map')
        print(cmd)
        check_call(cmd)
        self.state = 'map'
        self.fname = newFileName
        
        
def main():
    fList = glob('/Users/aye/Data/ctx/inca_city/*/*.des.cub')
    for i,f in enumerate(fList):
        print 'processing {0}'.format(f)
        data = ISIS_Cube(f)
        data.do_map()
        print("\n###\n{0:2.2f}% done.\n###\n".format((i+1)/len(fList)*100.))

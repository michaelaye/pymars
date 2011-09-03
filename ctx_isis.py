#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Klaus-Michael Aye on 2010-10-30.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

from __future__ import division
import sys
import os
from glob import glob
from pprint import pprint
from subprocess import check_call,CalledProcessError
op = os.path

class ISIS_Cube():
    """CTX processing steps"""
    def __init__(self, fname, search=True):
        "fname: absolute path"
        self.fname = fname
        self.states=['UNK','IMG','cub','cal','des','map']
        self.extensions = ['xxx','IMG','cub','cal.cub','cal.des.cub',
                            'cal.des.map.cub']
        self.states_dir=dict(zip(self.extensions,self.states))
        self.state=self.states[0]
        self.fRoot = fname.split('.')[0]
        if not search:
            # the extension string is used as the key for the states dictionary
            self.state = self.states_dir[op.basename(fname).partition('.')[2]]
        else:
            print 'Searching...'
            self.state = 'UNK'
            self.search_other_states()
        print 'File status:',self.state
        print self.fname
    def do_all(self):
        self.do_cube()
        self.do_cal()
        self.do_destripe()
        self.do_map()
    def search_other_states(self):
        fnames = glob(self.fRoot+'*')
        extensions = [op.basename(fname).partition('.')[2] for fname in fnames]
        # start from highest evolved state
        for state,ext in zip(reversed(self.states),reversed(self.extensions)):
            if ext in extensions:
                self.state = state
                self.fname = self.fRoot + '.' + ext 
                return
    def do_process(self, cmd, state, fname):
        print(cmd)
        try:
            check_call(cmd)
        except CalledProcessError,e:
            print 'Got error from subprocess:',e
        self.state = state
        self.fname = fname
    def do_cube(self):
        """Import IMG into ISIS and do SPICEINIT."""
        if self.state != 'IMG':
            print 'Wrong state for cube production'
            return
        newFileName = self.fRoot + '.cub'
        cmd = ('mroctx2isis',
                'from='+self.fname,
                'to='+newFileName)
        self.do_process(cmd,'cub',newFileName)
        self.do_spice()
    def do_spice(self):
        cmd = ('spiceinit',
                'from='+self.fname)
        self.do_process(cmd,'cub',self.fname)
    def do_cal(self):
        if self.state != 'cub':
            print 'Wrong state for calibration'
            return
        newFileName = self.fRoot + '.cal.cub'
        cmd = ('ctxcal',
                'from='+self.fname,
                'to='+newFileName)
        self.do_process(cmd,'cal',newFileName)
    def do_destripe(self):
        if self.state != 'cal':
            print 'Wrong state for destriping'
            return
        newFileName = self.fRoot + '.cal.des.cub'
        cmd = ('ctxevenodd',
                'from='+self.fname,
                'to='+newFileName)
        self.do_process(cmd,'des',newFileName)
    def do_map(self):
        if self.nomap == True: 
            print 'Map projection denied by request.'
            return
        if self.state != 'des':
            print 'Wrong state for mapping'
            return
        newFileName = self.fRoot + '.cal.des.map.cub'
        cmd = ('cam2map',
                'from='+self.fname,
                'to='+newFileName,
                'pixres=map',
                'map='+os.getenv('HOME')+'/Data/ctx/ctx_polar_stereo.map')
        self.do_process(cmd,'map',newFileName)
            
        
        
def main():
    mapping, fList = sys.argv[1],sys.argv[2:]
    if not fList:
        print('provide a filename or list (with ls *.???).')
        sys.exit(1)
    for i,f in enumerate(fList):
        print 'processing {0}'.format(f)
        data = ISIS_Cube(f,search=True)
        if mapping == 'nomap':
            data.nomap = True
        data.do_all()
        print("\n###\n{0:2.2f}% done.\n###\n".format((i+1)/len(fList)*100.))

if __name__ == '__main__':
    main()
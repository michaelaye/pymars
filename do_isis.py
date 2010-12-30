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

    
fList = glob('/Users/aye/Data/ctx/richardson_crater/*.IMG')

calExt = '.cal'
evenoddExt = '.des'
mapExt = '.map'
cubExt= '.cub'

for i,f in enumerate(fList):
    if not 'P11' in f: continue
    try:
        fRoot = f.rstrip('.IMG')
        newExt = cubExt
        newFileName = fRoot + newExt
        cmd = ('mroctx2isis',
                'from='+f,
                'to='+newFileName)
        print(cmd)
        check_call(cmd)
        cmd = ('spiceinit',
                'from='+newFileName)
        print(cmd)
        check_call(cmd)
    
        oldFileName = newFileName
        newExt = calExt + newExt
        newFileName = fRoot + newExt
        cmd = ('ctxcal',
                'from='+oldFileName,
                'to='+newFileName)
        print(cmd)
        check_call(cmd)
    
        oldFileName = newFileName
        newExt = evenoddExt + newExt
        newFileName = fRoot + newExt
        cmd = ('ctxevenodd',
                'from='+oldFileName,
                'to='+newFileName)
        print(cmd)
        check_call(cmd)

        # oldFileName = newFileName
        # newExt = mapExt + newExt
        # newFileName = fRoot + newExt
        # cmd = ('cam2map',
        #         'from='+oldFileName,
        #         'to='+newFileName,
        #         'pixres=map',
        #         'map=ctx_polar_stereo.map')
        # print(cmd)
        # check_call(cmd)
        print("\n###\n{0:2.2f}% done.\n###\n".format((i+1)/len(fList)*100.))
    except:
        continue
    
    
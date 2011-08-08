#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Klaus-Michael Aye on 2010-11-01.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import glob
import pprint
import shutil

def put_in_hirise_folders():
    basePath = '/Users/aye/Data/ctx/ithaca'
    os.chdir(basePath)

    fileList = os.listdir(os.getcwd())

    for fName in fileList:
        head,sep,tail = fName.partition('.')
        print head
        if not (tail.endswith('cub') or tail.endswith('IMG') or
                tail.endswith('IMG_label')):
                continue
        try:
            phase, orbit, targetCode, mode, coords = head.split('_')
        except ValueError:
            continue
        if phase.startswith('B'):
            newPhase = 'ESP'
        else:
            newPhase = 'PSP'
        newFolderName = '_'.join([newPhase,orbit,targetCode])
        print newFolderName
        if not os.path.exists(basePath + os.sep + newFolderName):
            os.mkdir(basePath + os.sep + newFolderName)
        shutil.move(basePath + os.sep + fName, basePath + os.sep + newFolderName + os.sep)

def remove_some_cubes():
    basePath = '/Users/aye/Data/ctx/ithaca'
    os.chdir(basePath)
    
    fileList = os.listdir(os.getcwd())
    for fName in fileList:
        if not os.path.isdir(fName): continue
        dirName = fName
        fNames = os.listdir(basePath + os.sep + dirName + os.sep)
        for f in fNames:
            head,sep,tail = f.partition('.')
            if tail == 'cub': os.remove(basePath + os.sep + dirName + os.sep + f)

        
        
if __name__ == '__main__':
    put_in_hirise_folders()
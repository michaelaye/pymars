#!/usr/bin/env python
# encoding: utf-8
"""
std_scanner.py

Created by K.-Michael Aye on 2011-09-10.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
import subprocess as sub
import sys
import os
import glob
from hirise_tools import *
import pickle

def main():
    search_path = FROM_BASE+'ctx/*.cal.des.cub'
    fnames = glob.glob(search_path)
    cmd_base = ['gdalinfo','-stats']
    std_data = {}
    for fname in fnames[:10]:
        cmd = cmd_base+[fname]
        output = sub.Popen(cmd, stdout=sub.PIPE).communicate()[0]
        std = output.split()[-1].split('=')[-1]
        std_data[os.path.basename(fname).split('.cal.des.cub')[0]]=std
    with open('std_data.pkl','w') as f:
        pickle.dump(std_data,f)
    print std_data
if __name__ == '__main__':
    main()


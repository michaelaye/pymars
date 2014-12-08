#!/usr/bin/env python
# encoding: utf-8

from fan_finder2 import *
from multiprocessing import Pool
import time
from glob import glob
import pprint

def myscanner(bs):
    scanner(blocksize=bs)

def fscanner(fname):
    scanner(fname=fname)

if __name__ == '__main__':
#    bsizes = [128,256,512,1024,2048]
    list_of_fnames = glob('/imgdata/RDRgen/JP2s/PSP_??????_0???/PSP_??????_0???_RED.JP2')
    pprint.pprint(list_of_fnames)
    p = Pool()
    t = time.time()
    p.map(fscanner, list_of_fnames)
    print '{0} seconds.'.format(time.time()-t)
    

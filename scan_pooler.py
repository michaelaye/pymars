#!/usr/bin/env python
# encoding: utf-8

from fan_finder2 import *
from multiprocessing import Pool
import time

def myscanner(bs):
    scanner(blocksize=bs)

if __name__ == '__main__':
    bsizes = [128,256,512,1024,2048]
    p = Pool()
    t = time.time()
    p.map(myscanner, bsizes)
    print '{0} seconds.'.format(time.time()-t)
    

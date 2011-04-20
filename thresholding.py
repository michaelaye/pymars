#!/usr/bin/env python
# encoding: utf-8
"""
k-means-thresholding.py

Created by K.-Michael Aye on 2010-07-12.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""
from __future__ import division
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys
# import cv
from fan_finder import get_data

counter = 0
final_t = 0

def get_uint8(data):
    """make uint8 array out of Hirise data"""
    newd = np.round(data*255/data.max())
    newd = newd.astype(np.uint8)
    return newd

def get_new_t(data, t):
    """to be called recursively"""
    global counter
    global final_t
    counter +=1
    print 'given t:',t
    print 'counter:',counter
    eps = 0.00001
    g1 = data[data<t]
    g2 = data[data>t]
    t1 = g1.mean()
    t2 = g2.mean()
    new_t = (t1+t2)/2.
    if abs(new_t-t)<eps:
        print 'stop criteria reached'
        print 'diff:',new_t-t
        final_t = new_t
        return
    else:
        get_new_t(data,new_t)

def k_means_cluster(data):
    """one-dimensional case of k-means clustering algorithm, taken from Wikipedia
    entry for Thresholding"""
    t = np.median(data)
    new_t = get_new_t(data, t)
    print 'final t:',final_t
    return final_t

# def test_cvAdapt(data):
#     """docstring for test_cvAdapt"""
#     dst = data.copy()
#     for block in range(3,22,2):
#         for param in range(20):
#             print 'Doing {0} with {1}'.format(block,param)
#             cv.AdaptiveThreshold(data,dst,1,
#                                  adaptive_method=cv.CV_ADAPTIVE_THRESH_MEAN_C,
#                                  thresholdType=cv.CV_THRESH_BINARY_INV,
#                                  blockSize=block,
#                                  param1=param )
#             fig = plt.figure()
#             ax = fig.add_subplot(111)
#             ax.set_title('Block = {0}, Param1 = {1}'.format(block,param))
#             im = ax.imshow(dst)
#             fig.savefig('test_adapt/adapt_block_'+str(block)+'_param_'+str(param)+'.png')
#             plt.close(fig)

def main():
    """not implemented"""
    data = get_data(2)
    data = get_uint8(data)
    # test_cvAdapt(data)


if __name__ == '__main__':
    main()

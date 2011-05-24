#!/usr/bin/env python
# encoding: utf-8
"""
thresholding.py

Created by K.-Michael Aye on 2010-07-12.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""
from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import sys
# import cv
from fan_finder import get_data


def get_uint8(data):
    """make uint8 array out of Hirise data"""
    newd = np.round(data*255/data.max())
    newd = newd.astype(np.uint8)
    return newd

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

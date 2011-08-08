#!/usr/bin/python

from gdal_imports import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import sys
import roi
import os.path
import hirise_tools
import pickle

args = sys.argv
try:
    roi_data_file = args[1]
except IndexError:
    print "Usage: {0} roi_data_file".format(args[0])
    sys.exit(1)

roidata = roi.ROI_Data()
roidata.read_in(roi_data_file)
roidict = roidata.dict

for obsID in roidict:
    ccd = roidict[obsID]['CCDColour']
    fname = hirise_tools.getMosPathFromIDandCCD(obsID, ccd)
    print fname
    ds = gdal.Open(fname, GA_ReadOnly)
    band = ds.GetRasterBand(1)
    xOff = roidict[obsID]['Map_Sample_Offset']
    yOff = roidict[obsID]['Map_Line_Offset']
    xCoreg = roidict[obsID]['CoReg_Sample_Offset']
    yCoreg = roidict[obsID]['CoReg_Line_Offset']
    xSize = roidict[obsID]['NSAMPLES']
    ySize = roidict[obsID]['NLINES']
    data = band.ReadAsArray(int(xOff) + int(xCoreg),
                          int(yOff) + int(yCoreg),
                          int(xSize), int(ySize))
    data[np.where(data < 0)] = np.NaN
    with open(os.path.basename(fname) + '.pickled_array', 'w') as outfile:
        pickle.dump(data, outfile)

    fig = plt.figure()
    ax = fig.add_subplot(211)
    im = ax.imshow(data)
    ax.set_title(os.path.basename(fname))
    plt.colorbar(im)
    ax2 = fig.add_subplot(212)
    im2 = ax2.imshow(data, vmin=0.0, vmax=0.3)
    ax2.set_title(os.path.basename(fname) + ', fixed stretch')
    plt.colorbar(im2)
    fig.savefig(os.path.basename(fname) + '.png', dpi=100)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(data.ravel(), 30, log=True)
    fig.savefig(os.path.basename(fname) + '.histogram.png', dpi=100)
print 'done'


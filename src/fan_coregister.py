#!/usr/bin/python

from gdal_imports import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pickle
import os.path


def main():
    coordFile = open('subframes.pkl', 'r')
    bigList, index = pickle.load(coordFile)
    coordFile.close()
#    xOff = 6849
#    xEnd = 7826
#    yOff = 18426
#    yEnd = 18957
    
#    xSize = xEnd - xOff
#    ySize = yEnd - yOff
#    fixedList = [fname1, fixed_obsID, mainX, mainY, xSize, ySize, coregX, coregY]
#                   0         1          2     3       4      5       6       7

    for i, obs in enumerate(bigList):
        if i != 0 and (obs[6] == 0 and obs[7] == 0):
            print 'skipping {0} with no offsets'.format(obs[1])
            continue
        fname, x, y = obs[0], obs[2], obs[3]
        xSize, ySize = obs[4], obs[5]
        coregX, coregY = obs[6], obs[7]
        print("found {0}".format(fname))
        cube = gdal.Open(fname, GA_ReadOnly)
        inBand = cube.GetRasterBand(1)
        try:
            data = inBand.ReadAsArray(int(x) + int(coregX),
                                      int(y) + int(coregY),
                                      xSize, ySize)
        except ValueError:
            print('probably out of range..')
            continue
        data[np.where(data < 0)] = np.NaN
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

if __name__ == '__main__':
    main()

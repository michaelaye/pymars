#!/usr/bin/python

from gdal_imports import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import os.path


def main():
    coordFile = open("Coordinates_ESP_lat_-81.386_lon_295.667.txt")
    lines = coordFile.readlines()
    coordFile.close()
    xOff = 6849
    xEnd = 7826
    yOff = 18426
    yEnd = 18957
    
    xSize = xEnd - xOff
    ySize = yEnd - yOff


    for line in lines:
        if line.split()[0].split('_')[-1].split('.')[0] != 'RED':
            continue
        fname, x, y = line.split()[:3]
        print("found {0}".format(fname))
        cube = gdal.Open(fname, GA_ReadOnly)
        inBand = cube.GetRasterBand(1)
        try:
            data = inBand.ReadAsArray(int(x), int(y), xSize, ySize)
        except ValueError:
            print('probably out of range..')
            continue
        data[np.where(data < 0)] = np.NaN
        fig = plt.figure()
        ax = fig.add_subplot(111)
#        im = ax.imshow(data, vmin=0.0, vmax=0.27)
        im = ax.imshow(data)
        ax.set_title(os.path.basename(fname))
        plt.colorbar(im)
        fig.savefig(os.path.basename(fname) + '.png', dpi=100)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.hist(data.ravel(), 30, log=True)
        fig.savefig(os.path.basename(fname) + '.histogram.png', dpi=100)
    print 'done'

if __name__ == '__main__':
    main()

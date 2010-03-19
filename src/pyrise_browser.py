#!/usr/bin/python
'''
Created on Aug 16, 2009

@author: aye
'''

from gdal_imports import *
import matplotlib
matplotlib.use('Tkagg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import sys
import tkFileDialog as fd

def rebin(a, newshape):
        '''Rebin an array to a new shape.
        '''
        assert len(a.shape) == len(newshape)

        slices = [ slice(0, old, float(old) / new) for old, new in zip(a.shape, newshape) ]
        coordinates = np.mgrid[slices]
        indices = coordinates.astype('i')   #choose the biggest smaller integer index
        return a[tuple(indices)]

def rebin_factor(a, newshape):
        '''Rebin an array to a new shape.    
        newshape must be a factor of a.shape.        
        '''
        assert len(a.shape) == len(newshape)
        assert not np.sometrue(np.mod(a.shape, newshape))

        slices = [ slice(None, None, old / new) for old, new in zip(a.shape, newshape) ]
        return a[slices]

def downsample(band):
    maxsize = 2000
    cols = band.XSize
    rows = band.YSize
    factorX = cols / maxsize
    factorY = rows / maxsize
    factor = max(factorX, factorY)
#    maxsize = maxsize / factor * factor # integer cut-off trick to find largest common factor
    xShrinked = []
    yShrinked = []
    for yOff in range(0, rows, maxsize):
        print "{0:2.1f} % done.".format(100.0 * yOff / rows)
        if yOff + maxsize < rows:
            numrows = maxsize
        else:
            numrows = rows - yOff
        for xOff in range(0, cols, maxsize):
            if xOff + maxsize < cols:
                numcols = maxsize
            else:
                numcols = cols - xOff
            data = band.ReadAsArray(xOff, yOff, numcols, numrows)
            oldY, oldX = data.shape
            newX = oldX / factor
            newY = oldY / factor
            data = rebin(data, (newY, newX))
            xShrinked.append(data)
        data = np.hstack(xShrinked)
        xShrinked = []
        yShrinked.append(data)
    imData = np.vstack(yShrinked)
    yShrinked = None
    return imData

class Cube:
    displaySize = 512
    overlap = 2 # 1 block is 128, keep 2*128 = 256 in FOV when shifting
    def __init__(self, fname):
        self.inDs = gdal.Open(fname, GA_ReadOnly)
        # get image size
        self.rows = self.inDs.RasterYSize
        self.cols = self.inDs.RasterXSize
        self.bands = self.inDs.RasterCount
        self.inBand = self.inDs.GetRasterBand(1)
        self.inBand.SetNoDataValue = np.NaN
        blockSizes = self.inBand.GetBlockSize()
        self.xBlockSize = blockSizes[0]
        self.yBlockSize = blockSizes[1]
        self.xOffsets = range(0, self.cols, self.xBlockSize)
        self.yOffsets = range(0, self.rows, self.yBlockSize)
        self.xInd = len(self.xOffsets) / 2
        self.yInd = len(self.yOffsets) / 2
        self.read_data()

    def read_data(self, rows=None, cols=None):
        if rows == None:
            rows = self.displaySize
        if cols == None:
            cols = self.displaySize
        self.data = self.inBand.ReadAsArray(self.xOffsets[self.xInd],
                                            self.yOffsets[self.yInd],
                                            rows,
                                            cols)

    def up(self, event):
        self.yInd -= self.overlap
        self.yInd = max(self.yInd, 0)
        self.read_data()

        im.set_data(self.data)
        ax.set_title(' '.join([str(self.xInd), str(self.yInd)]))
        plt.draw()

    def down(self, event):
        self.yInd += self.overlap
        self.yInd = min(self.yInd, len(self.yOffsets) - 1)
        if self.yOffsets[self.yInd] + self.displaySize < self.rows:
            numRows = self.displaySize
        else:
            numRows = self.rows - self.yOffsets[self.yInd]
        self.read_data(rows=numRows)

        im.set_data(self.data)
        ax.set_title(' '.join([str(self.xInd), str(self.yInd)]))
        plt.draw()

    def next(self, event):
        self.xInd += self.overlap
        self.xInd = min(self.xInd, len(self.xOffsets) - 1)
        if self.xOffsets[self.xInd] + self.displaySize < self.cols:
            numCols = self.displaySize
        else:
            numCols = self.cols - self.xOffsets[self.xInd]
        self.read_data(cols=numCols)
        im.set_data(self.data)
        print self.data.mean()
        ax.set_title(' '.join([str(self.xInd), str(self.yInd)]))
        plt.draw()

    def prev(self, event):
        self.xInd -= self.overlap
        self.xInd = max(self.xInd, 0)
        self.read_data()
        im.set_data(self.data)
        ax.set_title(' '.join([str(self.xInd), str(self.yInd)]))
        plt.draw()


def main():
    if sys.platform == 'darwin':
    fname = '/Users/aye/Data/hirise/PSP_003092_0985/PSP_003092_0985_RED.cal.norm.map.equ.mos.cub'
    else:
    options = {}
    options['filetypes'] = [('mosaic cubes', '.mos.cub'), ('all cubes', '.cub')]
    fname = fd.askopenfilename(initialdir='/processed_data', **options)
    
    callback = Cube(fname)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    fig.subplots_adjust(bottom=0.2)
    im = ax.imshow(callback.data)
    
    axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
    axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
    axup = plt.axes([0.59, 0.05, 0.1, 0.075])
    axdown = plt.axes([0.48, 0.05, 0.1, 0.075])
    bnext = Button(axnext, 'Next')
    bnext.on_clicked(callback.next)
    bprev = Button(axprev, 'Previous')
    bprev.on_clicked(callback.prev)
    bup = Button(axup, 'Up')
    bup.on_clicked(callback.up)
    bdown = Button(axdown, 'Down')
    bdown.on_clicked(callback.down)
    
    plt.show()

if __name__ == '__main__':
    main()

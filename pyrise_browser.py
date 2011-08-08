#!/usr/bin/env python
'''
Created on Aug 16, 2009

@author: aye
'''

from gdal_imports import *
#import matplotlib
#matplotlib.use('Tkagg')
import matplotlib.pyplot as plt
from matplotlib.pylab import *
from matplotlib.widgets import Button
import sys
import tkFileDialog as fd
from matplotlib.widgets import RectangleSelector
from pylab import subplot, arange, plot, sin, cos, pi, show

def line_select_callback(event1, event2):
    'event1 and event2 are the press and release events'
    x1, y1 = event1.xdata, event1.ydata
    x2, y2 = event2.xdata, event2.ydata
    print "(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2)
    print " The button you used were: ", event1.button, event2.button


#current_ax=subplot(111)                    # make a new plotingrange
#N=100000                                   # If N is large one can see improvement
#x=10.0*arange(N)/(N-1)                     # by use blitting!
#
#plot(x,sin(.2*pi*x),lw=3,c='b',alpha=.7)   # plot something
#plot(x,cos(.2*pi*x),lw=3.5,c='r',alpha=.5)
#plot(x,-sin(.2*pi*x),lw=3.5,c='g',alpha=.3)
#
#print "\n      click  -->  release"

# drawtype is 'box' or 'line' or 'none'
#LS = RectangleSelector(current_ax, line_select_callback,
#                       drawtype='box',useblit=True,
#                       minspanx=5,minspany=5,spancoords='pixels')

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
    overlap = 1 # 1 block is 128, keep 2*128 = 256 in FOV when shifting
    def __init__(self, fname):
        self.inDs = gdal.Open(fname, GA_ReadOnly)
        # get image size
        self.rows = self.inDs.RasterYSize
        self.cols = self.inDs.RasterXSize
        self.bands = self.inDs.RasterCount
        self.inBand = self.inDs.GetRasterBand(1)
        blockSizes = self.inBand.GetBlockSize()
        self.xBlockSize, self.yBlockSize = blockSizes
        if any(array(blockSizes) == 1):
            self.xBlockSize = self.yBlockSize = self.displaySize / 2
        self.xOffsets = range(0, self.cols, self.xBlockSize)
        self.yOffsets = range(0, self.rows, self.yBlockSize)
        self.xInd = len(self.xOffsets) // 2
        self.yInd = len(self.yOffsets) // 2
        print self.xInd
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
    
    def updateFigure(self):
        self.im.set_data(self.data)
        self.ax.set_title(' '.join([str(self.xInd * self.displaySize),
                                    str(self.yInd * self.displaySize)]))
        plt.draw()
        

    def up(self, event):
        self.yInd -= self.overlap
        self.yInd = max(self.yInd, 0)
        self.read_data()
        self.updateFigure()


    def down(self, event):
        self.yInd += self.overlap
        self.yInd = min(self.yInd, len(self.yOffsets) - 1)
        if self.yOffsets[self.yInd] + self.displaySize < self.rows:
            numRows = self.displaySize
        else:
            numRows = self.rows - self.yOffsets[self.yInd]
        self.read_data(rows=numRows)
        self.updateFigure()
        
    def next(self, event):
        self.xInd += self.overlap
        self.xInd = min(self.xInd, len(self.xOffsets) - 1)
        if self.xOffsets[self.xInd] + self.displaySize < self.cols:
            numCols = self.displaySize
        else:
            numCols = self.cols - self.xOffsets[self.xInd]
        self.read_data(cols=numCols)
        self.updateFigure()

    def prev(self, event):
        self.xInd -= self.overlap
        self.xInd = max(self.xInd, 0)
        self.read_data()
        self.updateFigure()

def main():
    
    opts = [('mosaic cubes', '.mos.cub'),
            ('all cubes', '.cub'),
            ('PDS no label', '.img'),
            ('PDS w/ label', '.lbl'),
            ('All files', '.*')]

    if sys.platform == 'darwin':
        options = {}
        options['filetypes'] = opts
        fname = fd.askopenfilename(initialdir='/Users/aye/Data/mola', **options)
#        fname = '/Users/aye/Data/hirise/PSP_003092_0985/PSP_003092_0985_RED.cal.norm.map.equ.mos.cub'
    else:
        options = {}
        options['filetypes'] = opts
        fname = fd.askopenfilename(initialdir='/processed_data', **options)
    
    callback = Cube(fname)
    
    callback.fig = plt.figure()
    callback.ax = callback.fig.add_subplot(111)
    callback.fig.subplots_adjust(bottom=0.2)
    
    callback.im = callback.ax.imshow(callback.data)
    
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
    
    fig2 = figure()
    small = rebin(callback.data, (512, 512))
    imshow(small)

    LS = RectangleSelector(callback.ax, line_select_callback,
                   drawtype='box', useblit=True,
                   minspanx=5, minspany=5, spancoords='pixels')
    
    plt.show()

if __name__ == '__main__':
    main()

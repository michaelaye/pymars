'''
Created on Aug 16, 2009

@author: aye
'''
from gdal_imports import *
from matplotlib.widgets import Button
from cube_loader import *


def rebin_factor(a, factor):
        '''Rebin an array to a new shape.
        factor is the decrease-factor. So factor = 3 will reduce shape by 3.
        '''
        assert len(a.shape) == len(newshape)
        assert not sometrue(mod(a.shape, newshape))

        slices = [ slice(None, None, old / new) for old, new in zip(a.shape, newshape) ]
        return a[slices]
    
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

fname = '/Users/aye/Data/hirise/PSP_003092_0985_RED.cal.norm.map.equ.mos.cub'

callback = Cube(fname)

ax = plt.subplot(111)
plt.subplots_adjust(bottom=0.2)
im = plt.imshow(callback.data)

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


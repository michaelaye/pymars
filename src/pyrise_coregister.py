#!/usr/bin/python

from gdal_imports import *
#import matplotlib
#matplotlib.use('WxAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import matplotlib.cm as cm
import os.path

class Coreg:
    def __init__(self, fname1, fname2, resultTuple):
    
        xOff = 6849
        xEnd = 7826
        yOff = 18426
        yEnd = 18957
        
        xSize = xEnd - xOff
        ySize = yEnd - yOff
    
        xOff2 = 7443
        yOff2 = 19801
        inDs1 = gdal.Open(fname1, GA_ReadOnly)
        inDs2 = gdal.Open(fname2, GA_ReadOnly)
        inBand1 = inDs1.GetRasterBand(1)
        inBand2 = inDs2.GetRasterBand(1)
        data1 = inBand1.ReadAsArray(xOff, yOff, xSize, ySize)
        try:
            data2 = inBand2.ReadAsArray(xOff2, yOff2, xSize, ySize)
        except ValueError:
            print('probably out of range..')
    
        data1[np.where(data1 < 0)] = np.NaN
        data2[np.where(data2 < 0)] = np.NaN

        fig = plt.figure()
        ax = fig.add_subplot(111)
        fig.subplots_adjust(bottom=0.2)
        
        im1 = ax.imshow(data1, cmap=cm.gray)
        im2 = ax.imshow(data2, alpha=0.5)
        
        axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
        axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
        axup = plt.axes([0.59, 0.05, 0.1, 0.075])
        axdown = plt.axes([0.48, 0.05, 0.1, 0.075])
        axdone = plt.axes([0.30, 0.05, 0.1, 0.075])
        bnext = Button(axnext, 'Next')
        bnext.on_clicked(self.next)
        bprev = Button(axprev, 'Previous')
        bprev.on_clicked(self.prev)
        bup = Button(axup, 'Up')
        bup.on_clicked(self.up)
        bdown = Button(axdown, 'Down')
        bdown.on_clicked(self.down)
        bdone = Button(axdone, 'Done')
        bdone.on_clicked(self.done)
    
        # save objects and variables for later
        self.fig = fig
        self.ax = ax
        self.im1 = im1
        self.im2 = im2
        self.xOff2 = xOff2
        self.yOff2 = yOff2
        self.xSize = xSize
        self.ySize = ySize
        self.inBand2 = inBand2
        self.xOff2Old = xOff2
        self.yOff2Old = yOff2
        self.result = resultTuple
        
        plt.show()

    def read_data(self):
        return self.inBand2.ReadAsArray(self.xOff2,
                                            self.yOff2,
                                            self.xSize,
                                            self.ySize)
        
    def done(self, event):
        print self.xOff2, self.yOff2
        self.result = (self.xOff2, self.yOff2)
        plt.close(self.fig)
    
    def up(self, event):
        self.yOff2 += 1
        self.im2.set_data(self.read_data())
        self.ax.set_title('deltaX: {0}, deltaY: {1}'.format(self.xOff2 - self.xOff2Old,
                                                             self.yOff2 - self.yOff2Old))
        self.fig.canvas.draw()
        
    def down(self, event):
        self.yOff2 -= 1
        self.im2.set_data(self.read_data())
        self.ax.set_title('deltaX: {0}, deltaY: {1}'.format(self.xOff2 - self.xOff2Old,
                                                             self.yOff2 - self.yOff2Old))
        self.fig.canvas.draw()
        
    def next(self, event):
        self.xOff2 -= 1
        self.im2.set_data(self.read_data())
        self.ax.set_title('deltaX: {0}, deltaY: {1}'.format(self.xOff2 - self.xOff2Old,
                                                             self.yOff2 - self.yOff2Old))
        self.fig.canvas.draw()

    def prev(self, event):
        self.xOff2 += 1
        self.im2.set_data(self.read_data())
        self.ax.set_title('deltaX: {0}, deltaY: {1}'.format(self.xOff2 - self.xOff2Old,
                                                             self.yOff2 - self.yOff2Old))
        self.fig.canvas.draw()


if __name__ == '__main__':
    #basefolder = 'processed_data'
    basefolder = '/Users/aye/Data/hirise'
    fname1 = os.path.join(basefolder, 'PSP_003092_0985/PSP_003092_0985_RED.cal.norm.map.equ.mos.cub')
    fname2 = os.path.join(basefolder, 'PSP_003158_0985/PSP_003158_0985_RED.cal.norm.map.equ.mos.cub')

    result = 0
    callback = Coreg(fname1, fname2, result)
    print 'now here', callback.result

#!/usr/bin/python

from gdal_imports import *
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons
import matplotlib.cm as cm
import os.path
import pickle
import sys
import roi

class CoordFinder_Results:
    def __init__(self, inputFile=None):
        self.obsFileNames = []
        self.xOffSets = []
        self.yOffSets = []
        self.CCDCol = []
        self.obsID = []
        if inputFile:
            self.read_file(inputFile)

    def parse_line(self, line):
        fname, xOff, yOff = line.split()
        bname = os.path.basename(fname)
        obsID_col, exts = bname.split('.')[:2]
        obsID, colour = obsID_col[:15], obsID_col[16:]
        if colour != 'RED':
            return
        self.obsFileNames.append(fname)
        self.xOffSets.append(int(xOff))
        self.yOffSets.append(int(yOff))
        self.CCDCol.append(colour)
        self.obsID.append(obsID)

    def read_file(self, fname):
        f = open(fname, 'r')
        for line in f:
            self.parse_line(line)
        f.close()


class SubFrame:
    def __init__(self, fname, x1, y1, xSize, ySize):
        self.fname = fname
        self.x1 = x1
        self.x2 = x1 + xSize
        self.y1 = y1
        self.y2 = y1 + xSize
        self.xSize = xSize
        self.ySize = ySize
        self.obsID = os.path.basename(fname).split('.')[0]
        self.coregX = 0
        self.coregY = 0
        self.d = {self.obsID: [self.fname,
                               self.x1, self, y1, self.xSize, self.ySize,
                               self.coregX, self.coregY]}


class Coreg:
    def __init__(self, sub1, sub2):

        fname1 = sub1.fname
        fname2 = sub2.fname
        xOff = sub1.x1
        xSize = sub1.xSize
        yOff = sub1.y1
        ySize = sub1.ySize
        xOff2 = sub2.x1
        yOff2 = sub2.y1

        inDs1 = gdal.Open(fname1, GA_ReadOnly)
        inDs2 = gdal.Open(fname2, GA_ReadOnly)
        inBand1 = inDs1.GetRasterBand(1)
        inBand2 = inDs2.GetRasterBand(1)
        data1 = inBand1.ReadAsArray(xOff, yOff, xSize, ySize)
        try:
            data2 = inBand2.ReadAsArray(xOff2, yOff2, xSize, ySize)
        except ValueError:
            print('probably out of range..')
            raise ValueError('out of range')

        data1[np.where(data1 < 0)] = np.NaN
        data2[np.where(data2 < 0)] = np.NaN

        fig = plt.figure()
        ax = fig.add_subplot(111)
        fig.subplots_adjust(bottom=0.2)

        im1 = ax.imshow(data1, cmap=cm.gray)
        im2 = ax.imshow(data2, alpha=0.5)

        axcolor = 'lightgoldenrodyellow'
        rax = plt.axes([0.05, 0.05, 0.15, 0.15], axisbg=axcolor)
        radio = RadioButtons(rax, ('x1', 'x5', 'x10'))
        radio.on_clicked(self.set_multiplier)
        axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
        axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
        axup = plt.axes([0.59, 0.05, 0.1, 0.075])
        axdown = plt.axes([0.48, 0.05, 0.1, 0.075])
        axdone = plt.axes([0.30, 0.05, 0.1, 0.075])
        bnext = Button(axnext, 'Right')
        bnext.on_clicked(self.next)
        bprev = Button(axprev, 'Left')
        bprev.on_clicked(self.prev)
        bup = Button(axup, 'Up')
        bup.on_clicked(self.up)
        bdown = Button(axdown, 'Down')
        bdown.on_clicked(self.down)
        bdone = Button(axdone, 'Done')
        bdone.on_clicked(self.done)

        fig2 = plt.figure()
        ax2 = fig2.add_subplot(211)
        ax2.imshow(data1)
        ax3 = fig2.add_subplot(212)
        ax3.imshow(data2)

        # save objects and variables for later
        self.fig = fig
        self.fig2 = fig2
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
        self.sub2 = sub2
        self.multiplier = 1

        plt.show()

    def set_multiplier(self, label):
        multiDict = {'x1':1, 'x5':5, 'x10':10}
        self.multiplier = multiDict[label]

    def read_data(self):
        return self.inBand2.ReadAsArray(self.xOff2,
                                            self.yOff2,
                                            self.xSize,
                                            self.ySize)

    def done(self, event):
        self.sub2.coregX, self.sub2.coregY = (self.xOff2 - self.xOff2Old,
                                              self.yOff2 - self.yOff2Old)

        plt.close(self.fig)
        plt.close(self.fig2)

    def up(self, event):
        self.yOff2 += 1 * self.multiplier
        self.im2.set_data(self.read_data())
        self.ax.set_title('{2}, deltaX: {0}, deltaY: {1}'.format(self.xOff2 - self.xOff2Old,
                                                             self.yOff2 - self.yOff2Old,
                                                             self.sub2.obsID))
        self.fig.canvas.draw()

    def down(self, event):
        self.yOff2 -= 1 * self.multiplier
        self.im2.set_data(self.read_data())
        self.ax.set_title('{2}, deltaX: {0}, deltaY: {1}'.format(self.xOff2 - self.xOff2Old,
                                                             self.yOff2 - self.yOff2Old,
                                                             self.sub2.obsID))
        self.fig.canvas.draw()

    def next(self, event):
        self.xOff2 -= 1 * self.multiplier
        self.im2.set_data(self.read_data())
        self.ax.set_title('{2}, deltaX: {0}, deltaY: {1}'.format(self.xOff2 - self.xOff2Old,
                                                             self.yOff2 - self.yOff2Old,
                                                             self.sub2.obsID))
        self.fig.canvas.draw()

    def prev(self, event):
        self.xOff2 += 1 * self.multiplier
        self.im2.set_data(self.read_data())
        self.ax.set_title('{2}, deltaX: {0}, deltaY: {1}'.\
                          format(self.xOff2 - self.xOff2Old,
                                 self.yOff2 - self.yOff2Old,
                                 self.sub2.obsID))
        self.fig.canvas.draw()


if __name__ == '__main__':
    import sys

    #basefolder = '/processed_data'
    basefolder = '/Users/aye/Data/hirise'
    fname1 = os.path.join(basefolder,
                          'PSP_003092_0985/\
                           PSP_003092_0985_RED.cal.norm.map.equ.mos.cub')
    fname2 = os.path.join(basefolder,
                          'PSP_003158_0985/\
                           PSP_003158_0985_RED.cal.norm.map.equ.mos.cub')

    args = sys.argv
    try:
        finder_output_file = args[1]
    except IndexError:
        print "Usage: {0} finder_output_file".format(args[0])
        sys.exit(1)

#    xSize = 977
#    ySize = 531
#    mainX = 6849 
#    mainY = 18426
    roidata = roi.ROI_Data()
    roidata.read_in(finder_output_file)

    for i, obsID in enumerate(sorted(roidata.dict.keys())):
        print i + 1, obsID

    fixed = raw_input('Number of obsID for reference: ')
    tobeShifted = raw_input('Number of obsID to be shifted (=co-registered): ')

    for i, pos in enumerate([fixed, tobeShifted]):
        inputLine = infile[int(pos) - 1].rstrip('\n')
        fname, centerX, centerY = inputLine.split()
        xOff = int(centerX) - samples / 2
        yOff = int(centerY) - lines / 2
        if i == 0:
            fixedSub = SubFrame(fname, xOff, yOff, samples, lines)
        else:
            shiftSub = SubFrame(fname, xOff, yOff, samples, lines)

    xSize = samples
    ySize = lines

    try:
        callback = Coreg(fixedSub, shiftSub)
    except ValueError:
        print 'out of range'
    print 'Total Offset for {0} with respect to {1}:\n {2} samples \n {3} lines'\
        .format(shiftSub.obsID, fixedSub.obsID, shiftSub.coregX, shiftSub.coregY)
    shiftList = [shiftSub.fname, shiftSub.obsID,
                 shiftSub.x1, shiftSub.y1, shiftSub.xSize, shiftSub.ySize,
                 shiftSub.coregX, shiftSub.coregY]

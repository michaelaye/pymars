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
import hirise_tools


class SubFrame:
    def __init__(self, fname, x1, y1, xSize, ySize):
        self.fname = fname
        self.x1 = x1
        self.x2 = x1 + xSize
        self.y1 = y1
        self.y2 = y1 + xSize
        self.xSize = xSize
        self.ySize = ySize
        self.obsID = hirise_tools.getObsIDFromPath(fname)
        self.coregX = 0
        self.coregY = 0
        self.d = {self.obsID: [self.fname,
                               self.x1, self, y1, self.xSize, self.ySize,
                               self.coregX, self.coregY]}


class Coreg:
    def __init__(self, sub1, subframes):

        self.sub1 = sub1
        self.subframes = subframes
        self.sub2iter = self.get_next_subframe()

        fname1 = sub1.fname
        xOff = sub1.x1
        xSize = sub1.xSize
        yOff = sub1.y1
        ySize = sub1.ySize
        self.xSize = xSize
        self.ySize = ySize

        inDs1 = gdal.Open(fname1, GA_ReadOnly)
        inBand1 = inDs1.GetRasterBand(1)
        data1 = inBand1.ReadAsArray(xOff, yOff, xSize, ySize)
        data1[np.where(data1 < 0)] = np.NaN

        self.sub2 = self.sub2iter.next()
        data2 = self.get_data2()
#==============================================================================
# coreg window
#==============================================================================
        fig = plt.figure()
        ax = fig.add_subplot(111)
        fig.subplots_adjust(bottom=0.2)

        im1 = ax.imshow(data1, cmap=cm.gray)
        im2 = ax.imshow(data2, alpha=0.5)

        ax.set_title(sub1.obsID + ' vs ' + self.sub2.obsID)
        self.make_buttons()

#==============================================================================
# overview window
#==============================================================================
        fig2 = plt.figure()
        ax2 = fig2.add_subplot(211)
        ax2.imshow(data1)
        ax3 = fig2.add_subplot(212)
        ax3.imshow(data2)

#==============================================================================
# save objects and variables for later
#==============================================================================
        self.fig = fig
        self.fig2 = fig2
        self.ax = ax
        self.ax2 = ax2
        self.ax3 = ax3
        self.multiplier = 1
        self.im1 = im1
        self.im2 = im2
        self.data1 = data1

        plt.show()

    def get_data2(self):
        sub2 = self.sub2
        fname2 = sub2.fname
        xOff2 = sub2.x1
        yOff2 = sub2.y1
        inDs2 = gdal.Open(fname2, GA_ReadOnly)
        inBand2 = inDs2.GetRasterBand(1)
        try:
            data2 = inBand2.ReadAsArray(xOff2, yOff2, self.xSize, self.ySize)
        except ValueError:
            print('probably out of range..')
            raise ValueError('out of range')
        data2[np.where(data2 < 0)] = np.NaN
        self.xOff2 = xOff2
        self.yOff2 = yOff2
        self.inBand2 = inBand2
        self.xOff2Old = xOff2
        self.yOff2Old = yOff2
        self.data2 = data2
        self.sub2 = sub2
        self.inDs2 = inDs2
        return data2

    def get_next_subframe(self):
            for subframe in self.subframes:
                yield subframe

    def make_buttons(self):
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

    def set_multiplier(self, label):
        multiDict = {'x1':1, 'x5':5, 'x10':10}
        self.multiplier = multiDict[label]

    def read_data(self):
        self.inBand2 = self.inDs2.GetRasterBand(1)
        return self.inBand2.ReadAsArray(self.xOff2,
                                            self.yOff2,
                                            self.xSize,
                                            self.ySize)

    def done(self, event):
        self.sub2.coregX, self.sub2.coregY = (self.xOff2 - self.xOff2Old,
                                              self.yOff2 - self.yOff2Old)
        print 'Sample Offset for {0}: {1}'.format(self.sub2.obsID,
                                                  self.sub2.coregX)
        print 'Line Offset for {0}: {1}'.format(self.sub2.obsID,
                                                  self.sub2.coregY)

        try:
            self.sub2 = self.sub2iter.next()
        except StopIteration:
            self.end()
        else:
            data2 = self.get_data2()
            self.ax.cla()
            self.im1 = self.ax.imshow(self.data1, cmap=cm.gray)
            self.im2 = self.ax.imshow(data2, alpha=0.5)
            self.ax.set_title(self.sub1.obsID + ' vs ' + self.sub2.obsID)
            self.fig.canvas.draw()
            self.ax3.cla()
            self.ax3.imshow(data2)
            self.fig2.canvas.draw()

    def end(self):
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

def get_subframe_from_roidata(roidata, obsID):
    indict = roidata.dict[obsID]
    ccd = indict['CCDColour']
    fname = hirise_tools.getMosPathFromIDandCCD(obsID, ccd)
    centerX = int(indict['Map_Sample_Offset'])
    centerY = int(indict['Map_Line_Offset'])
    samples = int(indict['NSAMPLES'])
    lines = int(indict ['NLINES'])
    xOff = int(centerX) - samples / 2
    yOff = int(centerY) - lines / 2
    return SubFrame(fname, xOff, yOff, samples, lines)


if __name__ == '__main__':
    import sys

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

    sKeys = sorted(roidata.dict.keys())
    for i, obsID in enumerate(sKeys):
        print i + 1, obsID

    fixed = raw_input('Number of obsID to be used as reference: ')
    tobeShifted = raw_input("""Number of obsID to be shifted (=co-registered)
    or type 0 (=zero) for all: """)

    fixed = int(fixed) - 1 # for human display i added 1 in line 232
    tobeShifted = int(tobeShifted) - 1

    fixedObsID = sKeys[fixed]
    fixedSub = get_subframe_from_roidata(roidata, fixedObsID)
    roidata.dict[fixedObsID]['CoReg_Sample_Offset'] = 0
    roidata.dict[fixedObsID]['CoReg_Line_Offset'] = 0

    targets = []
    if not tobeShifted == -1:
        targets.append(tobeShifted)
    else:
        targets = range(len(roidata.dict))
        targets.remove(fixed) # fixed was defined as human readable

    shiftSubFrames = []
    for target in targets:
        inputObsID = sKeys[target] # no -1 here b/c targets were created from 0
        shiftSub = get_subframe_from_roidata(roidata, inputObsID)
        shiftSubFrames.append(shiftSub)

    callback = Coreg(fixedSub, shiftSubFrames)

    for shiftSub in shiftSubFrames:
        print 'Total Offset for {0} with respect to {1}:\n {2} samples \n {3} lines'\
            .format(shiftSub.obsID, fixedSub.obsID, shiftSub.coregX, shiftSub.coregY)
        roidata.dict[shiftSub.obsID]['CoReg_Sample_Offset'] = shiftSub.coregX
        roidata.dict[shiftSub.obsID]['CoReg_Line_Offset'] = shiftSub.coregY

    roidata.write_out()

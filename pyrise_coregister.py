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
        self.ax.set_title('{2}, deltaX: {0}, deltaY: {1}'.format(self.xOff2 - self.xOff2Old,
                                                             self.yOff2 - self.yOff2Old,
                                                             self.sub2.obsID))
        self.fig.canvas.draw()


if __name__ == '__main__':    
    basefolder = '/processed_data'
    #basefolder = '/Users/aye/Data/hirise'
    fname1 = os.path.join(basefolder, 'PSP_003092_0985/PSP_003092_0985_RED.cal.norm.map.equ.mos.cub')
    fname2 = os.path.join(basefolder, 'PSP_003158_0985/PSP_003158_0985_RED.cal.norm.map.equ.mos.cub')
    pfile = open('subframes.pkl', 'r+')
    
    fixed_obsID = 'PSP_003092_0985'
    
    # index is the next to be coreg'ed position in coords results
    
    bigList, index = pickle.load(pfile)
    print "currently stored: {0} subframes,"\
            " index at {1}".format(len(bigList), index)
            
    # put filepointer to beginning again to overwrite old value later
    pfile.seek(0)
    
    xSize = 977
    ySize = 531
    mainX = 6849 
    mainY = 18426
    fixedList = [fname1, fixed_obsID, mainX, mainY, xSize, ySize, 0, 0]
    
    # coreg values are set at instantiation to 0
    fixedSub = SubFrame(fname1, mainX, mainY, xSize, ySize)
    if len(bigList) == 0:
        print "Storing fixed frame"
        bigList.append(fixedList)


    infile = 'Coordinates_PSP_lat_-81.386_lon_295.667.txt'
    # file is filtered for REDs only in instantiation of CoordFinder_Results
    coords = CoordFinder_Results(infile)
    toDo_obsID = coords.obsID[index]
    if toDo_obsID == fixed_obsID:
        print 'same as fixed. Skipping'
        pickle.dump((bigList, index + 1), pfile)
        sys.exit()
    if index > len(coords.obsID):
        print 'all done'
        sys.exit()
        
    fname2 = coords.obsFileNames[index]
    xOff = coords.xOffSets[index]
    yOff = coords.yOffSets[index]
    if any([xOff < 0, yOff < 0]):
        print 'negative offset found'
        pickle.dump((bigList, index + 1), pfile)
        pfile.close()
        sys.exit()
    shiftSub = SubFrame(fname2, xOff, yOff, xSize, ySize)
    try:
        callback = Coreg(fixedSub, shiftSub)
    except ValueError:
        print 'out of range'
        pickle.dump((bigList, index + 1), pfile)
        pfile.close()
        sys.exit()
    print 'Total Offset: ', shiftSub.coregX, shiftSub.coregY
    shiftList = [shiftSub.fname, shiftSub.obsID,
                 shiftSub.x1, shiftSub.y1, shiftSub.xSize, shiftSub.ySize,
                 shiftSub.coregX, shiftSub.coregY]
    bigList.append(shiftList)
    pickle.dump((bigList, index + 1), pfile)
    pfile.close()

'''
Created on Aug 16, 2009

@author: aye
'''
from gdal_imports import *

#import wx

def onpick(event):
    global index
    if index < len(xOffSets)-2:
        index +=1
        xOff = int(xOffSets[index])
        yOff = int(yOffSets[index])
        arr = cube.ReadAsArray( xOff, yOff, xSize, ySize )
        print 'min, max, mean: ',arr.min(), arr.max(), arr.mean()
        ax.imshow(arr, cmap = matplotlib.cm.gray)
        ax.set_title("{0},{1}, index {2}".format(xOff,yOff,index))
        fig.canvas.draw()

def format_coord(x, y):
    col = int(x+0.5)
    row = int(y+0.5)
    if col>=0 and col<numcols and row>=0 and row<numrows:
        z = arr[row,col]
        return 'x=%1.4f, y=%1.4f, z=%1.4f'%(x, y, z)
    else:
        return 'x=%1.4f, y=%1.4f'%(x, y)


#app = wx.App(redirect=False)
#dlg = wx.FileDialog(None, 
#                    message="Choose a file to open",
#                    defaultDir = '/Users/aye/Desktop/cut_jpeg2000/')
#
#retCode = dlg.ShowModal()
#if retCode == wx.ID_OK:
#    paths = dlg.GetPaths()
#    fName = paths[0]
#elif retCode == wx.ID_CANCEL: 
#    print 'canceled file dialog. exiting'
#    sys.exit(-1)
#else: 
#    print 'unknown error. exiting'
#    sys.exit(-1)

fName = '/Users/aye/Desktop/cut_jpeg2000/test.jp2'
cube = gdal.Open(str(fName), GA_ReadOnly )
print "have gdal.Open done"

# size of the part i want to read out
size = 400

xTotal = cube.RasterXSize
yTotal = cube.RasterYSize

xSize = xTotal / 10
ySize = yTotal / 10

print xSize,ySize
print "image size:",xTotal, yTotal
xOffSets = Numeric.linspace(0,xTotal,11)
yOffSets = Numeric.linspace(0,yTotal,11)
print xOffSets
print yOffSets

#xOff = xSize/2 - size/2 -1
#yOff = ySize/2 - size/2 -1
index = 0
fig = plt.figure()
ax = fig.add_subplot(111)
xOff = int(xOffSets[index])
yOff = int(yOffSets[index])
ax.set_title("{0},{1}, index {2}".format(xOff,yOff,index))
arr = cube.ReadAsArray(xOff, yOff, xSize, ySize)
ax.imshow(arr, cmap = matplotlib.cm.gray, picker=True)
numrows, numcols = arr.shape
ax.format_coord = format_coord
fig.canvas.mpl_connect('pick_event', onpick)
plt.show()

'''
Created on Aug 16, 2009

@author: aye
'''
from gdal_imports import *

fName = '/Users/aye/Desktop/cut_jpeg2000/test.jp2'
cube = gdal.Open(str(fName), GA_ReadOnly )
print "have gdal.Open done"

# size of the part i want to read out
size = 400

xTotal = cube.RasterXSize
yTotal = cube.RasterYSize

xSize = xTotal / 10
ySize = yTotal / 10


#xOff = xSize/2 - size/2 -1
#yOff = ySize/2 - size/2 -1
#ax = fig.add_subplot(111)
index = 0
arr = cube.ReadAsArray(1,1,xSize, ySize)
print 'read array'
print arr.max()
print arr.min()
fig = plt.figure()
ax = fig.add_subplot(111)
im = ax.imshow(arr)
print 'imshowed arr'
plt.show()
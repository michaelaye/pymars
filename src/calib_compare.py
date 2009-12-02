#!/usr/bin/python

from gdal_imports import *
#try:
#    fname = fd.askopenfilename(initialdir='/processed_data/maye')
#except:
#    fname = fd.askopenfilename()
#fname = '/processed_data/maye/PSP_003092_0985/PSP_003092_0985_RED5.calOld.map.cub'
fname = '/Users/aye/Desktop/cut_jpeg2000/test.jp2'
    
cube = gdal.Open(str(fname), GA_ReadOnly )

print cube.GetDescription()

try:
    size = int(sys.argv[1])
except:
    size = 300

xSize = cube.RasterXSize
ySize = cube.RasterYSize

print "Cube is {0} pixels in X and {1} pixels in Y".format(xSize, ySize)
xOff = xSize/2  - size/2 -1 - 300
yOff = ySize/2 - size/2 -1 - 300

print "reading a {0} sized array at {1},{2} offset".format(size,xOff,yOff)
arr = cube.ReadAsArray(xOff, yOff, size, size)

print "minimum of array: ", arr.min()

#arr[Numeric.where(arr < 0.0)] = Numeric.nan

print "minimum of array: ", arr.min()

fig = plt.figure()
ax = fig.add_subplot(111)
p = ax.patch
p.set_facecolor('black')
cax = ax.imshow(arr, interpolation = 'nearest') 
plt.grid(True)
cbar = fig.colorbar(cax)
numrows, numcols = arr.shape
def format_coord(x, y):
    col = int(x+0.5)
    row = int(y+0.5)
    if col>=0 and col<numcols and row>=0 and row<numrows:
        z = arr[row,col]
        return 'x=%1.4f, y=%1.4f, z=%1.4f'%(x, y, z)
    else:
        return 'x=%1.4f, y=%1.4f'%(x, y)

ax.format_coord = format_coord
plt.show()

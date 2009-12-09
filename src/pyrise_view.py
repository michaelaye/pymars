#!/usr/bin/python

from gdal_imports import *
import tkFileDialog as fd
import matplotlib.pyplot as plt

def main():    
    try:
        fname = fd.askopenfilename(initialdir='/processed_data/maye')
    except:
        fname = fd.askopenfilename()
        
    cube = gdal.Open(fname, GA_ReadOnly)
    
    print cube.GetDescription()
    
    try:
        size = int(sys.argv[1])
    except:
        size = 300
    
    xSize = cube.RasterXSize
    ySize = cube.RasterYSize
    
    print "Cube is {0} pixels in X and {1} pixels in Y".format(xSize, ySize)
    xOff = xSize / 2 - size / 2 - 1
    yOff = ySize / 2 - size / 2 - 1
    
    print "reading a {0} sized array at center coordinates {1},{2} offset".format(size, xOff, yOff)
    arr = cube.ReadAsArray(xOff, yOff, size, size)
    
    print "minimum of array: ", arr.min()
    
    arr[np.where(arr < 0.0)] = np.nan
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    p = ax.patch
    p.set_facecolor('black')
    cax = ax.imshow(arr, interpolation='nearest') 
    plt.grid(True)
    cbar = fig.colorbar(cax)
    numrows, numcols = arr.shape
    def format_coord(x, y):
        """ this function is required to show the pixel value with the mouse.
        function needs to be here, because it requires globals numrows and numcols."""
        col = int(x + 0.5)
        row = int(y + 0.5)
        if col >= 0 and col < numcols and row >= 0 and row < numrows:
            z = arr[row, col]
            return 'x=%1.4f, y=%1.4f, z=%1.4f   ' % (x, y, z)
        else:
            return 'x=%1.4f, y=%1.4f' % (x, y)
    
    ax.format_coord = format_coord
    plt.show()


if __name__ == '__main__':
    main()

#!/usr/bin/env python

#from matplotlib.widgets import RectangleSelector
#from pylab import subplot, arange, plot, sin, cos, pi, show
#def line_select_callback(event1, event2):
#    'event1 and event2 are the press and release events'
#    x1, y1 = event1.xdata, event1.ydata
#    x2, y2 = event2.xdata, event2.ydata
#    print "(%3.2f, %3.2f) --> (%3.2f, %3.2f)"%(x1,y1,x2,y2)
#    print " The button you used were: ",event1.button, event2.button
#
#
#current_ax=subplot(111)                    # make a new plotingrange
#N=100000                                   # If N is large one can see improvement
#x=10.0*arange(N)/(N-1)                     # by use blitting!
#
#plot(x,sin(.2*pi*x),lw=3,c='b',alpha=.7)   # plot something
#plot(x,cos(.2*pi*x),lw=3.5,c='r',alpha=.5)
#plot(x,-sin(.2*pi*x),lw=3.5,c='g',alpha=.3)
#
#print "\n      click  -->  release"
#
## drawtype is 'box' or 'line' or 'none'
#LS = RectangleSelector(current_ax, line_select_callback,
#                       drawtype='box',useblit=True,
#                       minspanx=5,minspany=5,spancoords='pixels')


from osgeo import gdal
# import tkFileDialog as fd
import matplotlib.pyplot as plt

def main():
    # try:
    #     fname = fd.askopenfilename(initialdir='/processed_data/maye')
    # except:
    #     fname = fd.askopenfilename()

    fname = '/Users/aye/Data/hirise/PSP_002622_0945_RED.JP2'
    cube = gdal.Open(fname)
    
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
    arr = cube.ReadAsArray(int(xOff), int(yOff), size, size)
    
    # print "minimum of array: ", arr.min()
    
    # arr[np.where(arr < 0.0)] = np.nan
    
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

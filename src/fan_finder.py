#!/usr/bin/python

from gdal_imports import *
import matplotlib.colors as colors
import scipy.ndimage as nd
import numpy as np

#from scipy import optimize
#from numpy import *


class Parameter:
    def __init__(self, value):
            self.value = value

    def set(self, value):
            self.value = value

    def __call__(self):
            return self.value

def fit(function, parameters, y, x = None):
    print "entered fit function"
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x)

    if x is None: x = arange(y.shape[0])
    p = [param() for param in parameters]
    return optimize.leastsq(f, p)


# giving initial parameters
mu = Parameter(7)
sigma = Parameter(3)
height = Parameter(5)

# define your function:
def f(x): return height() * exp(-((x-mu())/sigma())**2)

fname = '/Users/aye/Data/hirise/PSP_003092_0985_RED.cal.norm.map.equ.mos.cub'
    
cube = gdal.Open(fname, GA_ReadOnly )

print cube.GetDescription()


xOff = 6849
xEnd = 7826
yOff = 18426
yEnd = 18957

xSize = xEnd - xOff
ySize = yEnd - yOff

print "reading {0} at {1},{2} offset".format(fname,xOff,yOff)
arr_big = cube.ReadAsArray(xOff, yOff, xSize, ySize)

print "minimum of array: ", arr_big.min()
arr_big[Numeric.where(arr_big < 0.0)] = Numeric.nan
print "minimum of array after NaN determination: ", arr_big.min()

arr = arr_big[:200,:200]


fig1 = plt.figure(1)
ax1 = fig1.add_subplot(111)
#ax1.set_yscale('log')
pdf, bins, patches = ax1.hist(arr_big.reshape(arr_big.size), 30, color='g')
plt.xlabel('I/F')
maxpos = pdf.argmax()
print "most frequent I/F value: ",bins[maxpos]

fig2 = plt.figure(2)
ax2 = fig2.add_subplot(111)
palette = plt.cm.gray
palette.set_under('g',1.0)
palette.set_bad('b',1.0)
palette.set_over('r',1.0)
threshold = 0.065
#arr_masked = plt.ma.masked_where(arr_big < 0.06, arr_big)
arr_masked = plt.ma.masked_where(arr_big < threshold, arr_big)
im = ax2.imshow(arr_masked, cmap=palette,
                norm = colors.Normalize(vmin = arr_big.min(),
                                        vmax = arr_big.max(),
                                        clip = True ))

plt.colorbar(im, shrink=0.7)

arr_bin = plt.where(arr_big < threshold, 1, 0)
struc8 = np.ones((3,3))
labels, n = nd.label(arr_bin, struc8)
slices = nd.find_objects(labels)
print len(slices)
print slices[0]
print slices[1]

print labels[slices[0]]
print arr_bin[slices[0]].sum()
print arr_bin[slices[1]]
print arr_bin[slices[1]].sum()
print arr_bin[slices[2]]
print arr_bin[slices[2]].sum()

plt.figure(2)
plt.title("I/F threshold at {0}, {1} fans found.".format(threshold,n))
for i in range(n):
    y1 = slices[i][0].start
    y2 = slices[i][0].stop
    x1 = slices[i][1].start
    x2 = slices[i][1].stop
    area = arr_bin[slices[i]].sum()*0.25
    x = (x2-x1)/2+x1
    y = (y2-y1)/2+y1
    print x,y
    ax2.annotate(str(i)+'\n'+str(area)+' m^2',xy=(x,y),xycoords='data')

plt.show()


# fit! (given that data is an array with the data to fit)
#pOut, success = fit(f, [mu, sigma, height], data)



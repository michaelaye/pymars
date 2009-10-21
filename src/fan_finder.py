#!/usr/bin/python

from gdal_imports import *
import matplotlib.colors as colors

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


fig = plt.figure()
ax = fig.add_subplot(111)
ax.patch.set_facecolor('black')
cax = ax.imshow(arr_big, cmap= plt.cm.gray, origin='lower') 
cbar = fig.colorbar(cax)

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
ax2.patch.set_facecolor('black')
cax2 = ax2.imshow(arr, origin='lower')
cbar2 = fig2.colorbar(cax2)

fig3 = plt.figure()
data = arr[90,:]
lower = data.mean()-2*data.std()
supper = plt.ma.masked_where(data < lower, data)
slower = plt.ma.masked_where(data > lower, data)
plt.plot(slower, 'r', supper, 'b')

fig4 = plt.figure()
pdf, bins, patches = plt.hist(arr_big.reshape(arr_big.size), 30, normed=1)
maxpos = pdf.argmax()
print bins[maxpos]

fig5 = plt.figure()
palette = plt.cm.gray
palette.set_under('g',1.0)
palette.set_bad('b',1.0)
palette.set_over('r',1.0)
arr_masked = plt.ma.masked_where(arr_big < 0.06, arr_big)
im = plt.imshow(arr_masked, cmap=palette,
                origin = 'lower',
                norm = colors.Normalize(vmin = arr_big.min(),
                                        vmax = arr_big.max(),
                                        clip = True ))

print
plt.colorbar(im)
plt.show()


# fit! (given that data is an array with the data to fit)
#pOut, success = fit(f, [mu, sigma, height], data)



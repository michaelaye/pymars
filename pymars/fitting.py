'''
Created on Sep 18, 2010

@author: aye
'''

from pylab import *
from scipy import optimize, randn

class Parameter:
    def __init__(self, value):
            self.value = value

    def set(self, value):
            self.value = value

    def __call__(self):
            return self.value

def fit(function, parameters, y, x=None):
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x)

    if x is None: x = arange(y.shape[0])
    p = [param() for param in parameters]
    optimize.leastsq(f, p)
    
figure(1)
#subplot(211)
data1 = randn(1000) + 20
n1, bins1 = histogram(data1, 30)
plot(bins1[:-1], n1)
#subplot(212)
data2 = randn(1000) + 16
n2, bins2 = histogram(data2, 30)
plot(bins2[:-1], n2)
show()
n, bins, patches = hist(data, 30)
fitfunc = lambda p, X: p[0] * exp(-(X - p[1]) ** 2 / 2 * p[2] ** 2)
errfunc = lambda p, X, y: fitfunc(p, X) - y

p_i = [80, 10, 1]
p, success = optimize.leastsq(errfunc, p_i[:], args=(bins[:-1], n))
plot(bins[:-1], fitfunc(p, bins[:-1]), "r-")
print(p)
show()

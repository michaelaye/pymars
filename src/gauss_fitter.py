#!/usr/bin/python


import matplotlib.pylab as plt
from scipy import optimize
import numpy as np

class Parameter:
    def __init__(self, value):
            self.value = value

    def set(self, value):
            self.value = value

    def __call__(self):
            return self.value

def fit(function, parameters, y, x = None):
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x)

    if x is None: x = np.arange(y.shape[0])
    p = [param() for param in parameters]
    optimize.leastsq(f, p)


# giving initial parameters
mu = Parameter(7)
sigma = Parameter(3)
height = Parameter(5)

# define your function:
def f(x): return height() * np.exp(-((x-mu())/sigma())**2)

a = np.arange(100)-50

result = f(a)
plt.plot(result)
plt.show()
# fit! (given that data is an array with the data to fit)
#fit(f, [mu, sigma, height], data)


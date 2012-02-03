import numpy as np
import pprint
#import matplotlib.pyplot as plt

class Column(object):
    def __init__(self, dust, ice=0):
        self.n_dust_lyrs = dust
        self.n_ice_lyrs = ice
        
    def __gt__(self, other ):
        return (self.n_dust_lyrs+self.n_ice_lyrs) > other
    
    
# number of positions to play with
n = 10
# array along x, value indicates thickness of dust layer
dust = np.array([Column(i+1) for i in range(10)])

# distribution manipulation
# dust = dust*3
# dust = np.array(dust**2,dtype='int')

# array of temperatures near ground
temps = np.zeros(n)

# absorbtion parameter 
a = 0.8

# critical temp for removal of dust
T_c = 10

# constant energy input from above
I_above = 100

# epsilon to do floating point comparisons
eps = 0.0001

# latent heat to remove from temps when removing dust
L = 0.5*T_c

while np.any(dust>0):
    # calculate energy on ground layer
    I_ground = np.array([I_above*a**item.n_dust_lyrs for item in dust])
    
    # where is still dust? produces a boolean index array
    dusty = dust > 0
    # add energy that reached ground to ground T array:
    temps[dusty] += I_ground[dusty]
    
    # boolean array to state if T_c is reached
    state = temps > (T_c - eps)
    
    # get arrays of 1s and 0s to subtract from dust layer array
    dust_to_remove = 1 * state
    heat_to_remove = L * state
    # remove dust where T reached T_c
    dust[dusty] -= dust_to_remove[dusty]
    
    # remove heat where dust was removed
    temps -= heat_to_remove
    
    # print 'temps',temps
    for item in dust:
        print item,
    print

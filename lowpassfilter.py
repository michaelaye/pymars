from __future__ import division
from matplotlib.pylab import *

def lowpassfilter(shape, cutoff, n):
    
    if cutoff < 0 or cutoff > 0.5:
		print('cutoff frequency must be between 0 and 0.5')
    
    if n%1 != 0 | n < 1:
		print('n must be an integer >= 1')
    
    rows,cols = shape
    if mod(cols,2):
        range_x = arange(-(cols-1)/2,(cols-1)/2)/(cols-1)
    else:
        range_x = arange(-cols/2,(cols/2-1))/cols 
    
    if mod(rows,2):
        range_y = arange(-(rows-1)/2,(rows-1)/2)/(rows-1)
    else:
        range_y = arange(-rows/2,(rows/2-1))/rows 
    
    x, y = meshgrid(range_x, range_y)
    
    radius = sqrt(x**2 + y**2)       # Matrix values contain *normalised* radius from centre.
    
    #  Alteration, ELEC 301 Project Group, Dec 2001
    #  Original code fftshifted the filter before output.  Since
    #  imFFT and imIFFT already shift, the output should remain low-centered.
    f = 1 / (1.0 + (radius / cutoff)**(2*n))   # The filter
	# End Alteration
    return f
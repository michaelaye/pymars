from matplotlib.pyplot import subplots, imshow,savefig,colorbar,figure
import numpy
from scipy import ndimage
from pymars.fan_finder import get_data
import mahotas

_N  = numpy.array([[0, 1, 0],
                   [0, 0, 0],
                   [0, 1, 0]], dtype=bool)

_NE = numpy.array([[0, 0, 1],
                   [0, 0, 0],
                   [1, 0, 0]], dtype=bool)

_W  = numpy.array([[0, 0, 0],
                   [1, 0, 1],
                   [0, 0, 0]], dtype=bool)

_NW = numpy.array([[1, 0, 0],
                   [0, 0, 0],
                   [0, 0, 1]], dtype=bool)



# After quantizing the angles, vertical (north-south) edges get values of 3,
# northwest-southeast edges get values of 2, and so on, as below:
_NE_d = 0
_W_d = 1
_NW_d = 2
_N_d = 3

data = get_data('PSP_004081_0985')
for i in numpy.arange(20)+1:
	print i
	image = ndimage.median_filter(data,size=i)
	grad_x = ndimage.sobel(image, 0)
	grad_y = ndimage.sobel(image, 1)
	grad_mag = numpy.sqrt(grad_x**2+grad_y**2)
	grad_angle = numpy.arctan2(grad_y, grad_x)
	# next, scale the angles in the range [0, 3] and then round to quantize
	quantized_angle = numpy.around(3 * (grad_angle + numpy.pi) / (numpy.pi * 2))
	# Non-maximal suppression: an edge pixel is only good if its magnitude is
	# greater than its neighbors normal to the edge direction. We quantize
	# edge direction into four angles, so we only need to look at four
	# sets of neighbors
	NE = ndimage.maximum_filter(grad_mag, footprint=_NE)
	W  = ndimage.maximum_filter(grad_mag, footprint=_W)
	NW = ndimage.maximum_filter(grad_mag, footprint=_NW)
	N  = ndimage.maximum_filter(grad_mag, footprint=_N)
	thinned = (((grad_mag > W)  & (quantized_angle == _N_d )) |
				((grad_mag > N)  & (quantized_angle == _W_d )) |
				((grad_mag > NW) & (quantized_angle == _NE_d)) |
				((grad_mag > NE) & (quantized_angle == _NW_d)) )
	thinned_grad = thinned * grad_mag
	thinned_grad = numpy.round(thinned_grad*255/thinned_grad.max())
	thinned_grad = thinned_grad.astype(numpy.uint8)
	high_threshold = mahotas.thresholding.otsu(thinned_grad)
	low_threshold = high_threshold // 2
	high = thinned_grad > high_threshold
	low = thinned_grad > low_threshold
	canny_edges = ndimage.binary_dilation(high, structure=numpy.ones((3,3)), iterations=-1, mask=low)
	fig, ax = subplots()
	im = ax.imshow(canny_edges)
#	colorbar(im)
#	ax2 = fig.add_subplot(212)
#	ax2.hist(thinned_grad.flatten(), bins=100,log=True)
	savefig('thinned_grad_sobel'+str(i)+'_.png')
	
	
	
	
from __future__ import print_function
from matplotlib.pylab import *
import matplotlib.cbook as cbook

data = ones((1500, 1500, 3))
imshow(data)
ax = gca()
print(cbook.report_memory())
print(len(ax.images))
hold(False)
imshow(data)
print(cbook.report_memory())
print(len(ax.images))
imshow(data)
print(cbook.report_memory())
print(len(ax.images))
imshow(data)
print(cbook.report_memory())
print(len(ax.images))
imshow(data)
print(cbook.report_memory())
print(len(ax.images))

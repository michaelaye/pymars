'''
Created on Aug 25, 2009

@author: aye
'''

#import site
#site.addsitedir('/Library/Frameworks/GDAL.framework/Versions/1.6/Resources')

try:
    from osgeo import gdal
    from osgeo.gdalconst import *
    gdal.TermProgress = gdal.TermProgress_nocb
except ImportError:
    import gdal
    from gdalconst import *

import numpy as np

try:
    from osgeo import gdal_array as gdalnumeric
except ImportError:
    import gdalnumeric

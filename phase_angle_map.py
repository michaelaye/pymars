#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
from mars import ImgData, Point
from mars_spice import MarsSpicer
import os
from spice import vsep,vminus
import spice
import numpy as np
import matplotlib.pyplot as plt

folder = os.environ['HOME']+'/Data/hirise/DEMs/inca'
dem = ImgData(os.path.join(folder, 'big_spider_dem.cub'))
# dem = ImgData(os.path.join(folder, 'DTM_Inca_City_ngate_1m_forPDS.cub'))
# slopes = ImgData(os.path.join(folder,'slopes_full.tif'))
# aspects = ImgData(os.path.join(folder,'aspects_full.tif'))
slopes = ImgData(os.path.join(folder,'big_spider_slopes.tif'))
aspects = ImgData(os.path.join(folder,'big_spider_aspects.tif'))
# spider1 = ImgData(os.path.join(folder,'ESP_022607_0985_cropped_big_spider.cub'))
# spider2 = ImgData(os.path.join(folder,'ESP_022699_0985_cropped_big_spider.cub'))

# read in required data
dem.read_all()
slopes.read_all()
aspects.read_all()

# plt.imshow(dem.data,aspect='auto')
# plt.plot(dem.center.sample,dem.center.line, 'r*',markersize=10)

# determine angle between north and top to correct aspect angles that count like
# north is at the top of the image
newPoint = Point(lon=dem.center.lon, lat=dem.center.lat+0.001)
newPoint.lonlat_to_pixel(dem.geotransform, dem.projection)
# plt.plot(newPoint.sample, newPoint.line, 'g*', markersize=10)
v1 = np.array((newPoint.x - dem.center.x, newPoint.y - dem.center.y))
# delta between north and top of image
delta_angle = np.degrees(np.arctan2(v1[1],v1[0]))-90.0
# dsample = newPoint.sample - dem.center.sample
# dline = newPoint.line - dem.center.line
# plt.quiver(dem.center.sample,dem.center.line,dsample,dline,angles='xy', scale_units='xy', scale=1)

# correct aspects for delta angle
# it needs to be added, because aspects go clock-wise
aspects.data += delta_angle
# bend around data > 360
mask = aspects.data > 360.0
aspects.data[mask] = aspects.data[mask] - 360.0


# # create MarsSpicer object
mspice = MarsSpicer()
utc1 = '2011-05-24T00:58:08.402'
utc2 = '2011-05-31T05:01:50.854'
mspice.utc = utc2

mspice.obs = 'MRO'
mspice.instrument = 'MRO_HIRISE'
mspice.set_spoint_by('sincpt')
phase = np.zeros_like(dem.data)

emissions = []
incidences = []
rev_srfvec = spice.vminus(mspice.srfvec)
for sample in xrange(phase.shape[0]):
    if sample % 10 == 0:
        print('Sample {0}'.format(sample))
    for line in xrange(phase.shape[1]):
        slope = float(slopes.data[sample, line])
        aspect = float(aspects.data[sample, line])
        # newPoint = Point(sample, line)
        # newPoint.pixel_to_lonlat(dem.geotransform, dem.projection)
        # mspice.set_spoint_by(lat = newPoint.lat, lon = newPoint.lon)

        mspice.tilt = slope
        mspice.aspect = aspect
        trnormal = mspice.tilted_rotated_normal
        incidence = spice.vsep(trnormal, mspice.sun_direction)
        emission = spice.vsep(trnormal, rev_srfvec)
        emissions.append(emission)
        incidences.append(incidence)
        
        # print("Inc: %f" % incidence)
        # print("Emis: %f" % emission)
        
        # phase[sample,line] = 

emissions = np.degrees(np.array(emissions))
incidences = np.degrees(np.array(incidences))

plt.hist(emissions, 90, label = 'emissions')
plt.hist(incidences, 90, label = 'incidences')
plt.legend()
# figure()
# plt.imshow(phase)
# 
# 
plt.show()
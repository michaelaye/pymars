#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
from mars import ImgData, Point
from mars_spice import MarsSpicer
import os
from spice import vsep,vminus
import numpy as np
from matplotlib.pyplot import quiver, imshow, plot, show, figure

folder = os.environ['HOME']+'/Data/hirise/DEMs/inca'
dem = ImgData(os.path.join(folder, 'big_spider_dem.cub'))
slopes = ImgData(os.path.join(folder,'big_spider_slopes.tif'))
aspects = ImgData(os.path.join(folder,'big_spider_aspects.tif'))
# spider1 = ImgData(os.path.join(folder,'ESP_022607_0985_cropped_big_spider.cub'))
# spider2 = ImgData(os.path.join(folder,'ESP_022699_0985_cropped_big_spider.cub'))

# read in required data
dem.read_all()
slopes.read_all()
aspects.read_all()

# imshow(dem.data,aspect='auto')
# plot(dem.center.sample,dem.center.line, 'r*',markersize=10)

# determine angle between north and top to correct aspect angles that count like
# north is at the top of the image
newPoint = Point(lon=dem.center.lon, lat=dem.center.lat+0.001)
newPoint.lonlat_to_pixel(dem.geotransform, dem.projection)
# plot(newPoint.sample, newPoint.line, 'g*', markersize=10)
v1 = np.array((newPoint.x - dem.center.x, newPoint.y - dem.center.y))
# delta between north and top of image
delta_angle = np.degrees(np.arctan2(v1[1],v1[0]))-90.0
# dsample = newPoint.sample - dem.center.sample
# dline = newPoint.line - dem.center.line
# quiver(dem.center.sample,dem.center.line,dsample,dline,angles='xy', scale_units='xy', scale=1)

# correct aspects for delta angle
# it needs to be added, because aspects go clock-wise
aspects.data += delta_angle
# bend around data > 360
mask = aspects.data > 360.0
aspects.data[mask] = aspects.data[mask] - 360.0

# create MarsSpicer object
mspice = MarsSpicer()
mspice.goto_ls_0()
mspice.advance_time_by(24*3600*356)
utc = mspice.utc

timestep = 600
nsteps = 500

mspice.goto('inca')
times, _ = mspice.time_series('F_aspect',timestep, nsteps, provide_times='l_s')

insol = np.zeros_like(dem.data)
for sample in range(insol.shape[0]):
    print('Sample {0}'.format(sample))
    for line in range(insol.shape[1]):
        mspice.utc = utc
        newPoint = Point(sample, line)
        newPoint.pixel_to_lonlat(dem.geotransform, dem.projection)
        mspice.set_spoint_by(lat = newPoint.lat, lon = newPoint.lon)

        mspice.tilt = float(slopes.data[sample, line])
        mspice.aspect = float(aspects.data[sample, line])
        energies = mspice.time_series('F_aspect',timestep, nsteps)
        insol[sample,line] = energies.sum()
        
figure()
imshow(insol)
show()
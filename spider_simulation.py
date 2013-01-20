#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
import matplotlib
matplotlib.use('TkAgg')
from mars import ImgData, Point
from mars_spice import MarsSpicer
import os
from spice import vsep
import numpy as np
from matplotlib.pyplot import quiver, imshow, plot, show, figure,hist
import pdstools
import math

def get_xyz(theta,phi):
    t = np.radians(theta)
    p = np.radians(phi)
    x = np.sin(t)*np.cos(p)
    y = np.sin(t)*np.sin(p)
    z = np.cos(t)
    return x,y,z
    
def get_north_shifted_point(dem,offset=0.001):
    newPoint = Point(lon=dem.center.lon, lat=dem.center.lat+offset)
    newPoint.lonlat_to_pixel(dem.geotransform, dem.projection)
    return newPoint
    
def correct_azimuth(dem, aspects):
    """determine angle between north and top to correct aspect angles.
    
    GDAL tools put azimuth 0 at the top of the image.
    
    >>> dem = ImgData('/Users/maye/data/hirise/inca/big_spider_dem.cub')
    
    """
    newPoint = get_north_shifted_point(dem)
    # plot(newPoint.sample, newPoint.line, 'g*', markersize=10)
    v1 = np.array((newPoint.x - dem.center.x, newPoint.y - dem.center.y))
    # delta between north and top of image
    delta_angle = np.degrees(np.arctan2(v1[1],v1[0]))-90.0
    dsample = newPoint.sample - dem.center.sample
    dline = newPoint.line - dem.center.line
    # quiver(dem.center.sample,dem.center.line,dsample,dline,angles='xy', scale_units='xy', scale=1)

    # correct aspects for delta angle
    # it needs to be added, because aspects go clock-wise
    # DANGER: This only works
    aspects.data -= delta_angle
    # bend around data > 360
    mask = aspects.data > 360.0
    aspects.data[mask] = aspects.data[mask] - 360.0
    
def main():
    folder = os.environ['HOME']+'/data/hirise/inca'
    dem = ImgData(os.path.join(folder, 'big_spider_dem.cub'))
    slopes = ImgData(os.path.join(folder,'big_spider_slopes.tif'))
    aspects = ImgData(os.path.join(folder,'big_spider_aspects.tif'))
    spider1 = ImgData(os.path.join(folder,'ESP_022607_0985_cropped_big_spider.cub'))
    # spider2 = ImgData(os.path.join(folder,'ESP_022699_0985_cropped_big_spider.cub'))

    # read in required data
    dem.read_all()
    slopes.read_all()
    aspects.read_all()
    spider1.read_all()

    correct_azimuth(dem, aspects)

    # create MarsSpicer object
    mspice = MarsSpicer()
    # get labels from observation
    labels = pdstools.get_labels('/Users/maye/data/hirise/inca/ESP_022607_0985_RED.LBL')
    mspice.utc = pdstools.get_time(labels)
    #set coordinates
    mspice.set_spoint_by(lat=pdstools.get_mean_lat(labels),lon=pdstools.get_mean_lon(labels))

    cos_corrected = np.zeros(dem.data.shape)
    real_inc_degrees = np.zeros_like(dem.data)
    label_incidence = pdstools.get_incidence(labels)
    label_sol_azi = pdstools.get_sub_sol_azi(labels)
    sun_vec = get_xyz(label_incidence, label_sol_azi)

    print("slopes min max: {0}, {1}".format(slopes.data.min(),slopes.data.max()))
    print("aspect min max: {0}, {1}".format(aspects.data.min(),aspects.data.max()))

    cos_corrected[0,:]= np.nan
    cos_corrected[:,0]= np.nan
    print(type(cos_corrected))

    for sample in range(1,dem.X-1):
        # print sample
        for line in range(1,dem.Y-1):
            slope = float(slopes.data[line,sample])
            aspect= float(aspects.data[line, sample])
            normal_vec = get_xyz(slope, aspect)
            current_inc = math.degrees(vsep(normal_vec,sun_vec))
            real_inc_degrees[line,sample] = current_inc
            if current_inc >= 89.0:
                cos_corrected[line,sample] = np.nan
            else:
                value = math.cos(math.radians(current_inc))
                cos_corrected[line,sample]= value
           
    print('loop done.')
    print('min/max:{0}, {1}'.format(real_inc_degrees.min(),real_inc_degrees.max()))
    print('min/max:{0}, {1}'.format(np.nanmin(cos_corrected),np.nanmax(cos_corrected)))

    print np.histogram(cos_corrected,range=(0,57))
    # fig = figure()
    # ax = fig.add_subplot(121)
    imshow(cos_corrected,cmap = 'gray')
    # ax2 = fig.add_subplot(122)
    # ax2.hist(cos_corrected.flatten())
    show()

if __name__ == '__main__':
    main()
    
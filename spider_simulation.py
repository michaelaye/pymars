#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
from __future__ import division, print_function
import matplotlib
matplotlib.use('TkAgg')
from mars import ImgData, Point
import os
import numpy as np
import matplotlib.pyplot as plt
import pdstools

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
    
def correct_azimuth(aspects, dem=None, angle=None):
    """determine angle between north and top to correct aspect angles.
    
    Parameters
    ----------
    aspects:    ImgData object with aspects angles from gdaldem to be corrected
    angle:      Angle value to use for correction. Alternatively provide /dem/
    dem:        dem ImgData object to derive north from.
    
    GDAL tools put azimuth 0 at the top of the image.
    
    >>> dem = ImgData('/Users/maye/data/hirise/inca/big_spider_dem.cub')
    
    """
    if not any([dem, angle]):
        raise NameError('Either dem or angle needs to be defined.')
    if dem:
        newPoint = get_north_shifted_point(dem)
        # create numpy vector
        v1 = np.array((newPoint.x - dem.center.x, newPoint.y - dem.center.y))
        # delta between north and top of image, -90 for the difference between GDAL and Hirise Azi-0
        delta_angle = np.degrees(np.arctan2(v1[1],v1[0])) - 90.0
        # correct aspects for delta angle
        # it needs to be added, because aspects go clock-wise
    else:
        delta_angle = angle
    # aspects.data -= delta_angle
    aspects.data += 270
    # bend around data > 360
    mask = aspects.data > 360.0
    aspects.data[mask] = aspects.data[mask] - 360.0
    
def test_correct_azimuth(aspects, dem=None, angle=None):
    if not any([dem, angle]):
        raise NameError('Either dem or angle needs to be defined.')
    if dem:
        newPoint = get_north_shifted_point(dem)
        # plot(newPoint.sample, newPoint.line, 'g*', markersize=10)
        v1 = np.array((newPoint.x - dem.center.x, newPoint.y - dem.center.y))
        # delta between north and top of image
        delta_angle = np.degrees(np.arctan2(v1[1],v1[0]))-90.0
        dsample = newPoint.sample - dem.center.sample
        dline = newPoint.line - dem.center.line
        # quiver(dem.center.sample,dem.center.line,dsample,dline,angles='xy', scale_units='xy', scale=1)
    else:
        delta_angle = angle
    # correct aspects for delta angle
    # it needs to be added, because aspects go clock-wise
    # DANGER: This only works
    # aspects.data -= delta_angle
    aspects.data += delta_angle
    # bend around data > 360
    mask = aspects.data > 360.0
    aspects.data[mask] = aspects.data[mask] - 360.0
    
def main():
    folder = os.environ['HOME']+'/data/hirise/inca'
    # dem = ImgData(os.path.join(folder, 'big_spider_dem.cub'))
    slopes = ImgData(os.path.join(folder,'big_spider_slopes.tif'))
    aspects = ImgData(os.path.join(folder,'big_spider_aspects.tif'))
    spider1 = ImgData(os.path.join(folder,'ESP_022607_0985_cropped_big_spider.cub'))
    # spider2 = ImgData(os.path.join(folder,'ESP_022699_0985_cropped_big_spider.cub'))

    # read in required data
    # dem.read_all()
    slopes.read_cropped_by_n(1)
    aspects.read_cropped_by_n(1)
    spider1.read_all()

    # correct_azimuth(dem, aspects)
    
    # clean up data
    slopes.data[slopes.data < 0] = np.nan
    slopes.data[slopes.data > 90] = np.nan
    aspects.data[aspects.data < 0] = np.nan
    aspects.data[aspects.data > 360] = np.nan
    
    # create MarsSpicer object
    # mspice = MarsSpicer()
    # get labels from observation
    labels = pdstools.get_labels('/Users/maye/data/hirise/inca/ESP_022607_0985_RED.LBL')
    # mspice.utc = pdstools.get_time(labels)
    #set coordinates
    # mspice.set_spoint_by(lat=pdstools.get_mean_lat(labels),lon=pdstools.get_mean_lon(labels))

    label_incidence = pdstools.get_incidence(labels)
    label_sol_azi = pdstools.get_sub_sol_azi(labels)
    # correct for difference to GDAL coordinates (not correcting the aspects map)
    sol_azi = 90 + label_sol_azi
    # using negative sol_azi because angles are positive in clock-direction in HiRISE data
    sun_vec = get_xyz(label_incidence, -sol_azi)
    # now the S/C (emission) vector
    sc_azimuth = pdstools.get_sub_sc_azimuth(labels)
    # shift to GDAL 0-point, as above
    sc_azimuth += 90
    emis = pdstools.get_emission(labels)
    # again, use negative azimuth, as the formula for xyz uses positive counter-clockwise
    sc_vec = get_xyz(emis, -sc_azimuth)

    print("slopes min max: {0}, {1}".format(np.nanmin(slopes.data),np.nanmax(slopes.data)))
    print("aspect min max: {0}, {1}".format(np.nanmin(aspects.data),np.nanmax(aspects.data)))
    print(slopes.data.argmin(),slopes.data.argmax())
    print(aspects.data.argmin(),aspects.data.argmax())
    normal_xyz = get_xyz(slopes.data, 360-aspects.data)
    normal_x,normal_y,normal_z = normal_xyz
    normal_vec = np.dstack([normal_x,normal_y,normal_z])
    # first calculate real incidences
    cosa = normal_vec.dot(sun_vec) / np.apply_along_axis(np.linalg.norm,2,normal_vec)
    cosa /= np.linalg.norm(sun_vec)
    print('cosa calculated.')
    # now real emissions
    cose = normal_vec.dot(sc_vec) / np.apply_along_axis(np.linalg.norm,2,normal_vec)
    cose /= np.linalg.norm(sc_vec)
    print('cose calculated.')
    
    # set smaller than 0 to 0
    cosa[cosa<0.0] = 0.0
    
    real_inc = np.degrees(np.arccos(cosa))
    real_emis = np.degrees(np.arccos(cose))
    # if current_inc >= 89.0:
    #     cos_corrected[line,sample] = np.nan
    # else:
    #     value = math.cos(math.radians(current_inc))
    #     cos_corrected[line,sample]= value
    cos_corrected = cosa

    print('min/max:{0}, {1}'.format(np.nanmin(real_inc),np.nanmax(real_inc)))
    print('min/max:{0}, {1}'.format(np.nanmin(cos_corrected),np.nanmax(cos_corrected)))
    print('min/max:{0}, {1}'.format(np.nanmin(cose),np.nanmax(cose)))

    print(np.histogram(cos_corrected,range=(0,1)))
    print(np.histogram(real_inc,range=(0,90)))
    fig = plt.figure()
    ax_inc = fig.add_subplot(122)
    # ax_inc = fig.add_subplot(221)
    img = ax_inc.imshow(cos_corrected,cmap = 'gray')
    ax_inc.set_title("'Lambertian' image from Inca DEM",fontsize=14)
    # colorbar(img)
    plt.axis('off')
    ax_real = fig.add_subplot(121)
    img = ax_real.imshow(spider1.data,cmap='gray')
    ax_real.set_title('Ortho-image Inca spider',fontsize=14)
    # ax_emis = fig.add_subplot(222)
    # img = ax_emis.imshow(cose, cmap='gray')
    # colorbar(img)
    # ax_emis.set_title('cose')
    # ax_hist = fig.add_subplot(223)
    # emis_angles = np.degrees(np.arccos(cose))
    # ax_hist.hist(emis_angles.flatten(),bins=45,range=(0,90))
    # ax_hist.set_title('Emission angles histogram')
    plt.axis('off')
    plt.show()
    return [real_inc,real_emis]

if __name__ == '__main__':
    main()
    
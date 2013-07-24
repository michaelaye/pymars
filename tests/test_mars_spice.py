from pymars import mars_spice as ms
from pymars import mars
from pymars import pdstools
from nose.tools import assert_equals


labels = pdstools.get_labels('data/ESP_022699_0985_RED.LBL')


def test_azimuth():
    dem = mars.ImgData('/Users/maye/data/hirise/inca_city_dem/latest_download/ESP_022699_0985_RED_A_01_ORTHO.JP2')
    #mspice = ms.MarsSpicer(pdstools.get_time(labels))
    mspicer = ms.MarsSpicer()
    mspicer.goto_ls_0()
    mspicer.set_spoint_by(lat=dem.center.lat, lon=dem.center.lon)
    p2lon, p2lat = mspicer.point_towards_sun(pixel_res=1)
    p2 = mars.Point(lat=p2lat, lon=p2lon)
    p2.lonlat_to_pixel(dem.center.geotrans, dem.center.proj)
    assert_equals(dem.center.calculate_azimuth(p2),
                  pdstools.get_sub_sol_azi(labels))


def test_incidence_angle():
    inc = pdstools.get_incidence(labels)
    mspicer = ms.MarsSpicer()
    mspicer.utc = pdstools.get_time(labels)
    lat = pdstools.get_mean_lat(labels)
    lon = pdstools.get_mean_lon(labels)
    mspicer.set_spoint_by(lat=lat, lon=lon)
    calculated_inc = mspicer.illum_angles.dsolar
    # rounding off all fractions here for this test! improve?
    assert_equals(round(calculated_inc), round(inc))


def test_local_solar_time():
    label_time = pdstools.get_local_solar_time(labels)
    mspicer = ms.MarsSpicer()
    mspicer.utc = pdstools.get_time(labels)
    lat = pdstools.get_mean_lat(labels)
    lon = pdstools.get_mean_lon(labels)
    mspicer.set_spoint_by(lat=lat, lon=lon)
    calculated_soltime = mspicer.fractional_local_time
    assert_equals(round(label_time, 1), round(calculated_soltime, 1))       

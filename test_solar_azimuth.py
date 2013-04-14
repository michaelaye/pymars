import mars_spice as ms
import mars
import pdstools

dem = mars.ImgData('/Users/maye/data/hirise/inca_city_dem/latest_download/ESP_022607_0985_RED_A_01_ORTHO.JP2')
labels = pdstools.get_labels('/Users/maye/data/hirise/inca/ESP_022607_0985_RED.LBL')
mspice = ms.MarsSpicer(pdstools.get_time(labels))
mspice.set_spoint_by(lat=dem.center.lat, lon=dem.center.lon)
p2lon, p2lat = mspice.compute_solar_azimuth(pixel_res=1)
p2 = mars.Point(lat=p2lat,lon=p2lon)
p2.lonlat_to_pixel(dem.center.geotransform, dem.center.proj)
print 'Calculated:',dem.center.calculate_azimuth(p2)
print 'Calculated, zero=top',dem.center.calculate_azimuth(p2,zero='top')
print 'From label:',pdstools.get_sub_sol_azi(labels)
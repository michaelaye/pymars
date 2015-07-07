# coding=utf-8
"""
This is a little module calculating the maximum deviation of solar
incidence angles between the 4 corners of as given by a PDS label.
"""
from __future__ import print_function
from kmaspice import MarsSpicer
from numpy import array
import pdstools

labels = pdstools.PDSLabel('/Users/maye/data/hirise/inca/ESP_022607_0985_RED.LBL')
# taking these from the grayscale label of ESP_022607_0985
max_lat = labels.maxlat
min_lat = labels.minlat
east_lon = labels.eastmost
west_lon = labels.westmost

start_time = labels.time

event = MarsSpicer(time=start_time)
inc_angles = []
for lat,lon in [(max_lat,east_lon),
                (max_lat,west_lon),
                (min_lat,east_lon),
                (min_lat,west_lon)]:
    event.set_spoint_by(lat=lat,lon=lon)
    inc_angles.append(event.illum_angles.dsolar)
    print("Lat = {0}, Lon = {1}, \nIncidence angle:{2}\n".format(
            lat,lon,event.illum_angles.dsolar))


angles = array(inc_angles)

delta = angles.max()-angles.min()

print("Max difference: ",delta)
print("Relative error to mean [%]: ",delta*100/angles.mean())

import math

def m_get_lat(map_projection, x, y, LatP, Rp):
#--- get lat and lon of the position /first image/----
  if map_projection == 'POLAR STEREOGRAPHIC':
    P = math.sqrt(x**2 + y**2)
    C = 2.00 * math.atan(P / (2.00 * Rp))
    Lat = math.asin( math.cos(C)*math.sin(LatP) +  y*math.sin(C)*math.cos(LatP) / P )
    return Lat
  else: print "This map projection is not implemented yet"

def m_get_lon( x, y, LonP):
  if x < 0 : Lon = LonP - math.atan(x/y) 
  else: Lon = LonP + math.atan(x/y)
  return Lon

def m_get_xy_from_latlon( Lat, Lon, LonP, Rp, map_projection, x, y):
  if map_projection == "POLAR STEREOGRAPHIC":
#   ;---get x and y in km
    x =  2.00 * Rp * math.tan(math.pi / 4.0 + lat / 2.00) * math.sin(Lon - LonP)
    y =  -2.00 * Rp * math.tan(math.pi / 4.00 + Lat / 2.00) * math.cos(Lon - LonP)
#   ;----get line, sample for second file in pix
  else: print 'Unknown map projection'

def m_get_sample_from_x( x, sample_offset, scale):
  sample = (x/scale + sample_offset + 1.00)
  return sample

def m_get_line_from_y( y, line_offset, scale):
  line = (1.00 - line_offset - y/scale)
  return line

LonP, LatP, line_offset, sample_offset, scale, Rp, lines, samples, map_projection = \
    0.0000000, -1.5707963 , 894419.50 , 1866088.5 , 0.25000000 , 3376200.0 , 10028.000 , 44744.000, 'POLAR STEREOGRAPHIC'

print LonP, LatP, line_offset, sample_offset, scale, Rp, lines, samples, map_projection

sample = 1
line = 1
    
x = (sample - sample_offset -1.0) * scale
y = (1.00 - line_offset - line) * scale
print x,y
lat = m_get_lat(map_projection, x, y, LatP, Rp)
lon = m_get_lon(x, y, LonP)
print lat*180/math.pi, lon*180/math.pi
m_get_xy_from_latlon(lat, lon, LonP, Rp, map_projection, x, y)
sample2 = m_get_sample_from_x(x, sample_offset, scale)
line2 = m_get_line_from_y(y, line_offset, scale)
print sample2, line2

#!/Library/Frameworks/Python.framework/Versions/7.3/bin/python
from visual import *

class CoordinateSystem(object):
    def __init__(self):
        self.x_axis = vector(1,0,0)
        self.y_axis = vector(0,1,0)
        self.z_axis = vector(0,0,1)
        
        # arrows for the axes
        to_x = arrow(pos=(0,0,0), axis=self.x_axis*50, shaftwidth=0.001, opacity=0.5)
        to_m_y = arrow(pos=(0,0,0), axis=-self.y_axis*50, shaftwidth=0.001, opacity=0.5)
        to_z = arrow(pos=(0,0,0), axis=self.z_axis*50, shaftwidth=0.001, opacity=0.5)

        # labels for the axes
        xlabel=label(pos=self.x_axis*50, text='x', yoffset=20)
        ylabel = label(pos=-self.y_axis*40, xoffset=20, text='-y')
        zlabel = label(pos=self.z_axis*50,gxoffset=-20,text='z')
    

scene = display(title='Illumination angles', x=200, y=200, width=600, height=600)
scene.forward = (0, 1,-1)
scene.range=60
scene.up = (0,0,1)

plane = box(pos = (0,0,0),length=100,height=100,width=0.1,
            opacity=0.5,color=color.orange)

coords = CoordinateSystem()

inc = 62.49
emis = 7.36
phase = 67.08
sub_sc_azi = 127.24
north_azimuth = 205.78
sun_azimuth = 153.58

sun_vec = rotate(coords.z_axis, radians(inc), coords.y_axis)
sun_vec = rotate(sun_vec, -radians(sun_azimuth), coords.z_axis)
sun_azi_vec = vector(sun_vec[0],sun_vec[1],0)
north_azi_vec = rotate(coords.x_axis, -radians(north_azimuth), coords.z_axis)
sc_vec = rotate(coords.z_axis, radians(emis), coords.y_axis)
sc_vec = rotate(sc_vec, -radians(sub_sc_azi), coords.z_axis)
    
# slope
surf_normal_vec = rotate(coords.z_axis,-radians(50), coords.x_axis)
# aspect
surf_normal_vec = rotate(surf_normal_vec, -radians(30), coords.z_axis)

to_sun = arrow(pos=(0,0,0), axis=50*sun_vec,
                     color=color.yellow,shaftwidth=0.001)
sunlabel=label(pos=50*sun_vec, text='sun',yoffset=20)
to_north = arrow(pos=(0,0,0), axis = 50*north_azi_vec, shaftwidth=0.001)
northlabel = label(pos=50*north_azi_vec, text='North',yoffset=20)
to_sc = arrow(pos=(0,0,0),axis=60*sc_vec, color=color.green,shaftwidth=0.001)
sclabel = label(pos=50*sc_vec, text='S/C',xoffset=20)
surf_normal = arrow(pos=(0,0,0),axis=50*surf_normal_vec,color=color.red,shaftwidth=0.002)
labelnormal=label(pos=50*surf_normal_vec, text='surf_normal',xoffset=20)
sun_azi = arrow(pos=(0,0,0),axis=50*sun_azi_vec,opacity=0.5,shaftwidth=0.001)
sun_azi_to_sun = arrow(pos=50*sun_azi_vec,axis=50*(sun_vec-sun_azi_vec),
                       opacity=0.5,shaftwidth=0.001)

print "Delta:",degrees(diff_angle(sun_azi_vec,sun_vec-sun_azi_vec))
print "Inc:",inc
print "Emis:",emis
print "phase", phase
print "north_azi",north_azimuth
print "sun_azimuth",sun_azimuth

print "Delta sun<->surface_normal",degrees(diff_angle(sun_vec, surf_normal_vec))


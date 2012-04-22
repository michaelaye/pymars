#!/Library/Frameworks/Python.Framework/Versions/2.7/bin/python
from __future__ import division
from visual import *

scene.forward = (1,0,0)
scene.up = (0,0,1)
scene.x = 400
scene.y = 300
scene.width = 800
scene.height = 800

xaxis = arrow(axis=(4000,0,0), shaftwidth=40, color=color.red)
yaxis = arrow(axis=(0,4000,0), shaftwidth=40, color=color.green)
zaxis = arrow(axis=(0,0,4000), shaftwidth=40, color=color.blue)
# mars = ellipsoid(length=2*3396.19,height=2*3396.19,width=2*3376.2, opacity=0.5, color=(1,0.7,0.2))
mars = sphere(radius=3396.19, opacity=0.5, color=(1,0.7,0.2))
spoint = vector(220.09830399469547, -440.60853011059214, -3340.5081261541495)
v_spoint = arrow(axis = spoint, shaftwidth=40, color=color.white)
scene.center = spoint
sun = vector(-0.7259364991852024, -0.6362878974945938, -0.2610630396142698)
v_sun = arrow(pos=spoint,axis = 500*sun, shaftwidth=40, color=color.yellow)
#!/usr/bin/python
'''
Created on Aug 16, 2009

@author: aye
'''
from gdal_imports import *
from hirise_tools import *

reader = csv.reader(open('Crater_coordinates.csv'))

try:
    size = int(sys.argv[1])
    vmin = float(sys.argv[2])
    vmax = float(sys.argv[3])
except:
    size = 50
    vmin = None
    print "taking default size of ",size

def genPlot(array, vmin, vmax, figNumber=1):
    plt.figure(figNumber)
    plt.subplot(2,3,i)
    print i
    plt.imshow(array, vmin = vmin, vmax= vmax, interpolation = None) 
    plt.xlabel('Sample')
    plt.ylabel('Line')
    plt.title(row[0])
    cb = plt.colorbar(orientation='hor', spacing='prop',ticks = [vmin,vmax],format = '%.2f')
    cb.set_label('Reflectance / cos({0:.2f})'.format(incAnglerad*180.0/math.pi))
    plt.grid(True)
    

times = []
means = []
means2 = []
plt.figure(1,figsize = (9,7), dpi=100)
plt.figure(3,figsize = (9,7), dpi=100)
for i,row in enumerate(reader):
    if i == 0 or row[0]=='': continue
    obsID = "_".join(row[0].split("_")[:3])
    path = '/processed_data/' + obsID + '/'
    searchPath = path + '*BG*.mos.cub'
    bg_file = glob.glob(searchPath)
    spiceinfo = glob.glob(path + '*BG*spiceinfo*')
    spicefile = open(spiceinfo[0],'r')
    L_s, incAngle = spicefile.readline().split()
    incAnglerad = float(incAngle)*math.pi/180.0
    times.append(float(L_s))
    eye_sample, eye_line = row[1:3]
    nose_sample, nose_line = row[3:5]
    print eye_sample, eye_line, nose_sample, nose_line
    print "opening",bg_file[0]
    cube = gdal.Open(bg_file[0], GA_ReadOnly )
    xOff = int(eye_sample) - size/2 -1
    yOff = int(eye_line) - size/2 -1
    array = cube.ReadAsArray(xOff, yOff, size, size)
    array = array / math.cos(incAnglerad)
    means.append(Numeric.mean(array))
    if i == 1 and vmin == None:
        vmin = Numeric.min(array)
        vmax = Numeric.max(array)
        print vmin,vmax
    genPlot(array, vmin, vmax)
    xOff = int(nose_sample) - size/2 -1
    yOff = int(nose_line) - size/2 -1
    array = cube.ReadAsArray(xOff, yOff, size, size)
    array = array/math.cos(incAnglerad)
    means2.append(Numeric.mean(array))
    genPlot(array, vmin,vmax, 3)
    

plt.figure(2)
plt.plot(times,means,'bo')
plt.xlabel('L_s [deg]')
plt.ylabel('Reflectance / cos(i) for {0}x{0} pixels'.format(size))
plt.title('mean(BG) vs L_s, eye-crater')
plt.plot(times,means2,'ro')
plt.show()

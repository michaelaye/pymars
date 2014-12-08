# encoding: utf-8

The ``mars`` module
======================

Using the ``Point`` class
-------------------------

First import ``Point`` from the ``mars`` module:

>>> from mars import Point

The default arguments determine ``sample`` and ``line``:

>>> p = Point(10,40)
>>> print(p)
Pixel: (10,40)
Map: (None,None)
Geo: (None,None,None)
	
>>> print(p.sample)
10
>>> print(p.line)
40

The attribute ``pixels`` provides a numpy array that can be
used for vectorial calculations:

>>> print(p.pixels)
[10 40]
	
For latitudinal arguments there is an optional altitude or radius, measured 
from the center of the body:

>>> geoP = Point(lat=30, lon=100)
>>> print(geoP)
Pixel: (None,None)
Map: (None,None)
Geo: (100,30,None)
>>> geoP = Point(lat=30, lon=100, radius=1234.5)
>>> print(geoP)
Pixel: (None,None)
Map: (None,None)
Geo: (100,30,1234.5)

Then there are the coordinates that are used for distances in map-projected
data:

>>> mapP = Point(x=1e3, y=-3.5e3)
>>> print(mapP)
Pixel: (None,None)
Map: (1000.0,-3500.0)
Geo: (None,None,None)

This also can be used as a numpy array, for vectorial calculations via the ``coords``
attribute:

>>> print(mapP.coords)
[ 1000. -3500.]

To be able to work with SPICE, rectangular coordinates that refer to a given
IAU_frame have been implemented:

>>> spiceP = Point()

	

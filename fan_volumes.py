# encoding: utf-8
"""
fan_volumes.py

Created by K.-Michael Aye on 2011-09-19.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
from __future__ import division
from pylab import *
from planets import Mars

def get_stsc_area(latitude):
    """Surface area in m**2 of Southern translucent seasonal cap from Piqueux's paper. 
    
    In: Latitude in degrees
    Out: Area in m**2
    """
    return 2*pi*Mars.radius_eq**2*(1-sin(deg2rad(latitude)))

# According to Candy's ICARUS paper, southern ice cap covers until lat of 50degree.
stsc_area = get_stsc_area(50)

# dust devil mass in kg per martian annum taken from Whelley[2008]
dust_devil_mass = 2.3e11

# taken from Martin[1995], extrapolation from some areas to +/- 60 deg latitudes 
global_dust_storm_mass = 4.3e11 
piqueux_bulk_density = 4.e3/3.
silt_to_sand_fraction = 0.355
sand_to_silt_factor = (1-silt_to_sand_fraction)/silt_to_sand_fraction

class Fan(object):
    """docstring for Fan"""
    # these required thicknesses taken from Piqueux's paper
    # for each particle size in micron a layer thickness in m is defined
    d = {2:0.5e-3,
         10:1e-3,
         150:5e-3}
    def __init__(self, psize,fan_fraction=0.3, packing=1.0):
        """packing is set to 1, which is fine if one works with bulk densities"""
        super(Fan, self).__init__()
        self.psize = psize
        self.fan_fraction = fan_fraction
        self.packing = packing
        self.thickness = self.d[psize]
        dusty_area = stsc_area * fan_fraction
        self.vol = dusty_area * self.thickness
        self.sand_vol = self.vol*packing
        self.sand_mass = self.sand_vol * piqueux_bulk_density
        self.dust_mass = self.sand_mass/sand_to_silt_factor

def main():
    fractions = linspace(0.05,0.9,10)
    fans = []
    for psize in [10]:
        fans.append(Fan(psize,fan_fraction = 0.3333333))
    print "Piqueux's density: {0} kg/m**3".format(piqueux_bulk_density)
    print "Dust devil mass: {0:g} kg".format(dust_devil_mass)
    print "Global dust storm mass: {0:g} kg".format(global_dust_storm_mass)
    print
    for fan in fans:
        print """Particle size: {0} mu, 
thickness deduced from Kieffer's thermal modeling: {1} m""".format(fan.psize,fan.thickness)
        print "Geom. volume at {1} fan fraction: {0:g} m**3".format(fan.vol,fan.fan_fraction)
        # print "Particle volume at {1} packing: {0:g} m**3".format(fan.sand_vol,fan.packing)
        print "Sand mass: {1:g} kg".format(fan.packing,fan.sand_mass)
        print "Dust mass: {1:g} kg".format(fan.packing,fan.dust_mass)
        print "Ratio fan dust mass / global_dust_storm: {0:g}"\
            .format(fan.dust_mass/global_dust_storm_mass)
        print "Ratio fan dust mass / dust_devil_mass: {0:g}"\
                .format(fan.dust_mass/dust_devil_mass)
        print
        # print "Volume if divided by 0.3 instead of multipling: {0:g} m**3".format(fan.vol/0.3/0.3)
    # print "200 x Wheeley mass: {0}".format(200*dust_devil_mass)
    #     plot(fan.fan_fraction,fan.sand_mass/2.0,label="{0} mm fan layer".format(fan.thickness*1e3))
    # xlabel('Fraction of surface covered by fans')
    # ylabel('Estimated dust mass from fans [kg]')
    # grid()
    # xlim([0,0.95])
    # ylim(ymax = 1.0e13)
    # legend(loc='best')
    # show()
if __name__ == '__main__':
    main()


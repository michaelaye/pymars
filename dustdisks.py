from __future__ import division
from numpy import pi, deg2rad, array,sin,cos,tan, zeros
from traits.api import HasTraits, Float, Property, Tuple
from mars_spice import MarsSpicer
from spice import furnsh, vsep, vrotv
import cStringIO
import datetime as dt
from read_ClimateDatabase import read_daily_average_CO2_depth

tau = 2*pi

class Mars(HasTraits):
    g = Float(3.758)            # m/sec2 - g at north pole of Mars
    # only for SPICE stuff
    obliquity = Float(deg2rad(25.19))   # degrees - angle of inclination of the axis of rotation to the orbital plane

class Regolith(HasTraits):
    rho = Float(1300000)        #230000,  # g/m3 - regolith density
    sreg = 0.40*4.184,          # specific heat of regolith
    A = Float(0.25)             # albedo of regolith

class CO2(HasTraits):
    spec_heat = Float(0.15*4.184)   # J/g/K specific heat of CO2 gas
    rho = Float(156000)         # 156000, # g/m3 - density of ice
    s = Float(0.205*4.184)          # J/g/K - specific heat of dry ice
    L = 635.0                       # J/g - latent heat of vaporization CO2

class CO2_block(CO2, MarsSpicer):
    from define_my_consts import ro_CO2
    from CO2_phase_diagram import CO2_sublime_mass
     
    def __init__(self, time = None, dt = None):
        MarsSpicer.__init__(self, time)
        #self._h = 1 # default thickness of the ice layer
        
    @property
    def _h(self):
        h = read_daily_average_CO2_depth(self.coords.dlat, self.coords.dlon, self.l_s)
        return h   
    
class DustParticle(Regolith, MarsSpicer):
    r = Float               # radius of the dust
    S = Property(depends_on = 'r')    # surface of dust disk
    #normal = Tuple
    gamma = Float
    
    def __init__(self, normal, degree=None, axis=None, time=None, rad = None, height = None):
        MarsSpicer.__init__(self, time)
        self.r = rad
        self._h = height
        if degree and axis:
            rot_axis = zeros(3)
            rot_axis[axis] = 1
            self.normal = vrotv(normal,deg2rad(degree), rot_axis)
            self.gamma = degree
        else:
            self.normal = normal

    def _get_S(self):
        # surface of dust disk
        return 0.5 * tau * self.r * self.r
        
    @property
    def h(self):
        h_CO2 = read_daily_average_CO2_depth(self.coords.dlat, self.coords.dlon, self.l_s)
        print h_CO2
        if self._h > h_CO2:
            return h_CO2  
        else:
            return self._h     

def write_output(output, arg):
    output.write("%7.5f  %7.5f %7.5f  %7.5f %7.5f %7.5f %7.5f %7.5f %7.5f\n" % arg)


def main():    
    dT = 70  # Kelvin
    utc = '2007-Jan-28-28T21:12:55' # time of PSP_002380_0985 = 174.477

    # angles between normal to the disk surface and Z-axis
    disk1 = DustParticle(normal = array((0,0,1)), time = utc)
    
    # rotating a z-normal by 10 degree around (0,1,0)
    # axis count starts at 0 !
    # disk2 = DustParticle(normal = array((0,0,1)), degree=10, axis = 1)

    time_step = dt.deltatime(hours=1)
    # coordinates of secondary halos in Inca City: lon = 296.591709, lat = -81.512266
    # set surface point via these coordinates

    disk1.set_spoint_by(lon=-81.512266, lat= 296.591709)

    # writing into a string and saving to file later
    output = cStringIO.StringIO()
    x = 0
    x2 = 0
    ds = 0
    while mspicer.l_s < 250:

        # if sun's lowest point is under horizon, there was time for freezing
        if hn < 0:
            Tch = 0

        # here solar incidence measured in height over horizon
        h = 90 - mspicer.coords.dsolar

        # if sun's under the horizon
        if h < 0:
            write_output(output, (mspicer.l_s, x, x2, hv, hn, h, disk1.mu, disk1.I, ds))
            disk1.time += time_step
            continue
    
        # sun is over horizon
        sun_vec = mspicer.sun_direction

        # length of passage of light through ice
        ds = cos(pi/2. - h)*(x + r)*1000000; # put' sveta vo ldu v micronah
        # exponential attenuation in this length
        #E = E*exp(-4.*pi*0.0001*ds/35);# s pogloscheniem

        #discs
        Ed1 = disk1.P
        #Ed = Ed*exp(-4.*pi*0.0001*ds/35.);# s pogloscheniem
        md = Ed1 / (CO2.s * dT + CO2.L) # mass / t [g/s]
        Vd = md/CO2.rho  # Vol / t [m**3/s]
        mchd = rho*pi*r*r*r/10. # why would this be the mass of the disk?

        Ed2 = disk2.P
        #Ed2 = Ed2*exp(-4.*pi*0.0001*ds/35.);# s pogloscheniem
        md2 = Ed2 / (CO2.s * dT + CO2.L);
        Vd2 = md2/CO2.rho

        #nagrevanie chastichki
        # warming up of the particle
        # 217: equilibrium T of CO2
        if (Tch < 217):
            # duration of warming up
            tnagd = floor((disk1.S * disk1.r / 10.) * disk1.sreg * dT / Ed1) + 1
            Tch = 217
        else:
            tnagd = 0

        # # rastaplivanie l'da
        # # melting of ice
        # for ( t = tnagd; t <= 3600; t++ )
        # {
        #     if (disk1.gamma != 90.*pi/180.):
        #         dx = Vd/pi/r/r*cos(gamma);
        #     else:
        #         dx = Vd/(r*r/5.);
        #     x = x + dx;
        # 
        #     if (gamma2 != 90.*pi/180.) dx2 = Vd2/pi/r/r*cos(gamma2);
        #     else dx2 = Vd2/(r*r/5.);
        #     x2 = x2 + dx2;
        # };

if __name__ == '__main__':
    main()

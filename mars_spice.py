import spice
from collections import namedtuple
import numpy as np
from traits.api import HasTraits, Str, Int, Float, ListStr, Enum, Date, Property, \
    Tuple, Range, cached_property, Instance, DelegatesTo, Bool, List
import datetime as dt
import dateutil.parser as tparser
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, drange
import math

L_sol = 3.839e26 # [Watt]

metakernel_paths = [
    '/Users/maye/Data/spice/mars/mro_2009_v06_090107_090110.tm',
    '/Users/maye/Data/spice/mars/mro_2007_v07_070127_070128.tm',
    '/Users/maye/Data/spice/mars/mro_2007_v07_070216_070217.tm',
    '/Users/maye/Data/spice/mars/mro_2011_v04_110524_110524.tm',
    ]

# pure planetary bodies meta-kernel without spacecraft data
spice.furnsh('/Users/maye/Dropbox/src/pymars/mars.tm')

# simple named Radii structure, offering Radii.a Radii.b and Radii.c

Radii = namedtuple('Radii', 'a b c')

def make_axis_rotation_matrix(direction, angle):
    """
    Create a rotation matrix corresponding to the rotation around a general
    axis by a specified angle.

    R = dd^T + cos(a) (I - dd^T) + sin(a) skew(d)

    Parameters:

        angle : float a
        direction : array d
    """
    d = np.array(direction, dtype=np.float64)
    d /= np.linalg.norm(d)

    eye = np.eye(3, dtype=np.float64)
    ddt = np.outer(d, d)
    skew = np.array([[    0,  d[2], -d[1]],
                     [-d[2],    0,   d[0]],
                     [ d[1], -d[0],    0]], dtype=np.float64)

    mtx = ddt + math.cos(angle) * (eye - ddt) + math.sin(angle) * skew
    return mtx


class IllumAngles(HasTraits):
    phase = Float
    solar = Float
    emission = Float
    dphase = Property(depends_on = 'phase')
    dsolar = Property(depends_on = 'solar')
    demission = Property(depends_on = 'emission')

    @classmethod
    def fromtuple(cls, args, **traits):
        return cls(phase=args[0],solar=args[1],emission=args[2], **traits)
        
    @cached_property
    def _get_dphase(self):
        return np.rad2deg(self.phase)

    @cached_property
    def _get_dsolar(self):
        return np.rad2deg(self.solar)

    @cached_property
    def _get_demission(self):
        return np.rad2deg(self.emission)

    def __call__(self):
        print("Phase: {0},\nIncidence: {1}\nEmission: {2}".format(self.dphase,
                                                                  self.dsolar,
                                                                  self.demission))
        
class Coords(HasTraits):
    lon = Float
    lat = Float
    radius = Float
    dlon = Property(depends_on='lon')
    dlat = Property(depends_on='lat')
    deglon = dlon
    deglat = dlat
    
    @classmethod
    def fromtuple(cls, args, **traits):
        return cls(radius=args[0],lon=args[1],lat=args[2], **traits)

    @cached_property
    def _get_dlon(self):
        dlon = np.rad2deg(self.lon)
        # force 360 eastern longitude:
        if dlon < 0:
            dlon = 360 - abs(dlon)
        return dlon 
        
    @cached_property       
    def _get_dlat(self):
        return np.rad2deg(self.lat)

                
class Spicer(HasTraits):
    # Constants
    method = Str('Near point:ellipsoid')
    corr = Str('LT+S')
    
    # 'Constants' set by child class
    ref_frame = Str
    instrument = Str
    instrument_id = Property# (depends_on = 'instrument')
    obs = Str
    target = Str
    target_id = Property# (depends_on = 'target')
    radii = Property# (depends_on = 'target')
    north_pole = Property
    south_pole = Property
    
    # Init Parameters and their dependents
    time = Date
    utc = Property(depends_on = 'time')
    et = Property(depends_on = 'utc')
    l_s = Property# (depends_on = ['et', 'target'])
    # should actually be target_center_to_sun, but i don't do this distinction yet
    center_to_sun = Property(depends_on = 'et' )
    solar_constant = Property# (depends_on ='center_to_sun')
    subsolar = Property
    
    # surface point related attributes
    spoint_set = Bool
    spoint = Tuple
    coords = Property
    srfvec = Property
    snormal = Property# (depends_on = 'spoint')
    sun_direction = Property(depends_on = ['spoint', 'et', 'center_to_sun'])
    illum_angles = Property# (depends_on = ['et','snormal'])
    local_soltime = Property# (depends_on = ['spoint','et'])
    to_north = Property
    to_south = Property
    F_flat = Property# (depends_on = ['solar_constant','illum_angles'])
    tilt = Range(low=0.0, high = 90.0)
    aspect = Range(low=0.0, high=360.0)
    tilted_normal = Property# (depends_on = ['snormal','tilt'])
    tilted_rotated_normal = Property# (depends_on = ['spoint','tilted_normal','aspect'])
    F_tilt = Property# (depends_on = ['solar_constant','illum_angles',
                                    # 'sun_direction', 'tilted_normal'])
    F_aspect = Property# (depends_on = ['solar_constant','illum_angles',
                                      # 'sun_direction','tilted_rotated_normal'])
    
    def __init__(self, time=None):
        super(Spicer, self).__init__()
        if time is None:
            self.time = dt.datetime.now()
        else:
            self.time = tparser.parse(time)
            
    def goto_ls_0(self):
        self.utc = '2011-09-13T14:24:33.733548'
        
    def _get_utc(self):
        return self.time.isoformat()

    def _set_utc(self, utc):
        self.time = tparser.parse(utc)
        
    def _get_et(self):
        return spice.utc2et(self.utc)

    def _get_target_id(self):
        return spice.bodn2c(self.target)

    def _get_radii(self):
        _, radii = spice.bodvrd(self.target, "RADII",3)
        return Radii(*radii)

    def _get_solar_constant(self):
        dist = spice.vnorm(self.center_to_sun)
        # SPICE returns in [km] !!
        return L_sol / (4 * np.pi * (dist * 1e3)**2)
        
    def _get_instrument_id(self):
        if not self.instrument:
            print("Instrument is not set yet.")
            return
        return spice.bodn2c(self.instrument)
        
    def _get_pole(self, factor=1):
        return (0.0, 0.0, factor*self.radii.c)
        
    def _get_north_pole(self):
        return self._get_pole()

    def _get_south_pole(self):
        return self._get_pole(-1)    
        
    def set_spoint_by(self, func_str=None, lon=None, lat=None):
        """This executes the class method with the name stored in the dict.
        
        ... and sets attribute spoint to the first item of the return.
        This works because both sincpt and subpnt return spoint as first item.
        """
        if func_str is not None:
            if not self.instrument or not self.obs:
                print("Observer and/or instrument have to be set first.")
                return
            if func_str in 'subpnt':
                spoint = self.subpnt()[0]
            elif func_str in 'sincpt':
                spoint = self.sincpt()[0]
            else:
                raise Exception("No valid method recognized.")
        elif lon is not None and lat is not None:
            self.lon = lon
            self.lat = lat
            spoint = self.srfrec(lon, lat)
        self.spoint_set = True    
        self.spoint = spoint
        
    def srfrec(self, lon, lat, body=None):
        """Convert planetocentric longitude and latitude of a surface point on a
        specified body to rectangular coordinates.
        
        Input of angles in degrees, conversion is done here.
        If the body is not a SPICE ID, it will be converted.
        >>> mspice = MarsSpicer()
        >>> print('{0:g} {1:g} {2:g}'.format(*mspice.srfrec(0,85)))
        294.268 0 3363.5
        """
        if body is None:
            body = self.target_id
        if not str(body).isdigit():
            body = spice.bodn2c(body)
        return spice.srfrec(body, np.deg2rad(lon), np.deg2rad(lat))

    def getfov(self):
        # hardcoded 5 in PySPICE wrapper, hotfix to get around [] in bounds array
        return spice.getfov(self.instrument_id, 5)
        
    def sincpt(self):
        """Surface intercept point.
        
        Sets the spoint depending on the current active instrument's boresight.
        """
        # _ are dummy variables I don't need
        shape, frame, bsight, _, _ = self.getfov()
        self.bsight = bsight
        self.bsight_frame = frame
        return spice.sincpt("Ellipsoid", self.target, self.et, self.ref_frame,
                              self.corr, self.obs, frame, bsight)

    def subpnt(self):
        "output = (spoint, trgepoch, srfvec)"
        output = spice.subpnt(self.method, self.target, self.et, self.ref_frame, 
                              self.corr, self.obs)
        return output

    def _coords_default(self):
        return Coords.fromtuple((0,0,0))
        
    def _get_coords(self):
        if len(self.spoint) == 0:
            print("Surface point 'spoint' not set yet.")
            return
        return Coords.fromtuple(spice.reclat(self.spoint))

    def _get_snormal(self):
        if not self.spoint_set:
            print("Surface point was not defined yet.")
            return
        a, b, c = self.radii
        return spice.surfnm(a, b, c, self.spoint)
            
    def _get_center_to_sun(self):
        center_to_sun, lighttime = self.target_to_object("SUN")
        return center_to_sun
    
    @cached_property    
    def _get_sun_direction(self):
        return spice.vsub(self.center_to_sun, self.spoint)
    
    @cached_property
    def _get_srfvec(self):
        if self.obs is None:
            print("No observer has been set")
        else:
            output = spice.ilumin("Ellipsoid", self.target, self.et, self.ref_frame,
                                  self.corr, self.obs, self.spoint)
            return output[1]
            
    def _get_illum_angles(self):
        "Ilumin returns (trgepoch, srfvec, phase, solar, emission)"
        if self.obs is not None:
            output = spice.ilumin("Ellipsoid", self.target, self.et, self.ref_frame,
                                  self.corr, self.obs, self.spoint)
            return IllumAngles.fromtuple(output[2:]) 
        else:
            solar = spice.vsep(self.sun_direction, self.snormal)
            # leaving at 0 what I don't have
            return IllumAngles.fromtuple((0, solar, 0))
            
    def _get_F_flat(self):
        if self.illum_angles.dsolar > 90:
            return 0
        else:
            return self.solar_constant * math.cos(self.illum_angles.solar)
            
    def _get_local_soltime(self):
        return spice.et2lst(self.et, self.target_id, self.coords.lon, "PLANETOCENTRIC")
    
    def _get_l_s(self):
        return np.rad2deg(spice.lspcn(self.target, self.et, self.corr))
    
    def _get_subsolar(self):
        subsolar, _ = spice.nearpt(self.center_to_sun, *self.radii)
        return subsolar
        
    def target_to_object(self, object):
        """Object should be string of body, e.g. 'SUN'.
        
        Output has (object_vector[3], lighttime)
        # Potential TODO: spkezp would be faster, but it uses body codes instead of names
        """
        output = spice.spkpos(object, self.et, self.ref_frame, self.corr, self.target)
        return output
    
    def _get_to_north(self):
        return spice.vsub(self.north_pole, self.spoint)

    def _get_to_south(self):
        return spice.vsub(self.south_pole, self.spoint)

    def _get_tilted_normal(self):
        """
        Create a tilted normal vector for an inclined surface by self.tilt
        
        By default the tilt is applied to the snormal vector towards north.
        """
        axis = spice.vcrss(self.to_north, self.spoint) # cross product
        rotmat = make_axis_rotation_matrix(axis, np.radians(self.tilt))
        return np.matrix.dot(rotmat, self.snormal)
        
    def _get_flux(self, vector):
        diff_angle = spice.vsep(vector, self.sun_direction)
        if (self.illum_angles.dsolar > 90) or (np.degrees(diff_angle) > 90):
            return 0
        else:
            return self.solar_constant * math.cos(diff_angle)        
                    
    def _get_F_tilt(self):
        return self._get_flux(self.tilted_normal)        

    def _get_tilted_rotated_normal(self):
        """
        Rotate the tilted normal around the snormal to create an aspect angle.
        
        Angle should be in degrees.
        """
        rotmat = make_axis_rotation_matrix(self.snormal, np.radians(self.aspect))
        return np.matrix.dot(rotmat, self.tilted_normal)
        
    def _get_F_aspect(self):
        return self._get_flux(self.tilted_rotated_normal)
        
    def advance_time_by(self, secs):
        self.time += dt.timedelta(seconds=secs)
    
    def time_series(self, flux_name, dt, no_of_steps=None, delta_l_s=None, provide_times=None):
        """
        Provide time series of fluxes with a <dt> in seconds as sampling intervals.
        
        Parameters
        ----------
        flux_name : String. Decides which of flux vector attributes to integrate. 
            Should be one of ['F_flat','F_tilt','F_aspect']   
        dt : delta time for the time series, in seconds
        no_of_steps : number of steps to add to time series
        delta_l_s : Either this or <no_of_steps> needs to be provided. Decides about the 
            end of the loop.
        provide_times : Should be set to one of ['time','utc','et','l_s'] if wanted.
        
        Returns
        -------
        if provide_times == None:
            out : ndarray
            Array of evenly spaced flux values, given as E/(dt*m**2). 
            I.e. the internal fluxes are multiplied by dt.
        """
        saved_time = self.time
        times = []
        energies = []
        i = 0
        start_l_s = self.l_s
        accumulated_delta_l_s = 0
        if no_of_steps:
            criteria = (i < no_of_steps)
        else:
            criteria = (self.l_s < end_l_s)
        while criteria:
            i += 1
            if provide_times: times.append(getattr(self, provide_times))
            energies.append(getattr(self, flux_name) * dt)
            self.advance_time_by(dt)
            if no_of_steps:
                criteria = (i < no_of_steps)
            else:
                criteria = (self.l_s < end_l_s)
                
        self.time = saved_time
        if provide_times: return (np.array(times), np.array(energies))
        else: return np.array(energies)
                    
    def compute_azimuth(self, oP, pixel_res = 0.5):
        """
        Compute the azimuth in degrees of another Point instance <oP>.
        
        Not finished yet!!
        """
        poB = spice.vsub(self.subsolar, self.spoint)
        upoB = spice.vhat(poB)
        scale = pixel_res/0.5/2.0
        supoB = spice.vscl(scale, upoB)
        nB = spice.vadd(self.spoint, supoB)
        nB = spice.vhat(nB)
        nB = spice.vscl(self.coords.radius, nB)
        nrad, nlon, nlat = spice.reclat(nB)
        
            
class EarthSpicer(Spicer):
    target = 'EARTH'
    ref_frame = 'IAU_EARTH'
    obs = Enum([None])
    instrument = Enum([None])
    def __init__(self, time=None, obs=None, inst=None):
        super(EarthSpicer, self).__init__(time)
        self.obs = obs
        self.instrument = inst
    
class MercSpicer(Spicer):
    target = 'MERCURY'
    ref_frame = 'IAU_MERCURY'
    obs = Enum([None])
    instrument = Enum([None])
    def __init__(self, time=None, obs=None, inst=None):
        super(MercSpicer, self).__init__(time)
        self.obs = obs
        self.instrument = inst
        
class MarsSpicer(Spicer):
    target = 'MARS'
    ref_frame = 'IAU_MARS'
    obs = Enum([None, 'MRO','MGS','MEX'])
    instrument = Enum([None,'MRO_HIRISE','MRO_CRISM','MRO_CTX'])
    # Coords dictionary to store often used coords
    location_coords = dict(inca=(220.09830399469547, 
                                  -440.60853011059214, 
                                  -3340.5081261541495))

    def __init__(self, time=None, obs=None, inst=None):
        """ Initialising MarsSpicer class.
        
        >>> spice.furnsh(metakernel_paths[2])
        >>> mspicer = MarsSpicer(time='2007-02-16T17:45:48.642')
        >>> mspicer.set_spoint_by('sinc')
        Observer and/or instrument have to be set first.
        >>> dummy = mspicer.set(obs='MRO', instrument='MRO_HIRISE')
        >>> mspicer.set_spoint_by('sinc')
        >>> print('Incidence angle: {0:g}'.format(mspicer.illum_angles.dsolar))
        Incidence angle: 87.6614

        >>> mspicer = MarsSpicer(time='2007-01-27T12:00:00')
        >>> mspicer.goto('inca')
        >>> print('Incidence angle: {0:g}'.format(mspicer.illum_angles.dsolar))
        Incidence angle: 87.3537
        
        >>> mspicer = MarsSpicer(time='2007-01-27T12:00:00')
        >>> mspicer.set_spoint_by(lon=300, lat = -80)
        >>> print('Incidence angle: {0:g}'.format(mspicer.illum_angles.dsolar))
        Incidence angle: 85.8875
        """
        super(MarsSpicer, self).__init__(time)
        self.obs = obs
        self.instrument = inst
        
    def goto(self, loc_string):
        self.spoint_set = True
        self.spoint = self.location_coords[loc_string.lower()]

def plot_times():
    time1 = tparser.parse(mspicer.local_soltime[4])
    time2 = time1 + dt.timedelta(1) # adding 1 day
    delta = dt.timedelta(minutes = 30)
    times = drange(time1, time2, delta)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for time in times:
        mspicer.time += delta
    ax.plot_date(times, angles)
    fig.autofmt_xdate()
    plt.show()
    
def test_time_series():
    mspice = MarsSpicer()
    mspice.goto_ls_0()
    mspice.set_spoint_by(lat=-84, lon=0)
    mspice.tilt = 15
    mspice.aspect = 90
    mspice.advance_time_by(24*3600*356)
    utc = mspice.utc
    timestep = 600
    no_of_steps = 2000
    times, to_east = mspice.time_series('F_aspect', timestep, no_of_steps, provide_times='l_s')
    mspice.utc = utc
    flat = mspice.time_series('F_flat', timestep, no_of_steps)
    mspice.utc = utc
    tilted = mspice.time_series('F_tilt', timestep, no_of_steps)
    mspice.utc = utc
    mspice.aspect = 270
    to_west = mspice.time_series('F_aspect', timestep, no_of_steps)
    plt.plot(times, flat, '*-', label='flat')
    plt.plot(times, tilted, '*-', label='tilted')
    plt.plot(times, to_east, '*-', label='to_east')
    plt.plot(times, to_west, '*-', label = 'to_west')
    plt.legend()
    plt.show()
    
def test_phase():
    mspice = MarsSpicer()
    mspice.utc = '2011-05-24T00:58:08.402'
    mspice.obs = 'MRO'
    mspice.instrument = 'MRO_HIRISE'
    mspice.set_spoint_by('sincpt')
    print("Phase: %f" % np.degrees(spice.vsep(spice.vminus(mspice.srfvec), mspice.sun_direction)))
    print("Inc: %f" % np.degrees(spice.vsep(mspice.spoint, mspice.sun_direction)))
    print("Emis: %f" % np.degrees(spice.vsep(mspice.spoint, spice.vminus(mspice.srfvec))))
    
def main():
    mspicer = MarsSpicer()
    mspicer.set_spoint_by(lat=85, lon=0)
    print("Set mspicer to 85N, 0E.")
    print("Local soltime: {0}".format(mspicer.local_soltime[3]))
    print("L_s: {0}".format(mspicer.l_s))
    print("Incidence angle: {0:g}".format(mspicer.illum_angles.dsolar))
    print("F_flat: {0:g}".format(mspicer.F_flat))
    mspicer.tilt = 30
    mspicer.aspect = 180
    print("F_tilt: {0:g}".format(mspicer.F_tilt))
    print("Angle between trnormal and sun: {0}".format(np.degrees(spice.vsep(mspicer.tilted_rotated_normal,
                                                                  mspicer.sun_direction))))
    print("F_aspect: {0:g}".format(mspicer.F_aspect))
    l_s, energies = mspicer.time_series('F_flat', 3600, no_of_steps=100, provide_times='l_s')
    energies_aspect = mspicer.time_series('F_aspect', 3600, no_of_steps=100)
    l_s10, energies_10ls = mspicer.time_series('F_aspect', 3600, delta_l_s=10, provide_times='l_s')
    plt.plot(l_s, energies, label='flat',linewidth=2)
    plt.plot(l_s, energies_aspect, label='aspect: 180',linewidth=2)
    plt.figure()
    plt.plot(l_s10, energies_10ls, label='until delta_l_s=2')
    print('sum over energies_10ls: {0}'.format((energies_10ls[:-1].sum()+energies_10ls[1:].sum())/2.0))
    plt.legend()
    plt.show()
     
if __name__ == '__main__':
    # import doctest
    # doctest.testmod()
    # test_time_series()
    test_phase()
    # mspice = MarsSpicer()
    # mspice.goto('inca')
    # mspice.configure_traits()
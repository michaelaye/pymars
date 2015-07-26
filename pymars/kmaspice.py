from __future__ import division, print_function
try:
    import SpiceyPy as spice
except ImportError:
    import spice
from collections import namedtuple
import numpy as np
from traits.api import HasTraits, Str, Float, Enum, Date, Property, \
    Tuple, Range, cached_property, Bool
import datetime as dt
import dateutil.parser as tparser
import matplotlib.pyplot as plt
import math
import os
import sys

###
### SETUP
###
L_sol = 3.839e26  # [Watt]

KERNEL_DIR = os.path.join(os.environ['HOME'],
                          'Dropbox',
                          'SternchenAndMe',
                          'SPICE_kernels')

# pure planetary bodies meta-kernel without spacecraft data
minimum_kernel_list = ['lsk/naif0011.tls',
                       'pck/pck00010.tpc',
                       'spk/de430.bsp',
                       ]
for kernel in minimum_kernel_list:
    spice.furnsh(os.path.join(KERNEL_DIR, kernel))


# simple named Radii structure, offering Radii.a Radii.b and Radii.c
Radii = namedtuple('Radii', 'a b c')


###
### helper functions
###
def load_planet_masses_kernel():
    spice.furnsh(os.path.join(KERNEL_DIR,
                              'pck/de403-masses.tpc'))


def calc_fractional_day(time_tuple):
    hour, minute, second = time_tuple[:3]
    fraction = float(minute)/60 + float(second)/3600
    return hour + fraction


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
    skew = np.array([[0,     d[2],  -d[1]],
                     [-d[2],    0,   d[0]],
                     [d[1], -d[0],     0]], dtype=np.float64)

    mtx = ddt + math.cos(angle) * (eye - ddt) + math.sin(angle) * skew
    return mtx


##
### Helper Classes
###
class IllumAngles(HasTraits):
    phase = Float
    solar = Float
    emission = Float
    dphase = Property(depends_on='phase')
    dsolar = Property(depends_on='solar')
    demission = Property(depends_on='emission')

    @classmethod
    def fromtuple(cls, args, **traits):
        return cls(phase=args[0], solar=args[1], emission=args[2], **traits)

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
        print("Phase: {0},\nIncidence: {1}\nEmission: {2}"
              .format(self.dphase, self.dsolar, self.demission))


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
        return cls(radius=args[0], lon=args[1], lat=args[2], **traits)

    @cached_property
    def _get_dlon(self):
        dlon = np.rad2deg(self.lon)
        # force 360 eastern longitude:
        if dlon < 0:
            dlon += 360.0
        return dlon

    @cached_property
    def _get_dlat(self):
        return np.rad2deg(self.lat)


###
### Main class
###
class Spicer(HasTraits):
    """Main class for KMAspice.py

    All other planetary body classes inherit from this class.
    """
    # Constants
    method = Str('Near point:ellipsoid')
    corr = Str('LT+S')

    # 'Constants' set by child class
    ref_frame = Str
    instrument = Str
    instrument_id = Property  # (depends_on = 'instrument')
    obs = Str
    target = Str
    target_id = Property  # (depends_on = 'target')
    radii = Property  # (depends_on = 'target')
    north_pole = Property
    south_pole = Property

    # Init Parameters and their dependents
    time = Date
    utc = Property(depends_on='time')
    et = Property(depends_on='utc')
    l_s = Property  # (depends_on = ['et', 'target'])
    # should actually be target_center_to_sun,
    # but i don't do this distinction yet
    center_to_sun = Property(depends_on='et')
    solar_constant = Property  # (depends_on ='center_to_sun')
    subsolar = Property

    # surface point related attributes
    spoint_set = Bool
    spoint = Tuple
    coords = Property
    srfvec = Property
    snormal = Property  # (depends_on = 'spoint')
    sun_direction = Property(depends_on=['spoint', 'et', 'center_to_sun'])
    illum_angles = Property  # (depends_on = ['et','snormal'])
    local_soltime = Property  # (depends_on = ['spoint','et'])
    fractional_local_time = Property
    to_north = Property
    to_south = Property
    F_flat = Property  # (depends_on = ['solar_constant','illum_angles'])
    tilt = Range(low=0.0, high=90.0)
    aspect = Range(low=0.0, high=360.0)
    tau = Float(0.0)
    tilted_normal = Property  # (depends_on = ['snormal','tilt'])
    tilted_rotated_normal = Property
                # (depends_on = ['spoint','tilted_normal','aspect'])
    F_tilt = Property  # (depends_on = ['solar_constant','illum_angles',
                                    # 'sun_direction', 'tilted_normal'])
    F_aspect = Property  # (depends_on = ['solar_constant','illum_angles',
                                # 'sun_direction','tilted_rotated_normal'])

    def __init__(self, time=None):
        super(Spicer, self).__init__()
        if time is None:
            self.time = dt.datetime.now()
        else:
            self.time = tparser.parse(time)
        spice.furnsh("/Users/klay6683/Dropbox/NotPublic/spice/cosp_1000_040701_040701/cas_2004_v21_040701_040701.tm")

    def goto_ls_0(self):
        self.utc = '2011-09-13T14:24:33.733548'

    def _get_utc(self):
        return self.time.isoformat()

    def _set_utc(self, utc):
        self.time = tparser.parse(utc)

    def _get_et(self):
        return spice.utc2et(self.utc)

    def get_utc_from_et(self, et):
        return spice.et2utc(et, "ISOC", 14)

    def _get_target_id(self):
        return spice.bodn2c(self.target)

    def _get_radii(self):
        _, radii = spice.bodvrd(self.target, "RADII", 3)
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
            # removing these, because they should depend on spoint,
            # but they don't
            # self.lon = lon
            # self.lat = lat
            spoint = self.srfrec(lon, lat).tolist()
        self.spoint_set = True
        self.spoint = spoint

    def srfrec(self, lon, lat, body=None):
        """Convert lon/lat to rectangular coordinates.

        Convert planetocentric longitude and latitude of a surface point on a
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
        # hardcoded 5 in PySPICE wrapper,
        # hotfix to get around [] in bounds array
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
        output = spice.subpnt(self.method, self.target, self.et,
                              self.ref_frame, self.corr, self.obs)
        return output

    def _coords_default(self):
        return Coords.fromtuple((0, 0, 0))

    def _get_coords(self):
        if not self.spoint_set:
            raise SPointNotSetError
        return Coords.fromtuple(spice.reclat(self.spoint))

    def _get_snormal(self):
        if not self.spoint_set:
            raise SPointNotSetError
        a, b, c = self.radii
        return spice.surfnm(a, b, c, self.spoint)

    def _get_center_to_sun(self):
        center_to_sun, lighttime = self.target_to_object("SUN")
        return center_to_sun

    @cached_property
    def _get_sun_direction(self):
        if not self.spoint_set:
            raise SPointNotSetError
        return spice.vsub(self.center_to_sun, self.spoint)

    @cached_property
    def _get_srfvec(self):
        if self.obs is None:
            raise ObserverNotSetError
        else:
            output = spice.ilumin("Ellipsoid", self.target, self.et,
                                  self.ref_frame, self.corr, self.obs,
                                  self.spoint)
            return output[1]

    def _get_illum_angles(self):
        "Ilumin returns (trgepoch, srfvec, phase, solar, emission)"
        if self.obs is not None:
            output = spice.ilumin("Ellipsoid", self.target, self.et,
                                  self.ref_frame, self.corr, self.obs,
                                  self.spoint)
            return IllumAngles.fromtuple(output[2:])
        else:
            solar = spice.vsep(self.sun_direction, self.snormal)
            # leaving at 0 what I don't have
            return IllumAngles.fromtuple((0, solar, 0))

    def _get_local_soltime(self):
        try:
            return spice.et2lst(self.et, self.target_id, self.coords.lon,
                                "PLANETOCENTRIC")
        except SPointNotSetError:
            raise

    def _get_fractional_local_time(self):
        return calc_fractional_day(self.local_soltime)

    def _get_l_s(self):
        return np.rad2deg(spice.lspcn(self.target, self.et, self.corr))

    def _get_subsolar(self):
        #normalize surface point vector:
        uuB = spice.vhat(self.center_to_sun)

        # receive subsolar point in IAU_MARS rectangular coords
        # the *self.radii unpacks the Radii object into 3 arguments.
        v_subsolar = spice.surfpt((0, 0, 0), uuB, *self.radii)

        return v_subsolar

    def target_to_object(self, object):
        """Object should be string of body, e.g. 'SUN'.

        Output has (object_vector[3], lighttime)
        # Potential TODO: spkezp would be faster, but it uses body codes
        instead of names
        """
        output = spice.spkpos(object, self.et, self.ref_frame, self.corr,
                              self.target)
        return output

    def _get_to_north(self):
        if not self.spoint_set:
            raise SPointNotSetError
        return spice.vsub(self.north_pole, self.spoint)

    def _get_to_south(self):
        if not self.spoint_set:
            raise SPointNotSetError
        return spice.vsub(self.south_pole, self.spoint)

    def _get_tilted_normal(self):
        """
        Create a tilted normal vector for an inclined surface by self.tilt

        By default the tilt is applied to the snormal vector towards north.
        """
        if not self.spoint_set:
            raise SPointNotSetError
        axis = spice.vcrss(self.to_north, self.spoint)  # cross product
        rotmat = make_axis_rotation_matrix(axis, np.radians(self.tilt))
        return np.matrix.dot(rotmat, self.snormal)

    def _get_F_flat(self):
        # if self.illum_angles.dsolar > 90:
        #     return 0
        # else:
        #     return self.solar_constant * math.cos(self.illum_angles.solar)
        return self._get_flux(self.snormal)

    def _get_flux(self, vector):
        diff_angle = spice.vsep(vector, self.sun_direction)
        if (self.illum_angles.dsolar > 90) or (np.degrees(diff_angle) > 90):
            return 0
        else:
            return (self.solar_constant * math.cos(diff_angle) *
                    math.exp(-self.tau/math.cos(self.illum_angles.solar)))

    def _get_F_tilt(self):
        return self._get_flux(self.tilted_normal)

    def _get_tilted_rotated_normal(self):
        """
        Rotate the tilted normal around the snormal to create an aspect angle.

        Angle should be in degrees.
        """
        rotmat = make_axis_rotation_matrix(self.snormal,
                                           np.radians(self.aspect))
        return np.matrix.dot(rotmat, self.tilted_normal)

    def _get_F_aspect(self):
        return self._get_flux(self.tilted_rotated_normal)

    def advance_time_by(self, secs):
        self.time += dt.timedelta(seconds=secs)

    def time_series(self, flux_name, dt, no_of_steps=None, provide_times=None):
        """
        Provide time series of fluxes with a <dt> in seconds as sampling
        intervals.

        Parameters
        ----------
        flux_name :
            String. Decides which of flux vector attributes to integrate.
            Should be one of ['F_flat','F_tilt','F_aspect']
        dt :
            delta time for the time series, in seconds
        no_of_steps :
            number of steps to add to time series
        provide_times :
            Should be set to one of ['time','utc','et','l_s'] if wanted.

        Returns
        -------
        if provide_times == None:
            out : ndarray
            Array of evenly spaced flux values, given as E/(dt*m**2).
            I.e. the internal fluxes are multiplied by dt.
        else:
            out : (ndarray, ndarray)
            Tuple of 2 arrays, out[0] being the times, out[1] the fluxes
        """
        saved_time = self.time
        times = []
        energies = []
        i = 0
        criteria = (i < no_of_steps)
        while criteria:
            i += 1
            if provide_times:
                times.append(getattr(self, provide_times))
            energies.append(getattr(self, flux_name) * dt)
            self.advance_time_by(dt)
            criteria = (i < no_of_steps)

        self.time = saved_time
        if provide_times:
            return (np.array(times), np.array(energies))
        else:
            return np.array(energies)

    def point_towards_sun(self, pixel_res=0.5):
        """
        Compute the solar azimuth.

        Pixel resolution is required to stay within one pixel of the origin
        point
        """
        # Check if surface point spoint was set
        if not self.spoint_set:
            raise SPointNotSetError
        # Get the difference vector poB=subsolar-origin with its tail at origin
        # and its head at the subsolar point
        poB = spice.vsub(self.subsolar, self.spoint)

        # get pixel scale in km/pixel and then divide by 2 to insure to stay
        # within a pixel of the origin point
        scale = (pixel_res/1000.0)/2.0

        # the difference vector cuts through the body,
        # we need the tangent vector
        # to the surface at the origin point. vperp receives the perpendicular
        # component of the poB towards the spoint vector
        hpoB = spice.vperp(poB, self.spoint)
        # unitize the tangent vector and then scale it to within a pixel of the
        # origin point
        upoB = spice.vhat(hpoB)
        spoB = spice.vscl(scale, upoB)

        # Compute the new point in body fixed. This point will be within a
        # pixel of the origin but in the same direction as the requested la/lon
        # of the point of interest, i.e. the subsolar point
        nB = spice.vadd(self.spoint, spoB)

        coords = Coords.fromtuple(spice.reclat(nB))
        return coords.dlon, coords.dlat


class EarthSpicer(Spicer):
    target = 'EARTH'
    ref_frame = 'IAU_EARTH'
    obs = Enum([None])
    instrument = Enum([None])

    def __init__(self, time=None, obs=None, inst=None):
        super(EarthSpicer, self).__init__(time)
        self.obs = obs
        self.instrument = inst


class MoonSpicer(Spicer):
    target = 'MOON'
    ref_frame = 'IAU_MOON'
    obs = Enum([None])
    instrument = Enum([None])

    def __init__(self, time=None, obs=None, inst=None):
        super(MoonSpicer, self).__init__(time)
        self.obs = obs
        self.instrument = inst


class SaturnSpicer(Spicer):
    target = 'SATURN'
    ref_frame = 'IAU_SATURN'
    obs = Enum([None])
    instrument = Enum([None])

    def __init__(self, time=None, obs=None, inst=None):
        super(SaturnSpicer, self).__init__(time)
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

class CeresSpicer(Spicer):
    target = 'CERES'
    ref_frame = 'IAU_CERES'
    obs = Enum([None])
    instrument = Enum([None])

    def __init__(self, time=None, obs=None, inst=None):
        super(CeresSpicer, self).__init__(time)
        self.obs = obs
        self.instrument = inst


class MarsSpicer(Spicer):
    target = 'MARS'
    ref_frame = 'IAU_MARS'
    obs = Enum([None, 'MRO', 'MGS', 'MEX'])
    instrument = Enum([None, 'MRO_HIRISE', 'MRO_CRISM', 'MRO_CTX'])
    # Coords dictionary to store often used coords
    location_coords = dict(inca=(220.09830399469547,
                                 -440.60853011059214,
                                 -3340.5081261541495))

    def __init__(self, time=None, obs=None, inst=None):
        """ Initialising MarsSpicer class.

        Demo:
        >>> mspicer = MarsSpicer(time='2007-02-16T17:45:48.642')
        >>> mspicer.goto('inca')
        >>> print('Incidence angle: {0:g}'.format(mspicer.illum_angles.dsolar))
        Incidence angle: 95.5388

        >>> mspicer = MarsSpicer(time='2007-01-27T12:00:00')
        >>> mspicer.set_spoint_by(lon=300, lat = -80)
        >>> print('Incidence angle: {0:g}'.format(mspicer.illum_angles.dsolar))
        Incidence angle: 85.8875
        """
        super(MarsSpicer, self).__init__(time)
        self.obs = obs
        self.instrument = inst

    def goto(self, loc_string):
        """Set self.spoint to coordinates as saved in location_coords.

        Currently available locations:
            'inca'  (call like so: mspicer.goto('inca'))
        """
        self.spoint_set = True
        self.spoint = self.location_coords[loc_string.lower()]


def get_current_l_s():
    ms = MarsSpicer()
    return round(ms.l_s, 1)


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
    delta_in_rad = spice.vsep(mspicer.tilted_rotated_normal,
                              mspicer.sun_direction)
    print("Angle between trnormal and sun: {0}"
          .format(np.degrees(delta_in_rad)))
    print("F_aspect: {0:g}".format(mspicer.F_aspect))
    l_s, energies = mspicer.time_series('F_flat',
                                        3600,
                                        no_of_steps=100,
                                        provide_times='l_s')
    energies_aspect = mspicer.time_series('F_aspect', 3600, no_of_steps=100)
    plt.plot(l_s, energies, label='flat', linewidth=2)
    plt.plot(l_s, energies_aspect, label='aspect: 180', linewidth=2)
    plt.legend()
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Launch me like this to see a test-run: python {0} test-run"
              .format(sys.argv[0]))
        sys.exit()
    if sys.argv[1] == 'test-run':
        main()
    else:
        print("Cannot deal with option {0}".format(sys.argv[1]))

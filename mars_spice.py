import spice
from collections import namedtuple
import numpy as np
from traits.api import HasTraits, Str, Int, Float, ListStr, Enum, Date, Property, \
    Tuple, Range, cached_property
import datetime as dt
import dateutil.parser as tparser
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, drange
from sunpy.sun.constants import luminosity as L_sol

# spice.furnsh('/Users/maye/Data/spice/mars/mro_2009_v06_090107_090110.tm')
# spice.furnsh('/Users/maye/Data/spice/mars/mro_2007_v07_070127_070128.tm')
# spice.furnsh('/Users/maye/Data/spice/mars/mro_2007_v07_070216_070217.tm')

spice.furnsh('mars.tm')
Coords = namedtuple('Coords', 'radius lon lat')
Radii = namedtuple('Radii', 'a b c')
IllumAngles = namedtuple('IllumAngles', 'phase solar emission')
    
class Spicer(HasTraits):
    # Constants
    method = Str('Near point:ellipsoid')
    corr = Str('LT+S')
    
    # 'Constants' set by child class
    ref_frame = Str
    instrument = Str
    instrument_id = Property(depends_on = 'instrument')
    obs = Str
    target = Str
    target_id = Property(depends_on = 'target')
    radii = Property(depends_on = 'target')
    solar_constant = Property(depends_on ='target')
    
    # Init Parameters and their dependents
    time = Date
    utc = Property(depends_on = 'time')
    et = Property(depends_on = 'utc')
    l_s = Property(depends_on = 'et')
    
    # surface point related attributes
    spoint = Tuple
    coords = Property(depends_on = 'spoint')
    dcoords = Property(depends_on = 'coords')
    snormal = Property(depends_on = 'spoint')
    illum_angles = Property(depends_on = ['spoint','et'])
    dillum_angles = Property(depends_on = 'illum_angles')
    local_soltime = Property(depends_on = ['spoint','et'])
    
    def __init__(self, time=None):
        if time is None:
            self.time = dt.datetime.now()
        else:
            self.time = tparser.parse(time)
            
    def _get_utc(self):
        return self.time.isoformat()

    @cached_property
    def _get_et(self):
        return spice.utc2et(self.utc)

    @cached_property
    def _get_target_id(self):
        return spice.bodn2c(self.target)

    @cached_property
    def _get_radii(self):
        _, radii = spice.bodvrd(self.target, "RADII",3)
        return Radii(*radii)

    @cached_property
    def _get_solar_constant(self):
        center_to_sun, lighttime = self.target_to_object("SUN")
        dist = spice.vnorm(center_to_sun)
        # SPICE returns in [km] !!
        return L_sol / (4 * np.pi * (dist * 1e3)**2)
        
    @cached_property
    def _get_instrument_id(self):
        if not self.instrument:
            print("Instrument is not set yet.")
            return
        return spice.bodn2c(self.instrument)
        
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
                self.spoint = self.subpnt()[0]
            elif func_str in 'sincpt':
                self.spoint = self.sincpt()[0]
            else:
                print("No valid method recognized.")
        elif (lon and lat):
            self.lon = lon
            self.lat = lat
            self.spoint = self.srfrec(lon, lat)
            
    def srfrec(self, lon, lat, body=None):
        """Convert planetocentric longitude and latitude of a surface point on a
        specified body to rectangular coordinates.
        
        Input of angles in degrees, conversion is done here.
        If the body is not a SPICE ID, it will be converted.
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
        return spice.sincpt("Ellipsoid", self.target, self.et, self.ref_frame,
                              self.corr, self.obs, frame, bsight)

    def subpnt(self):
        "output = (spoint, trgepoch, srfvec)"
        output = spice.subpnt(self.method, self.target, self.et, self.ref_frame, 
                              self.corr, self.obs)
        return output

    def _get_coords(self):
        if len(self.spoint) == 0:
            print("Surface point 'spoint' not set yet.")
            return
        return Coords(*spice.reclat(self.spoint))
        
    def _get_dcoords(self):
        dlon = np.rad2deg(self.coords.lon)
        if dlon < 0:
            dlon = 360 - abs(dlon)
        dlat = np.rad2deg(self.coords.lat)
        return Coords(self.coords.radius, dlon, dlat)
        
    @cached_property
    def _get_snormal(self):
        a, b, c = self.radii
        return spice.surfnm(a, b, c, self.spoint)
        
    @cached_property
    def _get_illum_angles(self):
        "Ilumin returns (trgepoch, srfvec, phase, solar, emission)"
        if self.obs is not None:
            output = spice.ilumin("Ellipsoid", self.target, self.et, self.ref_frame,
                                  self.corr, self.obs, self.spoint)
            return IllumAngles(*output[2:]) 
        else:
            center_to_sun, lighttime = self.target_to_object("SUN")
            surf_to_sun = spice.vsub(center_to_sun, self.spoint)
            solar = spice.vsep(surf_to_sun, self.snormal)
            # leaving at 0 what I don't have
            return IllumAngles(0, solar, 0)
            
    def _get_dillum_angles(self):
        dangles = []
        for angle in self.illum_angles:
            dangles.append(np.rad2deg(angle))
        return IllumAngles(*dangles)

    @cached_property
    def _get_local_soltime(self):
        lst = spice.et2lst(self.et, self.target_id, self.coords.lon, "PLANETOCENTRIC")
        return lst
    
    @cached_property
    def _get_l_s(self):
        return np.rad2deg(spice.lspcn(self.target, self.et, self.corr))
    
    @cached_property
    def get_subsolar(self):
        subsolar, _, _ = spice.subslr(self.method, self.target, self.et, self.ref_frame,
                                      self.corr, self.obs)
        return subsolar
        
    def target_to_object(self, object):
        """Object should be string of body, e.g. 'SUN'.
        
        Output has (object_vector[3], lighttime)
        """
        output = spice.spkpos(object, self.et, self.ref_frame, self.corr, self.target)
        return output

class EarthSpicer(Spicer):
    target = 'EARTH'
    ref_frame = 'IAU_EARTH'
    
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
        
        >>> from mars_spice import MarsSpicer
        >>> mspicer = MarsSpicer(time='2007-02-16T17:45:48.642')
        >>> mspicer.set_spoint_by('sinc')
        Observer and/or instrument have to be set first.
        >>> dummy = mspicer.set(obs='MRO', instrument='MRO_HIRISE')
        >>> mspicer.set_spoint_by('sinc')
        >>> print('Incidence angle: {0:g}'.format(mspicer.dillum_angles.solar))
        Incidence angle: 87.6614

        >>> mspicer = MarsSpicer(time='2007-01-27T12:00:00')
        >>> mspicer.goto('inca')
        >>> print('Incidence angle: {0:g}'.format(mspicer.dillum_angles.solar))
        Incidence angle: 87.3537
        
        >>> mspicer = MarsSpicer(time='2007-01-27T12:00:00')
        >>> mspicer.set_spoint_by(lon=300, lat = -80)
        >>> print('Incidence angle: {0:g}'.format(mspicer.dillum_angles.solar))
        Incidence angle: 85.8875
        """
        super(MarsSpicer, self).__init__(time)
        self.obs = obs
        self.instrument = inst
        
    def goto(self, loc_string):
        self.spoint = self.location_coords[loc_string.lower()]

def plot_times():
    angles = []
    time1 = tparser.parse(mspicer.local_soltime[4])
    time2 = time1 + dt.timedelta(1) # adding 1 day
    delta = dt.timedelta(minutes = 30)
    times = drange(time1, time2, delta)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for time in times:
        mspicer.time += delta
        mspicer.ilumin()
        angles.append(np.rad2deg(mspicer.solar))
    ax.plot_date(times, angles)
    fig.autofmt_xdate()
    plt.show()
    
if __name__ == '__main__':
    utc = '2007-01-28T21:12:55'
    mspicer = MarsSpicer(time=utc)
    print('Solar incidence: {0:g}'.format(mspicer.dsolar))
    print('Emission angle: {0:g}'.format(mspicer.demission))
    print('Phase angle: {0:g}'.format(mspicer.dphase))
    center_to_sun, lt = mspicer.mars_to_object("SUN")
    print(center_to_sun)
    surf_to_sun = spice.vsub(center_to_sun, mspicer.spoint)
    snormal = mspicer.surfnm()
    print("Diff: {0}".format(np.rad2deg(spice.vsep(surf_to_sun, snormal))))
    print(snormal)
        
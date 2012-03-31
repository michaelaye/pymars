import spice
import numpy as np
from traits.api import HasTraits, Str, Int, Float, ListStr, Enum, Date, Property, \
    Tuple
import datetime as dt
import dateutil.parser as tparser
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, drange

# spice.furnsh('mars.mk')
spice.furnsh('/Users/maye/Data/spice/mars/mro_2009_v06_090107_090110.tm')
spice.furnsh('/Users/maye/Data/spice/mars/mro_2007_v07_070127_070128.tm')
# spice.furnsh('/Users/maye/isis3/data/base/kernels/lsk/naif0009.tls')

class Spicer(HasTraits):
    timestr = Str
    target = Str
    target_ID = Property(depends_on = 'target')
    ref_frame = Str
    instrument = Str
    instrument_ID = Property(depends_on = 'instrument')
    method = Str('Near point:ellipsoid')
    corr = Str('LT+S')
    et = Float
    obs = Str
    time = Date
    utc = Property(depends_on = 'time')
    et = Property(depends_on = 'utc')
    spoint = Tuple
    lon = Float
    lat = Float
    dlon = Property(depends_on = 'lon')
    lat = Float
    dlat = Property(depends_on = 'lat')
    
    
    def __init__(self, time=None, target=None):
        if time is None:
            print('Uninitialised time. You still need to set it.')
        else:
            self.init_time(time)
        _, (self.a, self.b, self.c) = spice.bodvrd(target, "RADII",3)
    def _spoint_changed(self):
        self.reclat()
        self.surfnm()
        
    def surfnm(self):
        return spice.surfnm(self.a, self.b, self.c, self.spoint)
        
    def _get_dlon(self):
        dlon = np.rad2deg(self.lon)
        if dlon < 0:
            dlon = 360 - abs(dlon)
        return dlon
        
    def _get_dlat(self):
        return np.rad2deg(self.lat)
        
    def init_time(self,t):
        self.time = tparser.parse(t)

    def _get_utc(self):
        return self.time.isoformat()

    def _get_et(self):
        return spice.utc2et(self.utc)

    def _get_target_ID(self):
        return spice.bodn2c(self.target)

    def _get_instrument_ID(self):
        return spice.bodn2c(self.instrument)
        
    def subpnt(self):
        output = spice.subpnt(self.method, self.target, self.et, self.ref_frame, 
                              self.corr, self.obs)
        self.spoint, self.trgepoch, self.srfvec = output
        # call rectangular to latitudinal coords conv to keep lat, lon consistent
        return output

    def reclat(self):
        self.radius, self.lon, self.lat = spice.reclat(self.spoint)

    def ilumin(self):
        output = spice.ilumin("Ellipsoid", self.target, self.et, self.ref_frame,
                              self.corr, self.obs, self.spoint)
        self.trgepoch, self.srfvec, self.phase, self.solar, self.emission = \
            output
        self.dsolar = np.rad2deg(self.solar)
        self.demission = np.rad2deg(self.emission)
        self.dphase = np.rad2deg(self.phase)
        return output

    def srfrec(self, body, lon, lat):
        """Convert body to spice id if it's not a number.
        
        Input of angles in degrees, conversion is done here.
        """
        self.lon = lon
        self.lat = lat
        if not str(body).isdigit():
            self.body = spice.bodn2c(body)
        self.spoint = spice.srfrec(self.body, np.deg2rad(lon), np.deg2rad(lat))
        return self.spoint

    def et2lst(self):
        self.local_soltime = spice.et2lst(self.et, self.target_ID, self.lon, "PLANETOCENTRIC")
        return self.local_soltime
    
    def lspcn(self):
        return spice.lspcn(self.target_ID, self.et, self.corr)

    def sincpt(self):
        # hardcoded 5 in PySPICE wrapper, hotfix to get around [] in bounds array
        self.shape, self.frame, self.bsight, _, _ = spice.getfov(self.instrument_ID, 5)
        output = spice.sincpt("Ellipsoid", self.target, self.et, self.ref_frame,
                              self.corr, self.obs, self.frame, self.bsight)
        self.spoint, self.trgepoch, self.srfvec = output
        return self.spoint
        
    def subslr(self):
        subsolar, _, _ = spice.subslr(self.method, self.target, self.et, self.ref_frame,
                                      self.corr, self.obs)
        self.subsolar = subsolar
        return subsolar
        
        
class MarsSpicer(Spicer):
    target = 'MARS'
    ref_frame = 'IAU_MARS'
    obs = Enum(['MRO','MGS','MEX'])
    instrument = Enum(['MRO_HIRISE','MRO_CRISM','MRO_CTX'])
    def __init__(self, time=None, obs=None, inst=None):
        super(MarsSpicer, self).__init__(time, self.target)
        self.obs = 'MRO' if obs is None else obs
        self.instrument = 'MRO_HIRISE' if inst is None else inst
        self.target_id = spice.bodn2c(self.target)
    def mars_to_object(self, object):
        """Object should be string of body, e.g. 'SUN'.
        
        Output has (object_vector[3], lighttime)
        """
        output = spice.spkpos(object, self.et, self.ref_frame, self.corr, self.target)
        return output

if __name__ == '__main__':
    utc = '2007-01-28T21:12:55'
    mspicer = MarsSpicer(time=utc)
    # Inca City coords in Mars frame
    mspicer.sincpt()
    # mspicer.spoint = (220.09830399469547, -440.60853011059214, -3340.5081261541495)
    mspicer.ilumin()
    print('Solar incidence: {0:g}'.format(mspicer.dsolar))
    print('Emission angle: {0:g}'.format(mspicer.demission))
    print('Phase angle: {0:g}'.format(mspicer.dphase))
    center_to_sun, lt = mspicer.mars_to_object("SUN")
    print(center_to_sun)
    surf_to_sun = spice.vsub(center_to_sun, mspicer.spoint)
    snormal = mspicer.surfnm()
    print("Diff: {0}".format(np.rad2deg(spice.vsep(surf_to_sun, snormal))))
    print(snormal)
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
        
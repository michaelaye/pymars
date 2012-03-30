import spice
import numpy as np
from traits.api import HasTraits, Str, Float, ListStr, Enum, Date, Property
import datetime as dt
import dateutil.parser as tparser
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, drange

spice.furnsh('mars.mk')

class Spicer(HasTraits):
    timestr = Str
    target = Str
    ref_frame = Str
    method = Str('Near point:ellipsoid')
    corr = Str('LT+S')
    et = Float
    obs = Str
    time = Date
    utc = Property(depends_on = 'datetime')
    et = Property(depends_on = 'utc')
    def __init__(self, time=None):
        if time is None:
            print('Uninitialised time. You still need to set it.')
        else:
            self.init_time(time)
    def init_time(self,t):
        self.time = tparser.parse(t)
    def _get_utc(self):
        return self.time.isoformat()
    def _get_et(self):
        return spice.utc2et(self.utc)
    def subpnt(self):
        output = spice.subpnt(self.method, self.target, self.et, self.ref_frame, 
                              self.corr, self.obs)
        self.spoint, self.trgepoch, self.srfvec = output
        return output
    def ilumin(self):
        output = spice.ilumin("Ellipsoid", self.target, self.et, self.ref_frame,
                              self.corr, self.obs, self.spoint)
        self.trgepoch, self.srfvec, self.phase, self.solar, self.emission = \
            output
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
        self.lst = spice.et2lst(self.et, self.body, self.lon, "PLANETOCENTRIC")
        return self.lst
        
class MarsSpicer(Spicer):
    target = 'MARS'
    ref_frame = 'IAU_MARS'
    obs = Enum(['MRO','MGS','MEX'])
    def __init__(self, time=None, obs=None):
        super(MarsSpicer, self).__init__(time)
        self.obs = 'MRO' if obs is None else obs
        self.target_id = spice.bodn2c(self.target)


if __name__ == '__main__':
    utc = '7 Jan 2009 15:00'
    mspicer = MarsSpicer(time=utc)
    print(mspicer.srfrec('mars', 296, -81.3))
    print(mspicer.et2lst())
    mspicer.ilumin()
    print(np.rad2deg(mspicer.solar))
    angles = []
    time1 = mspicer.time
    time2 = mspicer.time + dt.timedelta(1)
    delta = dt.timedelta(minutes = 1)
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
        
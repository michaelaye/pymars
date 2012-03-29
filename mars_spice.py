import spice
import numpy as np
from traits.api import HasTraits, Str, Float, ListStr, Enum
import datetime as dt
import dateutil.parser as tparser

spice.furnsh('mars.mk')

class Spicer(HasTraits):
    timestr = Str
    target = Str
    ref_frame = Str
    method = Str('Near point:ellipsoid')
    corr = Str('LT+S')
    et = Float
    obs = Str
    def __init__(self, time=None):
        if time is None:
            print('Uninitialised time. You still need to set it.')
        else:
            self.init_time(time)
    def init_time(self,t):
        self.datetime = tparser.parse(t)
        self.utc = self.datetime.isoformat()
        self.et = spice.utc2et(self.utc)
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
                             
                             
class MarsSpicer(Spicer):
    target = 'MARS'
    ref_frame = 'IAU_MARS'
    obs = Enum(['MRO','MGS','MEX'])
    def __init__(self, time=None, obs=None):
        super(MarsSpicer, self).__init__(time)
        self.obs = 'MRO' if obs is None else obs


if __name__ == '__main__':
    utc = '2012-03-14T03:38:58.482'
    mspicer = MarsSpicer(time=utc)
    mspicer.subpnt()
    mspicer.ilumin()
    print(np.rad2deg(mspicer.solar))

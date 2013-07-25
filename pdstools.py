from pds.core.common import open_pds
from pds.core.parser import Parser
from math import cos, sin, acos, radians, degrees


def get_labels(fname):
    parser = Parser()
    return parser.parse(open_pds(fname))


def print_root_and_groups(labels):
    for key in labels.iterkeys():
        if hasattr(labels[key], 'keys'):
            print
            print key
            print '-----------------'
            print labels[key].keys()
            print '================='
        else:
            print 'Root item:', key, labels[key]


def get_time(labels=None, fname=None):
    if fname is not None:
        labels = get_labels(fname)
    return labels['TIME_PARAMETERS']['START_TIME']


def get_angle(labels, group, key):
    value = labels[group][key]
    return float(value.split()[0])


def get_north_azimuth(labels=None, fname=None):
    if fname is not None:
        labels = get_labels(fname)
    return get_angle(labels, 'VIEWING_PARAMETERS', 'NORTH_AZIMUTH')


def get_incidence(labels=None, fname=None):
    if fname is not None:
        labels = get_labels(fname)
    return get_angle(labels, 'VIEWING_PARAMETERS', 'INCIDENCE_ANGLE')


def get_emission(labels=None, fname=None):
    if fname is not None:
        labels = get_labels(fname)
    return get_angle(labels, 'VIEWING_PARAMETERS', 'EMISSION_ANGLE')


def get_phase(labels=None, fname=None):
    if fname is not None:
        labels = get_labels(fname)
    return get_angle(labels, 'VIEWING_PARAMETERS', 'PHASE_ANGLE')


def get_sub_sol_azi(labels=None, fname=None):
    if fname is not None:
        labels = get_labels(fname)
    return get_angle(labels, 'VIEWING_PARAMETERS', 'SUB_SOLAR_AZIMUTH')


def get_local_solar_time(labels=None, fname=None):
    if fname is not None:
        labels = get_labels(fname)
    return get_angle(labels, 'VIEWING_PARAMETERS', 'LOCAL_TIME')


def get_mean_lat(labels):
    maxlat = get_angle(labels, 'IMAGE_MAP_PROJECTION', 'MAXIMUM_LATITUDE')
    minlat = get_angle(labels, 'IMAGE_MAP_PROJECTION', 'MINIMUM_LATITUDE')
    return (maxlat + minlat) / 2.0


def get_mean_lon(labels):
    west_lon = get_angle(labels, 'IMAGE_MAP_PROJECTION', 'WESTERNMOST_LONGITUDE')
    east_lon = get_angle(labels, 'IMAGE_MAP_PROJECTION', 'EASTERNMOST_LONGITUDE')
    return (west_lon + east_lon) / 2.0


def get_sub_sc_azimuth(labels):
    inc = radians(get_incidence(labels))
    emis = radians(get_emission(labels))
    g = radians(get_phase(labels))
    cosa = cos(g) - (cos(inc) * cos(emis))
    cosa /= (sin(inc) * sin(emis))
    return degrees(acos(cosa))


class PDSLabel(object):
    """Deal with PDS labels via properties."""

    def __init__(self, fname):
        super(PDSLabel, self).__init__()
        self.fname = fname
        self.labels = get_labels(fname)
        self.map_projection = self.labels['IMAGE_MAP_PROJECTION']
        
    def get_float_val(self, val):
        return float(val.split()[0])
        
    @property
    def westmost(self):
        return self.get_float_val(self.map_projection['WESTERNMOST_LONGITUDE'])
    
    @property
    def eastmost(self):
        return self.get_float_val(self.map_projection['EASTERNMOST_LONGITUDE'])
        
    @property
    def maxlat(self):
        return self.get_float_val(self.map_projection['MAXIMUM_LATITUDE'])
        
    @property
    def minlat(self):
        return self.get_float_val(self.map_projection['MINIMUM_LATITUDE'])
        
    @property
    def local_soltime(self):
        return get_local_solar_time(labels=self.labels)
        
    @property
    def phase(self):
        return get_phase(labels=self.labels)
        
    @property
    def time(self):
        return get_time(labels=self.labels)
        
    @property
    def meanlon(self):
        return get_mean_lon(labels=self.labels)
        
    @property
    def meanlat(self):
        return get_mean_lat(labels=self.labels)
        
        
if __name__ == '__main__':
    fname = '/Users/maye/data/hirise/inca/ESP_022607_0985_RED.LBL'
    labels = get_labels(fname)
    # print_root_and_groups(labels)
    print get_north_azimuth(labels)

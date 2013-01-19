from pds.core.common import open_pds
from pds.core.parser import Parser

def get_labels(fname):
    parser = Parser()
    return parser.parse(open_pds(fname))
    
def print_root_and_groups(labels):
    for key in labels.iterkeys():
        if hasattr(labels[key],'keys'):
            print
            print key
            print '-----------------'
            print labels[key].keys()
            print '================='
        else:
            print 'Root item:',key, labels[key]
            
def get_angle(labels, group, key):
    value = labels[group][key]
    return float(value.split()[0])
    
def get_north_azimuth(labels=None, fname=None):
    if fname is not None:
        labels = get_pds_labels(fname)
    return get_angle(labels,'VIEWING_PARAMETERS','NORTH_AZIMUTH')
    
def get_time(labels=None, fname=None):
    if fname is not None:
        labels = get_pds_labels(fname)
    return get_angle(labels,'TIME_PARAMETERS','START_TIME')
    
def get_incidence(labels=None, fname=None):
    if fname is not None:
        labels = get_pds_labels(fname)
    return get_angle(labels,'VIEWING_PARAMETERS','INCIDENCE_ANGLE')

def get_emission(labels=None, fname=None):
    if fname is not None:
        labels = get_pds_labels(fname)
    return get_angle(labels,'VIEWING_PARAMETERS','EMISSION_ANGLE')

def get_phase(labels=None, fname=None):
    if fname is not None:
        labels = get_pds_labels(fname)
    return get_angle(labels,'VIEWING_PARAMETERS','PHASE_ANGLE')
    
def get_mean_lat(labels):
    maxlat = get_angle(labels,'IMAGE_MAP_PROJECTION','MAXIMUM_LATITUDE')
    minlat = get_angle(labels,'IMAGE_MAP_PROJECTION','MINIMUM_LATITUDE')
    return (maxlat+minlat)/2.0

def get_mean_lon(labels):
    west_lon = get_angle(labels,'IMAGE_MAP_PROJECTION','WESTERNMOST_LONGITUDE')
    east_lon = get_angle(labels,'IMAGE_MAP_PROJECTION','EASTERNMOST_LONGITUDE')
    return (west_lon+east_lon)/2.0
    
if __name__ == '__main__':
    fname = '/Users/maye/data/hirise/inca/ESP_022607_0985_RED.LBL'
    labels = get_pds_labels(fname)
    # print_root_and_groups(labels)
    print get_north_azimuth(labels)
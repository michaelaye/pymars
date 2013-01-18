from pds.core.common import open_pds
from pds.core.parser import Parser

def get_pds_labels(fname):
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
            
def get_north_azimuth(labels=None, fname=None):
    if fname is not None:
        labels = get_pds_labels(fname)
    value = labels['VIEWING_PARAMETERS']['NORTH_AZIMUTH']
    return float(value.split()[0])
    
if __name__ == '__main__':
    fname = '/Users/maye/data/hirise/inca/ESP_022607_0985_RED.LBL'
    labels = get_pds_labels(fname)
    # print_root_and_groups(labels)
    print get_north_azimuth(labels)
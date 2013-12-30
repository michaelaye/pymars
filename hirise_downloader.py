import urllib
import os
import sys
import xlrd

url_root = 'http://hirise-pds.lpl.arizona.edu/download/PDS/RDR'

def get_base_url(idString, color):
    """create base url from obs id"""
    sciencePhase, orbitString, targetCode = idString.split("_")
    lower = int(orbitString) / 100 * 100
    dirname = "_".join(["ORB", str(lower).zfill(6), str(lower + 99).zfill(6)])
    basename = idString + '_' + color + '.JP2'
    return '/'.join([url_root,sciencePhase,dirname,idString,basename])

# /ESP/ORB_012200_012299/ESP_012254_1065/ESP_012254_1065_RED.JP2

def get_file(url):
    local_path = os.path.basename(url)
    if os.path.exists(local_path):
        return "Local copy already exists."
    f = urllib.urlretrieve(url,local_path)
    if not f:
        return "Error. No object retrieved."
    else:
        return "Retrieved " + local_path
        
if __name__ == '__main__':
    try:
        # read in wanted color string as first argument
        color = sys.argv[1].upper()
    except:
        print 'Usage: {0} [red|color]'.format(os.path.basename(sys.argv[0]))
        sys.exit()
    # open excel workbook file
    wb = xlrd.open_workbook('./hireport_south_mars_zoo_v2_only_fans_short.xls')
    # get first worksheet
    sh = wb.sheet_by_index(0)
    # loop over rows
    for rownum in range(sh.nrows):
        # skip header row
        if rownum == 0: continue
        content = sh.cell(rownum,0).value
        # skip empty lines
        if not content: continue
        url = get_base_url(content, color)
        print get_file(url)
        


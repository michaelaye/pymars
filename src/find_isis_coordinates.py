#!/usr/bin/python2.6

'''
Created on Jul 14, 2009

@author: aye
'''
import parser

import sys
import os
from hirise_tools import *
from ISIS_Commands import *
import roi

# global for this module: which file extensions i should look for:
sExtensions = '.cal.norm.map.equ.mos.cub'

   # define an empty class, just to hold a set of parameters
class Params:
    pass
 
def get_rounded_int_str_from_value(sValue):
    return str(int(round(float(sValue))))

def get_rounded_str_from_value(sValue, iDigits):
    return str(round(float(sValue), iDigits))

def execute_mappt(params):
    """function to determine ground coords from sample/line.
    Results will be given in csv output file from ISIS mappt program."""
    sMAPPTcmd = ISIS_mappt()
    sSourcePath = getStoredPathFromID(params.sobsID) # DEST_BASE set in hirise_tools
    sCubePath = sSourcePath + params.sobsID + '_' + params.sCCDColour + sExtensions
    sMAPPTcmd.setInputPath(sCubePath)
    print "output-file for scan in prime image:", params.sMAPPTFile
    sMAPPTcmd.setOutputPath(params.sMAPPTFile)
    sMAPPTcmd.addParameters(['sample=' + params.sSample, 'line=' + params.sLine, 'type=image'])
    print sMAPPTcmd
    sMAPPTcmd.execute()

def use_mappt_latlon(params, coords):
    sMAPPTcmd = ISIS_mappt()
    sMAPPTcmd.setInputPath(params.sPath)
    sMAPPTcmd.setOutputPath(params.sMAPPTFile)
    sMAPPTcmd.addParameters(['longitude=' + coords.longitude])
    sMAPPTcmd.addParameters(['latitude=' + coords.latitude, 'type=ground'])
    print sMAPPTcmd
    sMAPPTcmd.execute()
  
def get_latlon_from_csv(params, coords):
    cmdGetKey = ISIS_getkey('PixelValue')
    cmdGetKey.setInputPath(params.sMAPPTFile)
    pixelValue = cmdGetKey.getKeyValue()
    if pixelValue == "Null":
        print "Starting Coordinate seems to have no valid pixel-value, please check"
        sys.exit(1)
    cmdGetKey.setParameters('Longitude')
    coords.longitude = cmdGetKey.getKeyValue()
    cmdGetKey.setParameters('Latitude')
    coords.latitude = cmdGetKey.getKeyValue()

def get_sample_line_from_csv(params, coords):
    cmd = ISIS_getkey('PixelValue')
    cmd.setInputPath(params.sMAPPTFile)
    coords.pixelValue = cmd.getKeyValue()
    cmd.setParameters('Sample')
    coords.sample = cmd.getKeyValue()
    cmd.setParameters('Line')
    coords.line = cmd.getKeyValue()

def find_coords(params):
    if params.extraTargetCode == '':
        print """found no extra target code, will only search for target code 
                of obsID \n"""
        params.extraTargetCode = 'ouk;ohuoenuiuc' #dummy extra target code
    
    print "searching..."
    # get subData in obsID in case i need it later
    params.sSciencePhase, params.sOrbit, params.sTargetCode = \
        params.sobsID.split('_')
    
    
    # use mappt on given file to create output file from where to read the 
    # lon/lat to search for
    params.sMAPPTFile = params.sobsID + '_mappt.csv'
    execute_mappt(params)
    print "done mapping"
    
    myCoords = Coordinates()
    myCoords.sample = params.sSample
    myCoords.line = params.sLine
    
    get_latlon_from_csv(params, myCoords)
    print "\n Your input \n sample: {0} \n line: {1} \n was determined to be "\
          "\n latitude: \
        {2} \n longitude: {3}".format(params.sSample,
                                      params.sLine,
                                      myCoords.latitude,
                                      myCoords.longitude)

    print "\n Now searching for these coordinates in all mosaicked cubes with "\
          "target code", params.sTargetCode

    foundFiles = []
    zeros = []
    procPath = DEST_BASE # DEST_BASE set in hirise_tools
    # creating t (=search tuple) to remove potential 'None' type (=not defined)
    l = [params.sTargetCode,params.extraTargetCode]
    l.remove(None)
    t = tuple(l)
    for root,dirs,files in os.walk(procPath):
        # if folder has either target code as obsID or optional one:
        if root.endswith(t):
            for name in files:
                if name.endswith('.mos.cub'):
                    print 'Scanning', name
                    params.sPath = os.path.join(root, name)
                    use_mappt_latlon(params, myCoords)
                    get_sample_line_from_csv(params, myCoords)
                    if not myCoords.pixelValue == "Null" : 
                        foundFiles.append((name,
                                           get_rounded_int_str_from_value(myCoords.sample),
                                           get_rounded_int_str_from_value(myCoords.line)))
                        output = [params.sObsID,
                                  params.sCCDColour,
                                  get_rounded_int_str_from_value(myCoords.sample),
                                  get_rounded_int_str_from_value(myCoords.line),
                                  -10000,
                                  -10000]
                        params.write_row(output)
                        print output
                    else: zeros.append(name)
    print "Found {0} files with non-zero pixel values and {1} out-liers:"\
            .format(len(foundFiles), len(zeros))
    for dataTupel in foundFiles:
        print dataTupel[0], dataTupel[1], dataTupel[2]
    print 'Find results in', params.something
    return foundFiles      
            
            
if __name__ == "__main__":
    from optparse import OptionParser
    
    usage = """Usage: %prog roiName obsID ccdColour sample line
    [optional: -t 2nd_targetcode_nnnn]"""

    descript = """Utility to 1. calculate ground coordinates for a given
    sample/line pair for a given obsID. 2. find all mosaic data cubes on the hirise
    server with the same target code (optional: 2nd additional target code)
    as the given obsID, that also have this point inside (negative results mean
    outside, positive might still lie in black part of map-projected mosaic).
    The roiName that is required will be used for the resulting csv data file.
    The created data file will contain calculated sample/line pairs for the
    found data cube mosaics"""

    parser = OptionParser(usage=usage, description=descript)
    parser.add_option("-t", "--target", dest="extraTargetCode",
                      help="optional 2nd targetcode to search")


    (options,args)=parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        sys.exit(1)
    # create my parameter container
    params = roi.ROI()
    
    params.extraTargetCode = options.extraTargetCode
    print 'extra:', params.extraTargetCode
    
    # check if all required input parameters were given, if not, stop program
    try:
        params.sRoiName, params.sobsID, params.sCCDColour, params.sSample, \
        params.sLine = sys.argv[1:]
    except:
        print('\n Something wrong with parameters.')
        parser.print_help()
        sys.exit(1)

    find_coords(params)
        

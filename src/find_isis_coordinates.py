#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

'''
Created on Jul 14, 2009

@author: aye
'''
import parser

import sys
import os
import glob
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
    sMAPPTcmd.addParameters(['sample=' + params.sSample,
                             'line=' + params.sLine,
                             'type=image'])
    sMAPPTcmd.execute()

def use_mappt_latlon(params, coords):
    sMAPPTcmd = ISIS_mappt()
    sMAPPTcmd.setInputPath(params.sPath)
    sMAPPTcmd.setOutputPath(params.sMAPPTFile)
    sMAPPTcmd.addParameters(['longitude=' + coords.longitude])
    sMAPPTcmd.addParameters(['latitude=' + coords.latitude, 'type=ground'])
    sMAPPTcmd.execute()

def get_values_from_csv(params, coords, value1, value2):
    cmd = ISIS_getkey('PixelValue')
    cmd.setInputPath(params.sMAPPTFile)
    coords.pixelValue = cmd.getKeyValue()
    cmd.setParameters(value1)
    result1 = cmd.getKeyValue()
    cmd.setParameters(value2)
    result2 = cmd.getKeyValue()
    return [result1, result2]


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

    myCoords.longitude, myCoords.latitude = get_values_from_csv(params,
                                                               myCoords,
                                                               'Longitude',
                                                               'Latitude')
    if myCoords.pixelValue == "Null":
        print "Given Coordinates do not seem to have a valid pixel value. Check!"
        sys.exit(1)

    print """
             Your input
             sample: {0}
             line: {1}
             was determined to be
             latitude: {2:5.2f}
             longitude: {3:5.2f}""".format(params.sSample,
                                      params.sLine,
                                      float(myCoords.latitude),
                                      float(myCoords.longitude))

    print "\n Now searching for these coordinates in all mosaicked cubes with "\
          "target code", params.sTargetCode

    foundFiles = []
    zeros = []
    # creating t (=search tuple) to remove potential 'None' type (=not defined)
    l = [params.sTargetCode, params.extraTargetCode]
    # in case extraTargetCode was not defined (=None), remove it
    if None in l: l.remove(None)
    t = tuple(l)
     # get list of all folders that match the targetcode(s)
    tobeScanned = []
    os.chdir(DEST_BASE)
    for elem in t:
        tobeScanned.extend(glob.glob('*_' + elem))
    for folder in tobeScanned:
        fpath = os.path.join(DEST_BASE, folder)
        if not os.path.isdir(fpath):
            continue
        mosaics = glob.glob(os.path.join(fpath, "*.mos.cub"))
        for mosaic in mosaics:
            print 'Scanning', mosaic
            params.sPath = os.path.join(fpath, mosaic)
            use_mappt_latlon(params, myCoords)
            myCoords.sample, myCoords.line = get_values_from_csv(params,
                                                                 myCoords,
                                                                 'Sample',
                                                                 'Line')
            if not myCoords.pixelValue == "Null" :
                if any([myCoords.sample < 0, myCoords.line < 0]):
                    zeros.append(mosaic)
                params.map_sample_offset = \
                    get_rounded_int_str_from_value(myCoords.sample)
                params.map_line_offset = \
                    get_rounded_int_str_from_value(myCoords.line)
                params.write_row(output)
                print output
            else: zeros.append(mosaic)
    print "Found {0} files with non-zero pixel values and {1} out-liers:"\
            .format(len(foundFiles), len(zeros))
    for dataTupel in foundFiles:
        print dataTupel[0], dataTupel[1], dataTupel[2]
    print 'Find results in', params.sOutputFileName
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
    parser.add_option("-n", "--testing", action='store_true',
                      dest="testing", default=False,
                      help="test functionality without providing parameters")


    (options, args) = parser.parse_args()

     # create my parameter container
    params = roi.ROI()

    params.extraTargetCode = options.extraTargetCode

    if options.testing:
        params.sRoiName = 'IncaCity'
        params.sobsID = 'PSP_003092_0985'
        params.sCCDColour = 'RED'
        params.sSample = '5000'
        params.sLine = '18000'
        params.extraTargetCode = '0815'
    elif len(args) == 0:
        parser.print_help()
        sys.exit(1)
    else:
        try:
            params.sRoiName, params.sobsID, params.sCCDColour, params.sSample, \
            params.sLine = sys.argv[1:]
        except:
            print('\n Something wrong with parameters.')
            parser.print_help()
            sys.exit(1)

    find_coords(params)


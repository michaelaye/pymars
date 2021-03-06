#!/Library/Frameworks/Python.framework/Versions/Current/bin/python2.6
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
from hirise_tools import mosaic_extensions as extensions


def get_rounded_int_str_from_value(sValue):
    return str(int(round(float(sValue))))

def get_rounded_str_from_value(sValue, iDigits):
    return str(round(float(sValue), iDigits))

def get_ground_from_image(params):
    """function to determine ground coords from sample/line.
    Results will be given in csv output file from ISIS mappt program."""
    mapptCmd = ISIS_mappt()
    sourcePath = getStoredPathFromID(params.obsID) # DEST_BASE set in hirise_tools
    print sourcePath
    cubePath = glob.glob(sourcePath + '*'+extensions)[0]
    mapptCmd.setInputPath(cubePath)
    print "output-file for scan in prime image:", params.mapptFile
    mapptCmd.setOutputPath(params.mapptFile)
    mapptCmd.addParameters(['sample=' + params.inputSample,
                             'line=' + params.inputLine,
                             'type=image'])
    mapptCmd.execute()

def get_image_from_ground(params, coords):
    mapptCmd = ISIS_mappt()
    mapptCmd.setInputPath(params.mosaicPath)
    mapptCmd.setOutputPath(params.mapptFile)
    mapptCmd.addParameters(['longitude=' + coords.longitude])
    mapptCmd.addParameters(['latitude=' + coords.latitude, 'type=ground'])
    mapptCmd.execute()

def get_values_from_csv(params, coords, key1, key2):
    cmd = ISIS_getkey('PixelValue')
    cmd.setInputPath(params.mapptFile)
    coords.pixelValue = cmd.getKeyValue()
    result1 = cmd.getKeyValue(key1)
    result2 = cmd.getKeyValue(key2)
    return [result1, result2]


def find_coords(params):
    if params.extraTargetCode == '':
        print """found no extra target code, will only search for target code 
                of obsID \n"""
        params.extraTargetCode = 'ouk;ohuoenuiuc' #dummy extra target code

    print "searching..."
    # get subData in obsID in case i need it later
    params.sciencePhase, params.orbit, params.targetCode = \
        params.obsID.split('_')


    # use mappt on given file to create output file from where to read the 
    # lon/lat to search for
    params.mapptFile = params.obsID + '_mappt.pvl'
    get_ground_from_image(params)
    print "done mapping"

    myCoords = Coordinates()
    myCoords.sample = params.inputSample
    myCoords.line = params.inputLine

    myCoords.longitude, myCoords.latitude = \
        get_values_from_csv(params,
                            myCoords,
                            'PositiveEast360Longitude',
                            'PlanetocentricLatitude')
    if myCoords.pixelValue == "NULL":
        print "Given Coordinates do not seem to have a valid pixel value. Check!"
        sys.exit(1)

    print """
             Your input
             sample: {0}
             line: {1}
             was determined to be
             latitude: {2:5.2f}
             longitude: {3:5.2f}""".format(params.inputSample,
                                      params.inputLine,
                                      float(myCoords.latitude),
                                      float(myCoords.longitude))

    foundFiles = []
    zeros = []
    # creating t (=search tuple) to remove potential 'None' type (=not defined)
    for folder in os.listdir(DEST_BASE):
        fpath = os.path.join(DEST_BASE, folder)
        # in case it's not a folder, continue:
        if not os.path.isdir(fpath):
            continue
        searchpath = os.path.join(fpath,'*'+ extensions)
        mosaics = glob.glob(searchpath)
        for mosaic in mosaics:
            print 'Scanning', mosaic
            fpath = os.path.join(fpath, mosaic)
            params.mosaicPath = fpath
            params.obsID = getObsIDFromPath(fpath)
            params.ccdColour = getCCDColourFromMosPath(fpath)
            get_image_from_ground(params, myCoords)
            myCoords.sample, myCoords.line = \
                get_values_from_csv(params,
                                    myCoords,
                                    'Sample',
                                    'Line')
            if not myCoords.pixelValue == "NULL" :
                if any([myCoords.sample < 0, myCoords.line < 0]):
                    zeros.append(mosaic)
                params.mapSampleOffset = \
                    get_rounded_int_str_from_value(myCoords.sample)
                params.mapLineOffset = \
                    get_rounded_int_str_from_value(myCoords.line)
                params.store_row()
            else:
		zeros.append(mosaic)
    print "Found {0} files with non-zero pixel values and {1} out-liers:"\
            .format(len(params.dict), len(zeros))
    params.write_out()
    print 'Find results in', params.outputFileName


if __name__ == "__main__":
    from optparse import OptionParser

    usage = """Usage: %prog roiName obsID ccdColour sample line
                [target codes]"""

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
    params = roi.ROI_Data()

    params.extraTargetCode = options.extraTargetCode
    if options.testing:
        params.roiName = 'IncaCity'
        params.obsID = 'PSP_003092_0985'
        params.ccdColour = 'RED'
        params.inputSample = '6849'
        params.inputLine = '18426'
        params.extraTargetCode = '0815'
    elif len(args) == 0:
        parser.print_help()
        sys.exit(1)
    else:
        try:
            params.roiName, params.obsID, params.ccdColour, params.inputSample, \
            params.inputLine = args
        except:
            try:
                params.roiName, params.obsID, params.inputSample, \
                params.inputLine = args
                params.ccdColour = ''
            except:
                print('\n Something wrong with parameters.')
                parser.print_help()
                sys.exit(1)

    find_coords(params)


#!/usr/bin/python2.6

'''
Created on Jul 14, 2009

@author: aye
'''

import sys, os, csv, glob, string
from hirise_tools import *
from ISIS_Commands import *

# global for this module: which file extensions i should look for:
sExtensions = '.cal.norm.map.equ.mos.cub'

   # define an empty class, just to hold a set of parameters
class Params:
    pass
 
def getRoundedIntStrFromValue(sValue):
    return str(int(round(float(sValue))))

def getRoundedStrFromValue(sValue, iDigits):
    return str(round(float(sValue), iDigits))

def executeMAPPT(params):
    sMAPPTcmd = ISIS_mappt()
    sSourcePath = DEST_BASE + '/' + params.sobsID + '/' # DEST_BASE set in hirise_tools
    sCubePath = sSourcePath + params.sobsID + '_' + params.sCCDColour + sExtensions
    sMAPPTcmd.setInputPath(sCubePath)
    print "output-file for scan in prime image:", params.sOutputFileName
    sMAPPTcmd.setOutputPath(params.sOutputFileName)
    sMAPPTcmd.addParameters(['sample=' + params.sSample, 'line=' + params.sLine, 'type=image'])
    # call mappt. it will create the output csv file that then will be read
    print sMAPPTcmd
    sMAPPTcmd.execute()

def useMAPPT_latlon(params, coords):
    sMAPPT_cmd = ISIS_mappt()
    sMAPPT_cmd.setInputPath(params.sPath)
    sMAPPT_cmd.setOutputPath(params.sOutputFileName)
    sMAPPT_cmd.addParameters(['longitude=' + coords.longitude])
    sMAPPT_cmd.addParameters(['latitude=' + coords.latitude, 'type=ground'])
    # call mappt. it will create the output csv file that then will be read
    print sMAPPT_cmd
    sMAPPT_cmd.execute()
  
def getLatLonFromCSV(params, coords):
    cmdGetKey = ISIS_getkey('PixelValue')
    cmdGetKey.setInputPath(params.sOutputFileName)
    pixelValue = cmdGetKey.getKeyValue()
    if pixelValue == "Null":
        print "Starting Coordinate seems to have no valid pixel-value, please check"
        sys.exit(1)
    cmdGetKey.setParameters('Longitude')
    coords.longitude = cmdGetKey.getKeyValue()
    cmdGetKey.setParameters('Latitude')
    coords.latitude = cmdGetKey.getKeyValue()
    print coords.latitude
    print coords.longitude
    return

def getSampleLineFromCSV(params, coords):
    cmd = ISIS_getkey('PixelValue')
    cmd.setInputPath(params.sOutputFileName)
    coords.pixelValue = cmd.getKeyValue()
    cmd.setParameters('Sample')
    coords.sample = cmd.getKeyValue()
    cmd.setParameters('Line')
    coords.line = cmd.getKeyValue()
    return

def main(params):
    if params.extraTargetCode == '':
        print """found no extra target code, will only search for target code 
                of obsID \n"""
        params.extraTargetCode = 'ouk;ohuoenuiuc' #dummy extra target code
    
    print "{0} working.".format(params.sProgName)
    # get subData in obsID in case i need it later
    params.sSciencePhase, params.sOrbit, params.sTargetCode = \
        params.sobsID.split('_')
    
    params.sOutputFileName = "_".join([params.sobsID, 'mappt_output.csv'])
    
    # use mappt on given file to create output file from where to read the 
    # lon/lat to search for
    executeMAPPT(params)
    print "done mapping"
    
    myCoords = Coordinates()
    myCoords.sample = params.sSample
    myCoords.line = params.sLine
    
    getLatLonFromCSV(params, myCoords)
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
    resultFileName = "_".join(["Coordinates",
                               params.sTargetSciencePhase,
                               "lat",
                               getRoundedStrFromValue(myCoords.latitude, 3),
                               "lon",
                               getRoundedStrFromValue(myCoords.longitude,
                                                       3)]) + '.txt' 
    outFile = open(resultFileName, 'w')
    for folder in os.listdir(procPath):
        if folder.endswith((params.sTargetCode,
                            params.extraTargetCode)) and \
           folder.startswith(params.sTargetSciencePhase):
            for name in os.listdir(os.path.join(procPath, folder)):
                if name.endswith('.mos.cub'):
                    print 'Scanning', name
                    params.sPath = os.path.join(procPath, folder, name)
                    useMAPPT_latlon(params, myCoords)
                    getSampleLineFromCSV(params, myCoords)
                    if not myCoords.pixelValue == "Null" : 
                        foundFiles.append((name,
                                           getRoundedIntStrFromValue(myCoords.sample),
                                           getRoundedIntStrFromValue(myCoords.line)))
                        outputString = string.join([params.sPath,
                                                   getRoundedIntStrFromValue(myCoords.sample),
                                                   getRoundedIntStrFromValue(myCoords.line), '\n'])
                        outFile.write(outputString)
                        print outputString
                    else: zeros.append(name)
    print "Found {0} files with non-zero pixel values and {1} out-liers:"\
            .format(len(foundFiles), len(zeros))
    for dataTupel in foundFiles:
        print dataTupel[0], dataTupel[1], dataTupel[2]
    print 'Find results in', resultFileName
    return foundFiles      
            
            
if __name__ == "__main__":
    # create my parameter container
    params = Params()
    
    params.extraTargetCode = ''
    # check if all required input parameters were given, if not, stop program
    try:
        params.sProgName, params.sobsID, params.sCCDColour, params.sSample, \
        params.sLine, params.sTargetSciencePhase, params.extraTargetCode = sys.argv
    except:
        try:
            params.sProgName, params.sobsID, params.sCCDColour, params.sSample, \
            params.sLine, params.sTargetSciencePhase = sys.argv
        except:
            print "Usage: {0} obsID ccdColour sample line targetSciencePhase(PSP/ESP) \
    [optional: 2nd targetcode nnnn]".format(sys.argv[0])
            sys.exit()

    main(params)
        

#!/usr/bin/python2.6

'''
Created on Jul 14, 2009

@author: aye
'''

import sys, os, csv, glob, string, isis_settings
from hirise_tools import *
from ISIS_Commands import ISIS_mappt

# global for this module: which file extensions i should look for:
sExtensions='.cal.norm.map.equ.mos.cub'

   # define an empty class, just to hold a set of parameters
class Params:
    pass
 
def getRoundedIntStrFromValue(sValue):
    return str(int(round(float(sValue))))

def getRoundedStrFromValue(sValue, iDigits):
    return str(round(float(sValue), iDigits))

def getCSVFromMAPPT(params):
    sMAPPTcmd = ISIS_mappt()
    sSourcePath = isis_settings.DEST_BASE + '/'  + params.sobsID + '/'
    sCubePath = sSourcePath + params.sobsID + '_' + params.sCCDColour + sExtensions
    sMAPPTcmd.setInputPath(sCubePath)
    print "output-file for scan in prime image:",params.sOutputFileName
    sMAPPTcmd.setOutputPath(params.sOutputFileName)
    sMAPPTcmd.addParameters(['sample='+params.sSample,'line='+params.sLine,'type=image'])
    # call mappt. it will create the output csv file that then will be read
    sMAPPTcmd.execute()

def useMAPPT_latlon(params,coords):
    sMAPPT_cmd = ISIS_mappt()
    sMAPPT_cmd.setInputPath(params.sPath)
    sMAPPT_cmd.setOutputPath(params.sOutputFileName)
    sMAPPT_cmd.addParameters(['longitude=' + coords.longitude])
    sMAPPT_cmd.addParameters(['latitude=' + coords.latitude,'type=ground'])
    # call mappt. it will create the output csv file that then will be read
    sMAPPT_cmd.execute()
  
def getDicFromCSV(params):
    csvfile = open(params.sOutputFileName)
    dialect = csv.Sniffer().sniff(csvfile.read(2048))
    csvfile.seek(0)
    return csv.DictReader(csvfile, dialect=dialect)
        
def getLatLonFromCSV(params, coords):
    reader = getDicFromCSV(params)
    myDic = reader.next()
    pixelValue = myDic['PixelValue']
    if pixelValue == "Null":
        print "Starting Coordinate seems to have no valid pixel-value, please check"
        sys.exit()
    coords.longitude = myDic['Longitude']
    coords.latitude  = myDic['Latitude']
    csvfile.close()
    return

def getSampleLineFromCSV(params, coords):
    reader = getDicFromCSV(params)
    myDic = reader.next()
    coords.pixelValue = myDic['PixelValue']
    coords.sample = myDic['Sample']
    coords.line  = myDic['Line']
    csvfile.close()
    return

def main(params):
    if params.extraTargetCode == '':
        print 'found no extra target code, will only search for target code of obsID \n'
        params.extraTargetCode = 'ouk;ohuoenuiuc' #dummy extra target code
    
    print "{0} working.".format(params.sProgName)
    # get subData in obsID in case i need it later
    params.sSciencePhase, params.sOrbit, params.sTargetCode = params.sobsID.split('_')
    
    params.sOutputFileName = "_".join([params.sobsID,'mappt_output.csv'])
    
    # use mappt on given file to create output file from where to read the lon/lat to search for
    getCSVFromMAPPT(params)
    
    myCoords = Coordinates()
    myCoords.sample = params.sSample
    myCoords.line   = params.sLine
    
    getLatLonFromCSV(params,myCoords)
    print "\n Your input \n sample: {0} \n line: {1} \n was determined to be \n latitude: \
        {2} \n longitude: {3}".format(params.sSample, \
                                      params.sLine, \
                                      myCoords.latitude, \
                                      myCoords.longitude)

    print "\n Now searching for these coordinates in all mosaicked cubes with target code", \
        params.sTargetCode

    foundFiles = []
    zeros = []
    procPath = isis_settings.DEST_BASE
    resultFileName = "_".join(["Coordinates", \
                               params.sTargetSciencePhase, \
                               "lat", \
                               getRoundedStrFromValue(myCoords.latitude,3), \
                               "lon", \
                               getRoundedStrFromValue(myCoords.longitude,3)]) + '.txt' 
    outFile = open(resultFileName,'w')
    for folder in os.listdir(procPath):
        if folder.endswith((params.sTargetCode, params.extraTargetCode)) and folder.startswith(params.sTargetSciencePhase):
            for name in os.listdir(os.path.join(procPath,folder)):
                if name.endswith('.mos.cub'):
                    print 'Scanning',name
                    params.sPath = os.path.join(procPath,folder,name)
                    useMAPPT_latlon(params, myCoords)
                    getSampleLineFromCSV(params, myCoords)
                    if not myCoords.pixelValue == "Null" : 
                        foundFiles.append((name, \
                                           getRoundedIntStrFromValue(myCoords.sample), \
                                           getRoundedIntStrFromValue(myCoords.line)))
                        outputString = string.join([params.sPath, \
                                                   getRoundedIntStrFromValue(myCoords.sample), \
                                                   getRoundedIntStrFromValue(myCoords.line),'\n'])
                        outFile.write(outputString)
                        print outputString
                    else: zeros.append(name)
    print "Found {0} files with non-zero pixel values and {1} out-liers:".format(len(foundFiles),len(zeros))
    for dataTupel in foundFiles:
        print dataTupel[0],dataTupel[1],dataTupel[2]
    print 'Find results in',resultFileName
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
        
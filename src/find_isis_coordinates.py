#!/usr/bin/python

'''
Created on Jul 14, 2009

@author: aye
'''

import sys, os, csv, glob, string, isis_settings
from hirise_tools import *

   # define an empty class, just to hold a set of parameters
class Params:
    pass
 
def getRoundedIntStrFromValue(sValue):
    return str(int(round(float(sValue))))

def getRoundedStrFromValue(sValue, iDigits):
    return str(round(float(sValue), iDigits))

def executeMAPPT(params):
    sSourcePath = isis_settings.DEST_BASE + '/'  + params.sImageID + '/'
    sExtensions='.cal.norm.map.equ.mos.cub'
    sCubePath = sSourcePath + params.sImageID + '_' + params.sCCDColour + sExtensions
    # prepare command string for mappt
    sMAPPT_cmd = ['mappt']
    sMAPPT_cmd.append('from=' + sCubePath)
    print "output at first scan:",params.sOutputFileName
    sMAPPT_cmd.append('to=' + params.sOutputFileName)
    sMAPPT_cmd.append('sample=' + params.sSample)
    sMAPPT_cmd.append('line=' + params.sLine)
    sMAPPT_cmd.append('type=image')
    sMAPPT_cmd.append('format=flat')
    sMAPPT_cmd.append('append=false')
    # call mappt. it will create the output csv file that then will be read
    try:
        subprocess.call(sMAPPT_cmd)
    except OSError:
        print "Had trouble calling mappt program, did you forget to 'start_isis' ?"
        print "Exiting"
        sys.exit()
        
    return

def useMAPPT_latlon(params,coords):
    sMAPPT_cmd = ['mappt']
    sMAPPT_cmd.append('from=' + params.sPath)
    sMAPPT_cmd.append('to=' + params.sOutputFileName)
    sMAPPT_cmd.append('longitude=' + coords.longitude)
    sMAPPT_cmd.append('latitude=' + coords.latitude)
    sMAPPT_cmd.append('type=ground')
    sMAPPT_cmd.append('format=flat')
    sMAPPT_cmd.append('append=false')
    # call mappt. it will create the output csv file that then will be read
    subprocess.call(sMAPPT_cmd)
    return
    
def getLatLonFromCSV(params, coords):
    csvfile = open(params.sOutputFileName)
    dialect = csv.Sniffer().sniff(csvfile.read(2048))
    csvfile.seek(0)
    reader = csv.DictReader(csvfile, dialect=dialect)
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
    csvfile = open(params.sOutputFileName)
    dialect = csv.Sniffer().sniff(csvfile.read(2048))
    csvfile.seek(0)
    reader = csv.DictReader(csvfile, dialect=dialect)
    myDic = reader.next()
    coords.pixelValue = myDic['PixelValue']
    coords.sample = myDic['Sample']
    coords.line  = myDic['Line']
    csvfile.close()
    return

def main():
    
    # create my parameter container
    params = Params()
    
    params.extraTargetCode = ''
    # check if all required input parameters were given, if not, stop program
    try:
        params.sProgName, params.sImageID, params.sCCDColour, params.sSample, \
        params.sLine, params.sTargetSciencePhase, params.extraTargetCode = sys.argv
    except:
        try:
            params.sProgName, params.sImageID, params.sCCDColour, params.sSample, \
            params.sLine, params.sTargetSciencePhase = sys.argv
        except:
            print "Usage: {0} imageID ccdColour sample line targetSciencePhase(PSP/ESP) \
    [optional: 2nd targetcode nnnn]".format(sys.argv[0])
            sys.exit()

    if params.extraTargetCode == '':
        print 'found no extra target code, will only search for target code of obsID \n'
        params.extraTargetCode = 'ouk;ohuoenuiuc'
    
    print "{0} working.".format(params.sProgName)
    # get subData in imageID in case i need it later
    params.sSciencePhase, params.sOrbit, params.sTargetCode = params.sImageID.split('_')
    
    params.sOutputFileName = "_".join([params.sImageID,'mappt_output.csv'])
    # use mappt on given file to create output file from where to read the lon/lat to search for
    executeMAPPT(params)
    
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
                        outFile.write(string.join([params.sPath, \
                                                   getRoundedIntStrFromValue(myCoords.sample), \
                                                   getRoundedIntStrFromValue(myCoords.line),'\n']))
                    else: zeros.append(name)
    print "Found {0} files with non-zero pixel values and {1} out-liers:".format(len(foundFiles),len(zeros))
    for dataTupel in foundFiles:
        print dataTupel[0],dataTupel[1],dataTupel[2]
    print 'Find results in',resultFileName
            
            
            
if __name__ == "__main__":

    main()
        
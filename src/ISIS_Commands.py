'''
Created on Jul 21, 2009

@author: aye
'''
import os, sys
from hirise_tools import *

class ISIS_cmd:
    bInputToDelete = False
    def __init__(self):
        self.lInput = ['from=']
        self.lOutput = ['to=']
        self.lParameters = []
        
    def setInputPath(self,psInputPath):
#        self.lInput.append(psInputPath)
        self.lInput[0] += psInputPath

    def setOutputPath(self, psOutputPath):
        self.lOutput[0] += psOutputPath

    def addParameters(self, plParameters):
        "parameter is of type <list>"
        self.lParameters.extend(plParameters)
        
    def getExeList(self):
        argList = [self.sName]
        for parList in [self.lInput, self.lOutput, self.lParameters]:
            for item in parList:
                argList.append(item)
        return argList

    def execute(self):
        try:
            subprocess.call(self.getExeList())
        except OSError:
            print "Had trouble calling {0}, did you forget to start_isis?".format(self.sName)
            print "exiting..."
            sys.exit(-1)
            
    def __str__(self):
        return ' '.join([self.sName] + self.lInput + self.lOutput + self.lParameters) + '\n'
    
        
class ISIS_hi2isis(ISIS_cmd):
    sName = 'hi2isis'
 
        
class ISIS_spiceinit(ISIS_cmd):
    sName = 'spiceinit'
    def getExeList(self):
        return [self.sName, ' '.join(self.lInput + self.lParameters)]
    def __str__(self):
        return ' '.join([self.sName] + self.lInput + self.lParameters) + '\n'
 
    
class ISIS_hical(ISIS_cmd):
    sName = 'hical'
    def __init__(self):
        ISIS_cmd.__init__(self)
        self.bInputToDelete = True
 
    
class ISIS_hicalbeta(ISIS_cmd):
    sName = 'hicalbeta'
    def __init__(self):
        ISIS_cmd.__init__(self)
        self.bInputToDelete = True


class ISIS_histitch(ISIS_cmd):
    sName = 'histitch'
    def __init__(self):
        ISIS_cmd.__init__(self)
        self.lInput = ['from1=', 'from2=']
        self.lParameters.append('balance=true')
        self.bInputToDelete = True
    def setInputPath(self, psInputPath1):
        self.lInput[0] += psInputPath1
    def setInputPath2(self, psInputPath2):
        self.lInput[1] += psInputPath2


class ISIS_cubenorm(ISIS_cmd):
    sName = 'cubenorm'
    def __init__(self):
        ISIS_cmd.__init__(self)
        self.bInputToDelete = True
    

class ISIS_cam2map(ISIS_cmd):
    sName = 'cam2map'
    def __init__(self):
        ISIS_cmd.__init__(self)
        self.mapfilePath='/processed_data/polar_map_projection.map'
        self.useDefaultMap = True
        self.lParameters.append('pixres=MAP')
        self.bInputToDelete = True
    def setMap(self,pMapFilePath):
        self.mapfilePath = pMapFilePath
        self.useDefaultMap = False
    def getExeList(self):
        self.lParameters.append('map='+self.mapfilePath)
        return ISIS_cmd.getExeList(self)
    

class ISIS_equalizer(ISIS_cmd):
    sName = 'equalizer'
    def __init__(self):
        ISIS_cmd.__init__(self)
        self.lInput = ['fromlist=']
        self.lOutput = ['outstats=']
    def setHoldList(self, psPathToHoldList= None):
        if psPathToHoldList:
            self.lParameters.append('holdlist='+psPathToHoldList)
        else:
            inputListNamePath = self.lInput[0].split('=')[1]
            dirname, basename = os.path.split(inputListNamePath)
            phase, orbit, targetCode, detec = basename.split("_")[:4]
            fIn = open(inputListNamePath)
            # get first file of inputfile list
            holdFile = fIn.readline()
            # write it as holdlist-file
            outFileNamePath = os.path.join(dirname, "_".join([phase,orbit,targetCode,detec,"toHold.lis"])) 
            fOut = open(outFileNamePath,'w')
            fOut.write(holdFile)
            fIn.close()
            fOut.close()
            self.lParameters.append('holdlist=' + outFileNamePath)


    
class ISIS_automos(ISIS_cmd):
    sName = 'automos'
    def __init__(self):
        ISIS_cmd.__init__(self)
        self.lInput = ['fromlist=']
        self.lOutput = ['mosaic=']
        self.lParameters.append('priority=beneath')
        

class ISIS_getkey(ISIS_cmd):
    sName = 'getkey'
    lParameters = ['recursive=true']
    def __init__(self, psKeyword):
        ISIS_cmd.__init__(self)
        self.lOutput = []
        self.setParameters(psKeyword)
    def getKeyValue(self):
        try:
            return executeIsisCmdWithReturn(self.__str__()).splitlines()[0]
        except IndexError:
            print "was calling: \n",self.__str__()
            print "Problem with getting key value (getkey). \n" \
                   "Probably error in executing one of ISIS commands before"
            sys.exit()
    def setParameters(self, psKeyword):
        self.lParameters = []
        self.lParameters.append('keyword='+psKeyword)
        self.lParameters.append('recursive=true')
        
    
class ISIS_phocube(ISIS_cmd):
    '''
    Input: List of Bands from the possible bands to calculate as given here
    so initialize for example like this:
    phocmd = ISIS_phocube(['phase','emission'])
    ''' 
    sName = 'phocube'
    lParameterKeys = []
    lParameterKeys.append('PHASE')  #    Create a phase angle band.
    lParameterKeys.append('EMISSION') #    Create an emission angle band.
    lParameterKeys.append('INCIDENCE') #    Create an incidence angle band.
    lParameterKeys.append('LATITUDE') #    Create a latitude band.
    lParameterKeys.append('LONGITUDE') #    Create a longitude band.
    lParameterKeys.append('PIXELRESOLUTION') #    Create a pixel resolution band.
    lParameterKeys.append('LINERESOLUTION') #    Create a line resolution band.
    lParameterKeys.append('SAMPLERESOLUTION') #    Create a sample resolution band.
    lParameterKeys.append('DETECTORRESOLUTION') #    Create a detector resolution band.
    lParameterKeys.append('NORTHAZIMUTH') #    Create a north azimuth band.
    lParameterKeys.append('SUNAZIMUTH') #    Create a sun azimuth band.
    lParameterKeys.append('SPACECRAFTAZIMUTH') #    Create a spacecraft azimuth band.
    lParameterKeys.append('OFFNADIRANGLE') #    Create a offNadir angle band.
    def __init__(self, plBands):
        ISIS_cmd.__init__(self)
        plBandsUpper = [band.upper() for band in plBands]
        self.lParameters = [key + '=false' for key in self.lParameterKeys if key not in plBandsUpper ]
        for band in plBandsUpper:
            if band in self.lParameterKeys:
                self.lParameters.append(band + '=true')
            else:
                print "This band is not defined as an allowed parameter for phocube: ", band
                sys.exit()
        
        
class ISIS_stats(ISIS_cmd):
    sName = 'stats'
        
        
class ISIS_crop(ISIS_cmd):
    sName = 'crop'
    def __init__(self):
        ISIS_cmd.__init__(self)
        self.lParameters = ['nsamp=5','nline=5']
        
        
class ISIS_cosi(ISIS_cmd):
    sName = 'cosi'
    def __init__(self):
        ISIS_cmd.__init__(self)
        self.bInputToDelete = True
        
class ISIS_mappt(ISIS_cmd):
    sName = 'mappt'
    def __init__(self):
        ISIS_cmd.__init__(self)
        self.addParameters(['append=false'])
        

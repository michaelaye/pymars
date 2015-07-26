'''
Created on Jul 17, 2009

@author: aye
'''
from hirise_tools import *
from multiprocessing import Process
import subprocess
import glob
import os
import sys
from ISIS_Commands import *
from os.path import join as pjoin


class HiRiseCCD(object):
    ''' 
    each CCD colour has an amount of CCDs, and an identifier that consists
    of the colour string and a running number
    '''
    
    dCCDConfig = {'RED': (10, 0), 'IR': (2, 10), 'BG' : (2, 12)}

    sColour = ''
    iCCD = 0
    iNoOfCCDs = 0
    lListofCCDs = []
    lListofChannels = []
    
    def __init__(self, psColour):
        self.sColour = psColour
        amount, start = self.dCCDConfig[psColour]
        self.lListofCCDs = [self.sColour+str(i) for i in range(start, start+amount)]
        for ccd in self.lListofCCDs:
            for i in range(2):
                self.lListofChannels.append(ccd + '_' + str(i))
        
    def generateCCDID(self):
        for id in self.lListofCCDs:
            yield id
            
    def generateChannelID(self):
        for channelID in self.lListofChannels:
            yield channelID
    

class ISIS_Executer(object):
    '''
    This class serves as executing interface to the ISIS programs.
    It creates the calling command and then calls the ISIS programs
    externally, either by using multiprocess library or single process
    calls, depending on which ISIS program is used (cubenorm does not
    benefit from being called simultanuously).
    '''
    
    sConverter = 'hi2isis'
    sCalib     = 'hical'
    sSpice     = 'spiceinit'
    sStitcher  = 'histitch'
    sNormer    = 'cubenorm'
    sMapper    = 'cam2map'
    sEqualizer = 'equalizer'
    sMosaicer  = 'automos'
    sPhocube   = 'phocube'
    sCropper   = 'crop'
    sCosi      = 'cosi'
    
    lListToExecute = [sConverter,
                      sSpice,
                      # sPhocube,
                      sCalib,
                      sStitcher,
#                      sCosi,
                      sNormer,
                      sMapper,
                      sEqualizer,
                      sMosaicer,
                      ]

    # lExecuteSingle = [sNormer,sSpice]
    lExecuteSingle = []
    
    lWorkOnChannels = [sConverter, sSpice, sCalib, sPhocube, sStitcher]
    lCommandsWithList = [sEqualizer,sMosaicer]
    dIsisProgs = dict([(prog, eval("ISIS_"+prog) ) for prog in lListToExecute])
#    dIsisProgs[sPhocube] = eval("ISIS_phocube('incidence')")
    
    sRawExt = '.IMG'
    sCubExt = '.cub'
    sCalExt = '.cal'
    sNormExt= '.norm'
    sMapExt = '.map'
    sMosExt = '.mos'
    sEquStats='.equstats.pvl'
    sEquExt = '.equ'
    sPhoExt = '.pho'
    sCropExt= '.crop'
    sCosiExt= '.cosi'
    sSPIExt=  '.spi'
    
    dInputExtensions =  {sConverter:    sRawExt, 
                         sSpice:        sCubExt, 
                         sCropper:      sCubExt, 
                         sPhocube:      sCubExt, 
                         sCalib:        sCubExt,
                         sCosi:         sCalExt + sCubExt, 
                         sStitcher:     sCalExt + sCubExt, 
                         sNormer:       sCalExt + sCubExt, 
                         sMapper:       sCalExt + sNormExt + sCubExt, 
                         sEqualizer:    sCalExt + sNormExt + sMapExt + sCubExt, 
                         sMosaicer:     sCalExt + sNormExt + sMapExt + sEquExt + sCubExt
                         }

    dOutputExtensions = {sConverter:    sCubExt,
                         sSpice:        sCubExt,
                         sPhocube:      sPhoExt + sCubExt,
                         sCropper:      sCropExt + sCubExt,
                         sCalib:        sCalExt + sCubExt,
                         sCosi:         sCalExt + sCosiExt + sCubExt,
                         sStitcher:     sCalExt + sCubExt,
                         sNormer:       sCalExt + sNormExt + sCubExt,
                         sMapper:       sCalExt + sNormExt + sMapExt + sCubExt,
                         # equalizer's TO target is only the stats file, the equalization is applied directly to all input files
                         sEqualizer:    sCalExt + sNormExt + sMapExt + sEquStats,
                         sMosaicer:     sCalExt + sNormExt + sMapExt + sEquExt + sMosExt + sCubExt}
    
    def __init__(self, psObsID, psColour, plProgList = None, pbFake = False, pbDebug = False, pMapfile = None):
        '''
        The constructor of the executer class requires the ObsID and the to be
        processed CCD colour (determines loop ranges and file names to be used).
        Also a debug and a faking flag can be set to 
        1. let the object print more infos during operation
        2. let the object only fake the execution by printing the commands
        instead of executing them
        '''
        try:
            phase, orbit, targetCode = psObsID.split("_")
        except ValueError:
            print "ObsID should be in the form of 'PHA_012345_0123'"
            sys.exit()
        self.sObsID = psObsID
        self.sColour = psColour.upper()
        self.ccd = HiRiseCCD(self.sColour)
        if plProgList: 
            self.lListToExecute = plProgList
        
        self.bDebug  = pbDebug
        self.bFake   = pbFake
        self.mapfile = pMapfile
        # only hi2isis works from raw sources, all others from the place where intermediate data was saved
        # exception for hi2isis is coded in self.process function
        self.sSourcePath = self.sDestPath = getDestPathFromID(self.sObsID)
        
    def generateInputBasename(self, psProgName, psDetector):
        basename = self.sObsID + '_' + psDetector
        try:
            basename += self.dInputExtensions[psProgName]
        except KeyError as (strerror):
            print "{0} does not exist as registered program".format(strerror)
            sys.exit()
        return basename
    
    def generateOutputBasename(self, psProgName, psDetector):
        basename = self.sObsID + '_' + psDetector
        basename += self.dOutputExtensions[psProgName]
        return basename
        
    def generateInputList(self, prog):
        os.chdir(self.sSourcePath)
        extensions = self.dInputExtensions[prog]
        fileNames = glob.glob(self.sSourcePath + '*' + self.ccd.sColour + '*' + extensions)
        fileNames.sort()
        inputListFileName = self.sObsID + '_' + self.ccd.sColour + '_to' + prog.capitalize() + '.lis'
        if not self.bFake: 
            outfile = open(inputListFileName,'w')
            for fileName in fileNames:
                outfile.write(fileName + '\n')
            outfile.close()
        if self.bDebug: 
            print "Created ",inputListFileName
        return inputListFileName
    
    def generateSpiceInfo(self):
        cmdKey = ISIS_getkey('SolarLongitude')
        myIter = self.ccd.generateChannelID()
        inputPath = ''
        while not os.path.exists(inputPath):
            detec = myIter.next()
            inputFileBaseName = self.generateInputBasename(self.sPhocube, detec)
            inputPath = pjoin(self.sSourcePath, inputFileBaseName)
        cmdKey.setInputPath(inputPath)
        L_s = cmdKey.getKeyValue()
        glob_pattern = '*'+self.sColour+'*'+self.dOutputExtensions[self.sPhocube]
        sStatsInputFile = glob.glob(pjoin(self.sDestPath, glob_pattern))
        if not os.path.exists(sStatsInputFile[0]):
            print 'stats input file does not exist: ',statsInputFile[0]
            sys.exit()
        statsCmd = ISIS_stats()
        statsCmd.setInputPath(sStatsInputFile[0])
        outfname = "_".join([self.sObsID, self.sColour, 'phocube.stats.pvl'])
        outfileStats = pjoin(self.sDestPath, outfname)
        statsCmd.setOutputPath(outfileStats)
        if self.bDebug: 
            print statsCmd
        output = executeIsisCmd(statsCmd.getExeList())
        outfname = "_".join([self.sObsID, self.sColour, 'spiceinfo.txt'])
        outfileSpiceInfo = pjoin(self.sDestPath, outfname)
        cmdKey = ISIS_getkey('Average')
        cmdKey.setInputPath(outfileStats)
        avgIncAngle = cmdKey.getKeyValue()
        if self.bDebug: 
            print "L_s: ", L_s
            print "Average Incidence Angle: ", avgIncAngle
        f = open(outfileSpiceInfo,'w')
        f.write(L_s + ' ' + avgIncAngle + '\n')
        f.close()
        
    def processPhoCube(self, myIter):
        cmdGetKey = ISIS_getkey('Samples')
        inputPath = ''
        while not os.path.exists(inputPath):
            try:
                detec = myIter.next()
            except StopIteration:
                print "could not get next detector string. exiting"
                sys.exit()
            inputFileBaseName = self.generateInputBasename(self.sPhocube, detec)
            inputPath = self.sSourcePath + inputFileBaseName
        cmdGetKey.setInputPath(inputPath)
        samples = long(cmdGetKey.getKeyValue())
        if self.bDebug: 
            print "tried to get number of Samples now."
            print "Samples: ",samples
        cmdGetKey = ISIS_getkey('Lines')
        cmdGetKey.setInputPath(self.sSourcePath + inputFileBaseName)
        lines = long(cmdGetKey.getKeyValue())
        if self.bDebug: 
            print "tried to get number of Lines now."
            print "Lines: ",lines
        cropCmd = ISIS_crop()        
        cropCmd.setInputPath(self.sSourcePath + self.generateInputBasename(self.sCropper, detec))
        croppedName = self.sSourcePath + self.generateOutputBasename(self.sCropper, detec)
        cropCmd.setOutputPath(croppedName)
        sampPar = "samp={0}".format(samples/2)
        linePar = "line={0}".format(lines/2)
        cropCmd.addParameters([sampPar,linePar])
        if self.bDebug: 
            print "Calling crop with \n",cropCmd.getExeList()
        cropCmd.execute()
        phocmd = self.dIsisProgs[self.sPhocube](['incidence'])
        phocmd.setInputPath(croppedName)
        phocmd.setOutputPath(self.sDestPath + self.generateOutputBasename(self.sPhocube, detec))
        if self.bDebug: 
            print "calling phocube with \n",phocmd
        subprocess.call(phocmd.getExeList())
        self.generateSpiceInfo()
        
    def process(self):
        print "Programs that will be executed: ", self.lListToExecute
        for prog in self.lListToExecute:
            print "Processing obsID {1}, colour {2} with {0}".format(prog, 
                                                                     self.sObsID, 
                                                                     self.sColour)
            sSourcePath = self.sSourcePath
            sDestPath = self.sDestPath
            # hi2isis is the only one reading from original files (currently in /imgdata)
            if prog == self.sConverter: 
                sSourcePath = getSourcePathFromID(self.sObsID)
            if not os.path.exists(sDestPath): 
                print "Destination folder does not exist."
                print "Creating " + sDestPath + " for you."
                if not self.bFake: 
                    os.makedirs(sDestPath)
            os.chdir(sDestPath)
            # determine if to work with CCD IDs or with channel IDs:
            if prog in self.lWorkOnChannels:
                if self.bDebug: 
                    print "generating channel id iterator"
                myIter = self.ccd.generateChannelID()
            else:
                if self.bDebug: 
                    print "generating ccd id iterator" 
                myIter = self.ccd.generateCCDID()
            # if we need to process phocube, call it and jump to next program afterwards
            if prog == self.sPhocube:
                self.processPhoCube(myIter)
                continue
            procs = []
            toDelete = []
            if not prog in self.lCommandsWithList:
                if self.bDebug: 
                    print "In loop for multiple inputs"
                bFoundAny = False
                for i,detector in enumerate(myIter):
                    # get the ISIS command object
                    cmd = self.dIsisProgs[prog]()
                    # now check for any special settings
                    inputFileBaseName = self.generateInputBasename(prog, detector)
                    if self.bDebug: 
                        print "inputFileBaseName: ",inputFileBaseName
                    if prog == self.sStitcher:
                        inputFileBaseName2 = self.generateInputBasename(prog, myIter.next())
                        outputFileBaseName = self.generateOutputBasename(prog, detector[:4])
                    else: 
                        outputFileBaseName= self.generateOutputBasename(prog, detector)
                        if self.bDebug: 
                            print "outputFileBaseName: ",outputFileBaseName
                    inputFullPath = pjoin(sSourcePath, inputFileBaseName)
                    if os.path.exists(inputFullPath): 
                        cmd.setInputPath(inputFullPath)
                        bFoundAny = True
                    else:
                        if self.bDebug: 
                            print """did not find {0}, continuing with next detector.
                                  \n(Maybe input files were already deleted at previous 
                                  processing step?)""".format(inputFullPath) 
                        continue
                    if cmd.bInputToDelete: 
                        if self.bDebug: 
                            print "Adding {0} to toDelete-List.".format(inputFullPath)
                        toDelete.append(pjoin(sSourcePath, inputFileBaseName))
                    if prog == self.sStitcher:
                        cmd.setInputPath2(pjoin(sSourcePath, inputFileBaseName2))
                        if cmd.bInputToDelete: 
                            toDelete.append(pjoin(sSourcePath, inputFileBaseName2))
                    cmd.setOutputPath(pjoin(sDestPath, outputFileBaseName))
                    if (prog == self.sMapper) and self.mapfile: 
                        cmd.setMap(self.mapfile)
                    # time to execute
                    if self.bFake: 
                        print cmd
                    elif not prog in self.lExecuteSingle:
                        if self.bDebug: 
                            print "before multiprocess-call"
                            print cmd.getExeList()
                        p = Process(target=executeIsisCmd, args=(cmd.getExeList(),))
                        procs.append(p)
                        p.start()
                    else:
                        # some ISIS progs like cubenorm do not like to be run in parallel
                        if self.bDebug: 
                            print "before single process loop"
                        print "Working on", i
                        output = executeIsisCmd(cmd.getExeList())
                        if self.bDebug: 
                            print output
                # end of detector iterator
                if not bFoundAny:
                    print "Could not find any input path for {0}, exiting.".format(prog)
                    sys.exit()
                if self.bDebug:
                    print "{0} processes to be joined".format(len(procs))
                    print "Content of toDelete: ",toDelete
                if (len(procs) == 0) and (not prog in self.lExecuteSingle):
                    print "did not call any process for {0},exiting.".format(prog)
                    sys.exit()
                try:
                    for proc in procs: proc.join()
                except:
                    print "Something wrong with process joining"
                    sys.exit()
                for fName in toDelete:
                    print "Deleting ",fName
                    try:
                        if not self.bFake: 
                            os.remove(fName)
                    except OSError:
                        if self.bDebug: 
                            print "Tried to delete non-existing file"
            # if program works with inputLists
            else:
                if self.bDebug: 
                    print "in part for list input"
                cmd = self.dIsisProgs[prog]()
                inputListFileName = self.generateInputList(prog) 
                cmd.setInputPath(inputListFileName)
                cmd.setOutputPath(pjoin(self.sDestPath, 
                                        self.generateOutputBasename(prog, self.ccd.sColour)))
                if prog == self.sEqualizer: 
                    cmd.setHoldList()
                if self.bFake: 
                    print cmd
                else: 
                    if self.bDebug: 
                        print cmd
                    output = executeIsisCmd(cmd.getExeList())
                    if self.bDebug: 
                        print output
                if cmd.bInputToDelete:
                    fListOfFiles = open(inputListFileName)
                    for fName in fListOfFiles:
                        print "Deleting ",fName
                        try:
                            if not self.bFake: 
                                os.remove(fName.splitlines()[0])
                        except OSError:
                            if self.bDebug: 
                                print "Tried to delete non-existing file"

            # if phocube just finished, let's create the spiceinfo file for later analysis
            if prog == self.sPhocube:
                self.generateSpiceInfo()   
 

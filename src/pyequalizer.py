#!/usr/bin/python

import sys, glob
from hirise_tools import *
import subprocess
import time


def main():
    startTime = time.time()

    print "{0} started.".format(sys.argv[0])
    try:    
        idString = sys.argv[1]
        colour = sys.argv[2]
    except:
        print "Usage: {0} idString CCD-colour".format(sys.argv[0])
        print " Only RED is implemented as CCD-colour so far."
        sys.exit()
   
    sourcePath   = getDestPathFromID(idString)

    os.chdir(sourcePath)
    extensions = '.map.norm.cal.cub'
    fileNames = glob.glob(sourcePath + '*' + colour + '*' + extensions)
    fileNames.sort()
    equalizeInputList=idString + '_' + colour + '_toEqualize.lis'
    outfile = open(equalizeInputList,'w')
    for fileName in fileNames:
        print fileName
        outfile.write(fileName + '\n')
    outfile.close()
    print "Created ",equalizeInputList
    eqStatsFileName = idString + '_' + colour + '.eqstats.txt'
    isisCMD = ['equalizer']
    isisCMD.append('fromlist=' + equalizeInputList)
    isisCMD.append('to=' + sourcePath + eqStatsFileName)
    isisCMD.append('holdlist=' + equalizeInputList)
    isisCMD.append('apply=true')
    
    executeIsisCmd(isisCMD)

    endTime = time.time()
    print "Seconds run: ", endTime-startTime
    for fName in fileNames:
        print "Deleting ",fName
        os.remove(fName)
     
        
if __name__ == '__main__':
    main()
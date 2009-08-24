#!/usr/bin/python

import sys, glob
from hirise_tools import *
import subprocess
import time
import string


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

    extensions = ['map','norm','cal','equ','cub']
    fileNames = glob.glob(sourcePath + '*' + colour + '*.' + string.join(extensions,'.'))
    fileNames.sort()
    mosaicInputList=idString + '_toMosaic.lis'
    outfile = open(mosaicInputList,'w')
    for fileName in fileNames:
        print fileName
        outfile.write(fileName + '\n')
    outfile.close()
    print "Created ",mosaicInputList
    mosaicName = idString + '_' + colour + '.' + string.join(extensions[:-1],'.') + '.mos.cub'
    isisCMD = ['automos']
    isisCMD.append('fromlist=' + mosaicInputList)
    isisCMD.append('mosaic=' + sourcePath + mosaicName)
    isisCMD.append('priority=beneath')
    executeIsisCmd(isisCMD)

    endTime = time.time()
    print "Seconds run: ", endTime-startTime
    for fName in fileNames:
        print "Deleting ",fName
        os.remove(fName)
        
if __name__ == '__main__':
    main()
#!/usr/bin/python
import sys,os
from hirise_tools import *
from multiprocessing import Process
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
    
    # for RED colour, it's 10 CCDs
    if colour == 'RED': noCCDs = 10
    procs = []
    toDelete = []
    for ccd in range(10):
        fileBase = idString + '_' + colour + str(ccd) + '.cal.cub'
        newFileName = idString + '_' + colour + str(ccd) + '.norm.cal.cub'
        if not os.path.exists(sourcePath + fileBase):
            print "{0} CCD number {1} does not exist.".format(colour,ccd)
            continue
        isisCMD = ['cubenorm']
        isisCMD.append('from=' + sourcePath + fileBase)
        isisCMD.append(' to=' + sourcePath + newFileName)
        toDelete.append(sourcePath + fileBase)
        subprocess.call(isisCMD)
    #    print isisCMD
#        p = Process(target=subprocess.call, args=(isisCMD,))
#        procs.append(p)
#        p.start()
#            
#    for proc in procs:
#        proc.join()
        
    endTime = time.time()
    print "Seconds run: ", endTime-startTime
    for fName in toDelete:
        print "Deleting ",fName
        os.remove(fName)


if __name__ == '__main__':
    main()

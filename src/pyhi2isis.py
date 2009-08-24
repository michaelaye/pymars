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
    
    sourcePath = getSourcePathFromID(idString)
    destPath   = getDestPathFromID(idString)
    
    if not os.path.exists(destPath): 
        print "Destination folder does not exist."
        print "Creating " + destPath + " for you."
        os.mkdir(destPath)
    
    # for RED colour, it's 10 CCDs
    procs = []
    for ccd in range(10):
        for channel in range(2):
            fileBase = idString +'_' + colour + str(ccd) + '_' + str(channel) + '.IMG'
            newFileName = idString + '_' + colour + str(ccd) +'_' + str(channel) + '.cub'
            if not os.path.exists(sourcePath + fileBase):
                print "{0} CCD number {1}, channel {2} does not exist.".format(colour,ccd,channel)
                continue
            isisCMD = ['hi2isis']
            isisCMD.append('from=' + sourcePath + fileBase)
            isisCMD.append(' to=' + destPath + newFileName)
            try:
                p = Process(target=subprocess.call, args=(isisCMD,))
            except OSError:
                print "Had trouble calling mappt program, did you forget to 'start_isis' ?"
                print "Exiting"
                sys.exit()
            procs.append(p)
            p.start()
            
    for proc in procs:
        proc.join()
        
    endTime = time.time()
    print "Seconds run: ", endTime-startTime


if __name__ == "__main__":
    main()
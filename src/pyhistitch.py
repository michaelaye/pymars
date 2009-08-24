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
#        shallDelete = sys.argv[3]
    except:
        print "Usage: {0} idString CCD-colour".format(sys.argv[0])
        print " Only RED is implemented as CCD-colour so far."
        sys.exit()
   
    print "Working..."    
    sourcePath   = getDestPathFromID(idString)
    
    # for RED colour, it's 10 CCDs
    if colour == 'RED': noCCDs = 10
    procs = []
    toDelete = []
    for ccd in range(10):
        fileBase1 = idString +'_' + colour + str(ccd) + '_' + str(0) + '.cal.cub'
        fileBase2 = idString +'_' + colour + str(ccd) + '_' + str(1) + '.cal.cub'
        newFileName = idString + '_' + colour + str(ccd) + '.cal.cub'
        if not (os.path.exists(sourcePath + fileBase1) and os.path.exists(sourcePath + fileBase2)):
            print "{0} CCD number {1}, one or both channels do not exist.".format(colour,ccd)
            continue
        isisCMD = ['histitch']
        isisCMD.append('from1=' + sourcePath + fileBase1)
        isisCMD.append('from2=' + sourcePath + fileBase2)
        isisCMD.append('balance=true')
        toDelete.append(sourcePath+fileBase1)
        toDelete.append(sourcePath+fileBase2)
        isisCMD.append(' to=' + sourcePath + newFileName)
    #    print isisCMD
        p = Process(target=subprocess.call, args=(isisCMD,))
        procs.append(p)
        p.start()
            
    for proc in procs:
        proc.join()
        
    endTime = time.time()
    print "Seconds run: ", endTime-startTime
 #   if shallDelete == 'yes':
    for fName in toDelete:
        print "Deleting ",fName
        os.remove(fName)
        
if __name__ == '__main__':
    main()
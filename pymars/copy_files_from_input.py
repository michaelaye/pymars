'''
Created on Aug 3, 2009

@author: aye
'''
import csv, glob, hirise_tools, os, shutil

reader = csv.reader(open('IncaCity_obsIDs_input.csv'))


for row in reader:
    obsID = row[0]
    sourceDir = hirise_tools.getDestPathFromID(obsID)
    destDir = '/processed_data'
    newDirName = os.path.join(destDir,obsID)
    if not os.path.exists(newDirName):
        print obsID, 'not there, creating'
        os.mkdir(newDirName)
    toCopy= []
    toCopy.extend(glob.glob(os.path.join(sourceDir, '*.equ.mos.cub')))
    toCopy.extend(glob.glob(os.path.join(sourceDir, '*.equstats.pvl')))
    for f in toCopy:
        newPath = os.path.join(newDirName, os.path.basename(f))
        print "rename args:\n {0}\n{1}".format(f,newPath)
        os.rename(f,newPath)

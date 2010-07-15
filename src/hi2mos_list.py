#!/usr/bin/python

import ISIS
import csv
import time
import sys
import os.path
from hirise_tools import *
import twitter

args = sys.argv

def print_usage():
    print "Usage: {0} inputListFile ccdColour[RED,BG,IR]".format(args[0])

try:
    inputListFile = args[1]
    colour = args[2]
except:
    print_usage()
    sys.exit()
    

reader = csv.reader(open(inputListFile))

start = time.time()

for row in reader:
    obsID = row[0]
    if obsID == '': continue
    print obsID
    targetPath = getMosPathFromIDandCCD(obsID, colour, in_work=True)
    if os.path.exists(targetPath):
        continue
    executer = ISIS.ISIS_Executer(obsID ,colour)
    executer.process()
    api = twitter.Api('hirise_bern', 'hiRISE_BERN')
    api.PostUpdate(' '.join([idString, colour, 'finished']))
    
end = time.time()

print "time in hours:" (end-start)/3600.0
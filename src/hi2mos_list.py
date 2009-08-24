#!/usr/bin/python

import ISIS, csv, time, sys
from production_notifier import sendMail

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
    executer = ISIS.ISIS_Executer(obsID ,colour)
    executer.process()
    sendMail(obsID + ' ' + colour +' finished.','')
    
end = time.time()

print "time in hours:" (end-start)/3600.0
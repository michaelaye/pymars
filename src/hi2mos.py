#!/usr/bin/python

import ISIS, sys
from production_notifier import *

args = sys.argv

if len(args) < 2:
    print "Usage: {0} obsID CCDColour [comma separated list of isis commands, default: ALL]".format(args[0])
    sys.exit()
    
idString = args[1]
colour = args[2]

try:
    lCommands = (args[3]).split(',')
except:
    print "Found no command instruction, Doing all."
    lCommands = None

try:
    dummy = (args[4])
    bDebug = True
except:
    bDebug = None

try:
    dummy = (args[5])
    bFake = True
except:
    bFake = None
    
executer = ISIS.ISIS_Executer(idString,colour, plProgList = lCommands, pbDebug = bDebug, pbFake = bFake)
executer.process()

if lCommands == None: lCommands = ['all']
sendMail(' '.join([idString, colour, 'finished']),' '.join(lCommands))

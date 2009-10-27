#!/usr/bin/python

import ISIS, sys
from production_notifier import *

from optparse import OptionParser

parser = OptionParser()
usage = "usage: %prog obsID CCDColour mapfile [options]"
descript = "obsID should be in the official form XSP_oooooo_tttt , with XSP = PSP or ESP,"\
              "oooooo the 6-digit orbit number and tttt the 4-digit target code."\
              "CCDColour should be one of RED, BG, or IR."\
              "mapfile is the path to the mapping file that contains the required information"\
              "for the mapping, like mapping central coordinate and desired resolution."\
              "Note that for a mosaic, all elements of the mosaic need to be mapped to the same"\
              "resolution. See the ISIS website for more info."
              
parser = OptionParser(usage=usage,description=descript)
parser.add_option("-d", "--debug",
                  action="store_true", dest="debug", default=False,
                  help="print debug messages")
parser.add_option("-f", "--fake",
                  action="store_true", dest="fake", default=False,
                  help="fake the execution, some errors will appear, no real file operation will be done")
parser.add_option("-c", "--command-list", dest="commandList",
                  help="per default, the full list of ISIS commands are executed, "
                        "to create a calibrated map-projected mosaic out of all CCD's "
                        "that are found for the given CCDColour."
                        "If you do not want to execute the full list, you can provide here"
                        "a comma-separated list (no spaces!) of ISIS commands to be run, "
                        "but they have to be chosen from only the default list (so far),"
                        "otherwise they are not known in this framework.")


(options, args) = parser.parse_args()

try:
    idString = args[0]
    colour = args[1]
    mapfile = args[2]
except:
    parser.print_help()
    sys.exit(0)


if options.commandList:
    lCommands = options.commandList.split(',')
else:
    print "Found no command instruction, Doing all."
    lCommands = None
    
executer = ISIS.ISIS_Executer(idString, colour, 
                              plProgList = lCommands, 
                              pbDebug = options.debug, 
                              pbFake = options.fake,
                              pMapfile = mapfile)
executer.process()

if lCommands == None: lCommands = ['all']
sendMail(' '.join([idString, colour, 'finished']),' '.join(lCommands))

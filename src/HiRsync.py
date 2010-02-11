#!/usr/bin/python

import subprocess
import os.path
import sys
from hirise_tools import *

class HiRsync:
    SOURCE = "hisync.lpl.arizona.edu::hirise_data"
    PARAM_TEST = "-avnLh"
    PARAM_REAL = "-avLh"
    PARAM_LIST = "-avn"
    PROGRESS = "--progress"
    DEST_FOLDER_JP2 = "/imgdata/RDRgen/JP2s/"
    DEST_FOLDER_IMG = "/imgdata"
    EXCLUDES = [ ".*" ]
    RSYNC = "/usr/bin/rsync"
    
    def __init__(self,
                 dataType=None,
                 obsID=None,
                 do=False,
                 testing=False,
                 listMode=False,
                 folderExt=None):
        """
        jp2|img obsID [do=True|False(default),
        testing=True|False(default),
        listMode=True|False(default).
        'do' is for the rsync test mode.
        'testing' is for debugging to not type in an obsID
        'listMode' is for getting the folder listings at the hisync server
        """
        cmd = [self.RSYNC]
        cmd.append(self.PROGRESS)
        for exclude in self.EXCLUDES:
            cmd.append("--exclude=%s" % exclude)
        if dataType is None or obsID is None:
            if listMode is True:
                print "Not built in yet"
                raise TypeError('listMode not built in yet')
#                cmd.append(self.PARAM_LIST)
#                paraString = '/'.join([self.SOURCE])
            elif testing is True:
                obsID = 'ESP_012344_0950'
                dataType = 'img'
            else:
                raise TypeError('Need dataType, when not in listMode or '
                                'testing mode.')
        if do is False:
            cmd.append(self.PARAM_TEST)
        else:
            cmd.append(self.PARAM_REAL)
        sciencePhase, orbitNumber, targetCode = obsID.split("_")
        orbitFolder = getUpperOrbitFolder(orbitNumber)
        self.orbitFolder = orbitFolder
        if dataType.upper() == "JP2":
            dataCat = "RDRgen"
            destFolder = self.DEST_FOLDER_JP2
        elif dataType.upper() == "IMG":
            dataCat = "EDRgen"
            destFolder = self.get_EDRdestfolder(orbitNumber)
        else:
            raise ValueError('Only jp2 or img are allowed as dataType')
        paraString = "/".join([self.SOURCE,
                               dataCat,
                               sciencePhase.upper(),
                               orbitFolder,
                               obsID
                               ])
        cmd.append(paraString.encode())
        cmd.append(destFolder)
        self.cmd = cmd
        
    def get_EDRdestfolder(self, orbitNumber):
        EDRfolder = getEDRFolder(orbitNumber)
        return os.path.join(self.DEST_FOLDER_IMG,
                             EDRfolder,
                             self.orbitFolder)
    
    def __str__(self): 
        return " ".join(self.cmd)

    def execute_cmd(self):
        p = subprocess.Popen(self.cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print "StdOut:", stdout
        print "StdErr:", stderr
        return

if __name__ == "__main__":
    import sys
    from optparse import OptionParser
    
    usage = "usage: %prog [jp2|img] obsID [-d | -t ]"

    descript = """Utility to download datafiles from the hisync server in 
Arizona. So far, only the automatic download of EDR IMGs and RDR JP2s have 
been implemented. Image files will be placed in the correct folders, wherever
you use this utility. The correct folders will be determined by the 
observationID. Please note, that without the -d (=DO) flag, it will only make a
test run."""
              
    parser = OptionParser(usage=usage, description=descript)
    parser.add_option("-d", "--do",
                      action="store_true", dest="do", default=False,
                      help="do the download")
    parser.add_option("-t", "--testing",
                      action="store_true", dest="testing", default=False,
                      help="""use the built-in test mode to create some
                      default obsID and dataType for you. In this case you
                      do not need to give jp2|img and obsID as default 
                      parameters.""")
    parser.add_option("-l",
                      "--list-mode",
                      dest="listMode",
                      help="""Special mode to show only the folders on hisync.
                            Not functional yet.""")


    (options, args) = parser.parse_args()
    if options.testing is True:
        hirsync = HiRsync(testing=True)
    elif len(args) == 0:
        parser.print_help()
        sys.exit(0)
    else:
        try:
            datatype = args[0]
            obsid = args[1]
        except:
            print('\n Something went wrong at assignment of parameters! \n')
            parser.print_help()
            sys.exit(-1)
        else:
            hirsync = HiRsync(dataType=datatype,
                      obsID=obsid,
                      do=options.do,
                      testing=options.testing,
                      listMode=options.listMode)
    print(hirsync)
    hirsync.execute_cmd()

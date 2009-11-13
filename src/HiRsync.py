import subprocess
import os.path
from hirise_tools import *

class HiRsync:
    SOURCE = "hisync.lpl.arizona.edu::hirise_data"
    #  !!remove 'n' here to go hot!!
    PARAM_TEST = "-avnLh"
    PARAM_REAL = "-avLh"
    PARAM_LIST = "-avn"
    PROGRESS = "--progress"
    DEST_FOLDER_JP2 = "/imgdata/RDRgen/JP2s/"
    DEST_FOLDER_IMG = "/imgdata"
    EXCLUDES = [ ".*" ]
    RSYNC = "/usr/bin/rsync"
    
    def __init__(self, dataType=None, obsID=None, runForReal=False,
                 testing=False, listMode=False):
        """
        runForReal is for the rsync test mode.
        testing is for debugging to not type in an obsID
        listMode is for getting the folder listings at the hisync server
        """
        cmd = [self.RSYNC]
        if dataType is None:
            if listMode is True:
                cmd.append(self.PARAM_LIST)
            else:
                raise TypeError('Need dataType, when not in listMode')
        if runForReal is False:
            cmd.append(self.PARAM_TEST)
        else:
            cmd.append(self.PARAM_REAL)
        if obsID is None:
            if testing is True:
                obsID = 'ESP_012344_0950'
            else:
                raise TypeError('Need obsID, when testing=False')
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
        cmd.append(self.PROGRESS)
        for exclude in self.EXCLUDES:
            cmd.append("--exclude=%s" % exclude)
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
    argv = sys.argv
    print argv[1], argv[2]
    hirsync = HiRsync(dataType=argv[1], obsID=argv[2], runForReal=True)
    print(hirsync)
    hirsync.execute_cmd()

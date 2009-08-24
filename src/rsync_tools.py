from rsync_parameters import *
import subprocess

def getUpperOrbitFolder(orbitNumber):
#===============================================================================
# get the upper folder name where the given orbit folder is residing on the hisync server
# input: orbitNumber(int)
#===============================================================================
    lower = int(orbitNumber)/100*100
    return "_".join(["ORB", str(lower).zfill(6), str(lower+99).zfill(6)])


def getRsyncCmd(dataType, imgID):
    sciencePhase, orbitString, targetCode = imgID.split("_")
    orbitFolder = getUpperOrbitFolder(orbitString)
    if dataType == "JP2":
        dataCat = "RDRgen"
        destFolder = DEST_FOLDER_JP2
    elif dataType == "IMG":
        dataCat = "EDRgen"
        destFolder = DEST_FOLDER_IMG + '/' + orbitFolder
    cmd = [RSYNC]
    cmd.append(PARAM1)
    cmd.append(PARAM2)
    for exclude in EXCLUDES:
      cmd.append("--exclude=%s" % exclude)
    paraString = "/".join([SOURCE, dataCat, orbitFolder, imgID])
    cmd.append(paraString.encode())
    cmd.append(destFolder)
    return cmd

def executeCmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print "StdOut:", stdout
    return
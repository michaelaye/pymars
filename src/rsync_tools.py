from rsync_parameters import *
import subprocess

def getUpperOrbitFolder(orbitNumber):
#===============================================================================
# get the upper folder name where the given orbit folder is residing on the hisync server
# input: orbitNumber(int)
#===============================================================================
    """Return the upper folder name where the given orbit folder is residing on the hisync server.
    
    >>> getUpperOrbitFolder(3456)
    'ORB_003400_003499'
    >>> getUpperOrbitFolder(-1)
    Traceback (most recent call last):
      File "/usr/lib/python2.6/doctest.py", line 1241, in __run
        compileflags, 1) in test.globs
      File "<doctest rsync_tools.getUpperOrbitFolder[1]>", line 1, in <module>
        getUpperOrbitFolder(-1)
      File "rsync_tools.py", line 24, in getUpperOrbitFolder
        raise ValueError('Orbit number must be > 0 ! ')
    ValueError: Orbit number must be > 0 ! 
    """
    if orbitNumber < 0:
        raise ValueError('Orbit number must be > 0 ! ')
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
import subprocess

# TODO: check for write rights

class HiRsync:
    SOURCE = "hisync.lpl.arizona.edu::hirise_data"
    #  !!remove 'n' here to go hot!!
    PARAM1 = "-avnLh"
    PARAM2 = "--progress"
    DEST_FOLDER_JP2 = "/imgdata/RDRgen/JP2s/"
    DEST_FOLDER_IMG = "/imgdata"
    EXCLUDES = [ ".*" ]
    RSYNC = "/usr/bin/rsync"
    
    def __init__(self, dataType, obsID):
        sciencePhase, orbitString, targetCode = obsID.split("_")
        orbitFolder = self.getUpperOrbitFolder(orbitString)
        if dataType == "JP2":
            dataCat = "RDRgen"
            destFolder = self.DEST_FOLDER_JP2
        elif dataType == "IMG":
            dataCat = "EDRgen"
            destFolder = self.DEST_FOLDER_IMG + '/' + orbitFolder
        cmd = [self.RSYNC]
        cmd.append(self.PARAM1)
        cmd.append(self.PARAM2)
        for exclude in EXCLUDES:
          cmd.append("--exclude=%s" % exclude)
        paraString = "/".join([self.SOURCE, dataCat, orbitFolder, obsID])
        cmd.append(paraString.encode())
        cmd.append(destFolder)
        self.cmd = cmd
        
    def __str__(self):
        return "\n".join(self.cmd)

    def getUpperOrbitFolder(selff, orbitNumber):
        """Return the upper folder name where the given orbit folder is 
        residing on the hisync server.
        inputParamter: positive orbit number, negative number will raise an 
        error.
        
        >>> HiRsync.getUpperOrbitFolder(3456)
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
        lower = int(orbitNumber) / 100 * 100
        return "_".join(["ORB", str(lower).zfill(6), str(lower + 99).zfill(6)])

    def executeCmd(self):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print "StdOut:", stdout
        return

if __name__ == "__main__":
    import doctest
    doctest.testmod()

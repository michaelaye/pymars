import os, subprocess, sys

FROM_BASE = "/imgdata/"
DEST_BASE = "/processed_data/"

class Coordinates:
    path = ''
    obsID = 0
    sample = 0
    line = 0
    latitude = 0
    longitude = 0
    x = 0
    y = 0

def getCCDColourFromMosPath(path):
    basename = os.path.basename(path)
    firstpart = basename.partition('.')[0]
    return firstpart.split('_')[3]

def getObsIDFromPath(path):
    basename = os.path.basename(path)
    obsID = basename[:15]
    try:
        phase, orbit, targetcode = obsID.split('_')
    except ValueError:
        print("Path does not have standard ObsID, returning first 15 characters.")
    return obsID

def getUpperOrbitFolder(orbitNumber):
    '''
    get the upper folder name where the given orbit folder is residing on the 
    hisync server
    input: orbitNumber(int)
    '''
    lower = int(orbitNumber) / 100 * 100
    return "_".join(["ORB", str(lower).zfill(6), str(lower + 99).zfill(6)])

def getEDRFolder(orbitNumber):
    '''
    get the upper folder name where the given orbit folder is stored on hirise
    input: orbitNumber(int)
    '''
    lower = int(orbitNumber) / 1000 * 1000
    return "_".join(["EDRgen", str(lower).zfill(6), str(lower + 999).zfill(6)])

def getUsersProcessedPath():
    path = DEST_BASE
    path += os.environ['LOGNAME'] + '/'
    return path

def getSourcePathFromID(idString):
    sciencePhase, orbitString, targetCode = idString.split("_")
    path = FROM_BASE
    path += getEDRFolder(int(orbitString)) + '/'
    path += getUpperOrbitFolder(int(orbitString)) + '/' + idString + '/'
    return path

def getDestPathFromID(idString):
    path = getUsersProcessedPath()
    path += idString + '/'
    return path

def getStoredPathFromID(idString):
    path = DEST_BASE + idString + '/'
    return path

def executeIsisCmd(args):
    """as we are using check_call here, the input should be a list with strings,
        like ['ls','-l','-a']
    """
    try:
        p = subprocess.check_call(args)
    except OSError:
        print "Caught OSError. Did you forget to start_isis?"
        raise
        sys.exit()
    except subprocess.CalledProcessError:
        print "Process returned non-zero exit status. Command was called but did not succeed."
        sys.exit()
    return

def executeIsisCmdWithReturn(psArgs):
    '''
    This function takes a cmd string as argument, exactly as it would be typed in 
    the shell, so for example:
    psArgs = 'hi2isis from=pathToSource to=pathToDest'
    return: text output of the command
    '''
    try:
        output = subprocess.Popen(psArgs, shell=True, stdout=subprocess.PIPE).communicate()[0]
    except OSError:
        print "Caught OSError. Did you forget to start_isis?"
        sys.exit()
    except subprocess.CalledProcessError:
        print "Process returned non-zero exit status. Command was called but did not succeed."
 #       print output
        sys.exit()
    else:
        return output


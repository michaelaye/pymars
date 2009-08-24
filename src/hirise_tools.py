import isis_settings, os, subprocess, sys

class Coordinates:
    imageID  = 0
    sample   = 0
    line     = 0
    latitude = 0
    longitude= 0
    x        = 0
    y        = 0
 
def getUpperOrbitFolder(orbitNumber):
    '''
    get the upper folder name where the given orbit folder is residing on the hisync server
    input: orbitNumber(int)
    '''
    lower = int(orbitNumber)/100*100
    return "_".join(["ORB", str(lower).zfill(6), str(lower+99).zfill(6)])

def getEDRFolder(orbitNumber):
    '''
    get the upper folder name where the given orbit folder is residing on the hisync server
    input: orbitNumber(int)
    '''
    lower = int(orbitNumber)/1000*1000
    return "_".join(["EDRgen", str(lower).zfill(6), str(lower+999).zfill(6)])

def getUsersProcessedPath():
    path = isis_settings.DEST_BASE
    path += os.environ['LOGNAME'] + '/'
    return path

def getSourcePathFromID(idString):
    sciencePhase, orbitString, targetCode = idString.split("_")
    path = isis_settings.FROM_BASE
    path += getEDRFolder(int(orbitString)) + '/'
    path += getUpperOrbitFolder(int(orbitString)) + '/' + idString + '/'
    return path

def getDestPathFromID(idString):
    path = getUsersProcessedPath()
    path += idString + '/'
    return path

def executeIsisCmd(args):
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


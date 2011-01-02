import os, subprocess, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import colors

FROM_BASE = "/imgdata/"
DEST_BASE = "/Users/aye/Data/ctx/inca_city/"

# mosaic_extensions = '.cal.norm.map.equ.mos.cub'
mosaic_extensions = '.cal.des.map.cub'

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
    try:
        return firstpart.split('_')[3]
    except:
        print path

def getObsIDFromPath(path, instr = 'hirise'):
    basename = os.path.basename(path)
    if instr == 'hirise':
        obsID = basename[:15]
        try:
            phase, orbit, targetcode = obsID.split('_')
        except ValueError:
            print("Path does not have standard ObsID, returning first 15 characters.")
        return obsID
    if instr == 'ctx':
        try:
            obsID = basename.split('_')[1]
        except IndexError:
            print("Path does not have CTX file name format. Returning empty")
            return ''
            

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

def getStoredPathFromID(idString, in_work=False):
    folder = ''
    if in_work == True:
        folder = 'maye/'
    path = DEST_BASE + folder + idString + '/'
    return path

def getMosPathFromIDandCCD(obsID, ccd, in_work=False):
    root = getStoredPathFromID(obsID, in_work)
    path = os.path.join(root, '_'.join([obsID, ccd]) + mosaic_extensions)
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

def rebin(a, newshape):
        '''Rebin an array to a new shape.
        '''
        assert len(a.shape) == len(newshape)

        slices = [ slice(0, old, float(old) / new) for old, new in zip(a.shape, newshape) ]
        coordinates = np.mgrid[slices]
        indices = coordinates.astype('i')   #choose the biggest smaller integer index
        print len(indices),indices.max()
        return a[tuple(indices)]

def rebin_factor(a, newshape):
        '''Rebin an array to a new shape.    
        newshape must be a factor of a.shape.        
        '''
        assert len(a.shape) == len(newshape)
        assert not np.sometrue(np.mod(a.shape, newshape))

        slices = [ slice(None, None, old / new) for old, new in zip(a.shape, newshape) ]
        return a[slices]

def save_plot(data, title, fname, format='png', cb = True,vmax=0.3,vmin=0.0):
    """quick saving of some data in diff. formats"""
    fig = plt.figure()
    ax = fig.add_subplot(111)
    im = ax.imshow(data,interpolation='nearest')#, vmax=0.3,vmin=0.2)#,aspect='equal')
    # im = ax.imshow(data, norm=colors.LogNorm(vmin=0.01,vmax=0.7))
    
    if cb == True:
        # t = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        # plt.colorbar(im, ticks=t, format='$%.2f$')
        plt.colorbar(im)
    ax.set_title(title)
    plt.savefig(fname+'.'+format,dpi=200)
    plt.close(fig)

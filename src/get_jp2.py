import sys
from rsync_tools import *

def main():
    idString = sys.argv[1]
    cmd = getRsyncCmd("JP2", idString)
    print cmd
    executeCmd(cmd)
    
if __name__=="__main__":
    main()
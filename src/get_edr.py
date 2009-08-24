import sys
from rsync_tools import *

idString = sys.argv[1]
cmd = getRsyncCmd("IMG", idString)
print cmd
executeCmd(cmd)


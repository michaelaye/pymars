#!/usr/local/bin/python

import sys, xlrd
from rsync_tools import *

def main(): 
# reading excel file to find which data we want, to define SOURCE part of cmd
  book = xlrd.open_workbook(sys.argv[1])
  sh = book.sheet_by_index(0)
  print str(sh.nrows) + " lines"
# loop over rows in excel sheet
  for r in range(sh.nrows)[1:]:
    imgID = sh.row_values(r)[0]
    if imgID == "": 
      print "Line " + str(r) + " empty"
      continue
    print imgID
    cmd = getRsyncCmd("JP2", imgID)
    print cmd
    executeCmd(cmd)

if __name__ == "__main__":
	main()



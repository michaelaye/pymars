SOURCE = "hisync.lpl.arizona.edu::hirise_data/"
#  !!remove 'n' here to go hot!!
PARAM1 = "-avnLh"
PARAM2 = "--progress"
DEST_FOLDER_JP2 = "/imgdata/RDRgen/JP2s"
DEST_FOLDER_IMG = "/imgdata/"
EXCLUDES = [
  ".*", 
]
RSYNC = "/usr/bin/rsync"
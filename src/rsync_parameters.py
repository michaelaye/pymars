SOURCE = "hisync.lpl.arizona.edu::hirise_data/"
#  !!remove 'n' here to go hot!!
PARAM1 = "-avnLh"
PARAM2 = "--progress"
DEST_FOLDER_JP2 = "/imago1/RedMosaic_Color-JP2-select/"
DEST_FOLDER_IMG = "/imago1/EDRgen/"
EXCLUDES = [
  ".*", 
]
RSYNC = "/usr/bin/rsync"
#!/usr/bin/python

def parse_excel_and_hirsync(dataType, excelFile, do=False):
    import xlrd
    import HiRsync
    book = xlrd.open_workbook(excelFile)
    sh = book.sheet_by_index(0)
    print str(sh.nrows) + " lines"
    # loop over rows in excel sheet
    for r in range(sh.nrows)[1:]:
        obsID = sh.row_values(r)[0]
        if obsID == "": 
          print "Line " + str(r) + " empty"
          continue
        print obsID
        hirsync = HiRsync.HiRsync(dataType=dataType,
                                  obsID=obsID,
                                  do=do)
        print(hirsync)
        hirsync.execute_cmd()

if __name__ == "__main__":
    import sys
    from optparse import OptionParser
    
    parser = OptionParser()
    usage = "usage: %prog [jp2|img] inputExcelFile.xls [-d (for execution!)]"

    descript = """Utility to download datafiles from the hisync server in 
Arizona by using Excel sheets as input. So far, only the automatic download of 
EDR IMGs and RDR JP2s has been implemented. Image files will be placed in the correct 
folders, no matter from where you start this tool. The correct folders will be 
determined by the observationIDs that have to be located in the first sheet,
first column of the Excel input file. Please note, that without the -d (=DO) flag, 
it will only make a test run, showing you the paths where data will be 
stored."""
              
    parser = OptionParser(usage=usage, description=descript)
    parser.add_option("-d", "--do",
                      action="store_true", dest="do", default=False,
                      help="execute the download")


    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        sys.exit(-1)
    else:
        try:
            dataType = args[0]
            excelFile = args[1]
        except:
            print('\n Something went wrong at assignment of parameters! \n')
            parser.print_help()
            sys.exit(-1)
    
    parse_excel_and_hirsync(dataType, excelFile, do=options.do)



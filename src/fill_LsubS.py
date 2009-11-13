#!/usr/bin/python

'''
Created on Jul 15, 2009

@author: aye
'''

from hirise_tools import *
import sys, csv, isis_settings

def main():
    try:
        cvsFileName = sys.argv[1]
    except:
        print "Usage: {0} cvsFile".format(sys.argv[0])
        sys.exit()
    
    try:
        reader = csv.DictReader(open(cvsFileName,"rb"), delimiter = ';')
    except:
        print "something went wrong during reading csv - file"
        sys.exit()
        
    procPath = DEST_BASE # set in hirise_tools
    for myDic in reader:
        sObsId = myDic['Observation_id']
        if not sObsId.endswith('_0815'): continue
        destPath = os.path.join(procPath,sObsId) 
        if not os.path.exists(destPath): 
            print "Destination folder does not exist."
            print "Creating " + destPath + " for you."
            os.mkdir(destPath)
        outfileName = os.path.join(destPath,"_".join([sObsId, 'spiceinfo.txt']))
        print "Creating",outfileName
        outfile = open(outfileName,'w')
        try:
            outfile.write(" ".join([myDic['Ls\xb0'], myDic['INCIDENCE_ANGLE, deg'], '\n']))
            print " ".join([myDic['Ls\xb0'], myDic['INCIDENCE_ANGLE, deg'], '\n'])
        except KeyError:
            try:
                outfile.write(" ".join([myDic['Ls, deg'], myDic['INCIDENCE_ANGLE, deg'], '\n']))
                print " ".join([myDic['Ls, deg'], myDic['INCIDENCE_ANGLE, deg'], '\n'])
            except KeyError:
                print "Caught KeyError. check if key exists."
                continue

if __name__ == "__main__":
    main()
    
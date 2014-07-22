#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="aye"
__date__ ="$Feb 10, 2010 12:18:05 AM$"

import csv
import pickle
import os

def main():
    os.chdir('/Users/aye/Documents/hirise/fans')
    header = ['ObsID',
             'CCDColour',
             'Map_Sample_Offset',
             'Map_Line_Offset',
             'CoReg_Sample_Offset',
             'CoReg_Line_Offset',
             'NSAMPLES',
             'NLINES']
             
    writer = csv.writer(open('coreg_values.csv','wb'))
    writer.writerow(header)

    with open('data/subframes.pkl') as f:
        data, counter = pickle.load(f)

    for item in data:
        row = item[1:]
        row[0] = row[0].rstrip('_RED')
        row.insert(1,'RED')
        row.insert(4,row.pop(6))
        row.insert(5,row.pop(7))
        writer.writerow(row)

print 'Done'
if __name__ == "__main__":
    main()
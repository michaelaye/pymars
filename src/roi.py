#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__ = "aye"
__date__ = "$Feb 10, 2010 12:18:05 AM$"

import csv
import os
from hirise_tools import Coordinates

class ROI_Data():
    """region of interest meta-data collector"""
    keys = ['ObsID',
             'CCDColour',
             'Map_Sample_Offset',
             'Map_Line_Offset',
             'CoReg_Sample_Offset',
             'CoReg_Line_Offset',
             'NSAMPLES',
             'NLINES',
             'L_s',
             'Thresholds']
    def __init__(self, fname=None):
        self.dict = {}
        self.roiName = ''
        self.obsID = ''
        self.ccdColour = ''
        self.inputSample = ''
        self.inputLine = ''
        self.extraTargetCode = ''
        self.outputFileName = ''
        self.mapSampleOffset = ''
        self.mapLineOffset = ''
        self.coregSampleOffset = ''
        self.coregLineOffset = ''
        self.nsamples = ''
        self.nlines = ''
        self.l_s = ''
        self.thresholds = ''
        self.mosaicPath = ''
        if not fname is None:
            self.read_in(fname)

    def write_out(self):
        """important: self.keys is a list of keys for each row,
        self.dict.keys() are the obsIDs that have been stored in 
        the data dictionary self.dict, using obsIDs as the 
        referencing key."""
        self.outputFileName = self.roiName + '.csv'
        csvWriter = csv.DictWriter(open(self.outputFileName, 'wb'),
                                   self.keys)
        csvWriter.writerow(dict(zip(self.keys, self.keys)))
        for obsID in sorted(self.dict.keys()):
            csvWriter.writerow(self.dict[obsID])

    def store_row(self):
        self.dict[self.obsID] = dict(zip(self.keys, [self.obsID,
                                                  self.ccdColour,
                                                  self.mapSampleOffset,
                                                  self.mapLineOffset,
                                                  self.coregSampleOffset,
                                                  self.coregLineOffset,
                                                  self.nsamples,
                                                  self.nlines,
                                                  self.l_s,
                                                  self.thresholds]))

    def read_in(self, fname):
        self.roiName = fname.rstrip('.csv')
        self.data = []
        self.dict = {}
        self.inputFileName = fname
        csvReader = csv.DictReader(open(fname, 'rb'))
        for row in csvReader:
            self.dict[row['ObsID']] = row

    def __str__(self):
        for row in self.data:
            for element in row:
                print str(element),
            print '\n'

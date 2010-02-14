#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__ = "aye"
__date__ = "$Feb 10, 2010 12:18:05 AM$"

import csv
import os
from hirise_tools import Coordinates

class ROI():
    """region of interest meta-data collector"""
    keys = ['ObsID',
             'CCDColour',
             'Map_Sample_Offset',
             'Map_Line_Offset',
             'CoReg_Sample_Offset',
             'CoReg_Line_Offset',
             'NSAMPLES',
             'NLINES']
    def __init__(self):
        self.data = []
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
        self.mosaicPath = ''

    def write_out(self):
        outputFileName = "_".join([self.roi_name,
                                    self.CCDColour])
        outFile = open(outputFileName, 'wb')
        csvWriter = csv.writer(outFile)
        csvWriter.writerow(self.keys)
        csvWriter.writerows(self.data)
        outFile.close()
        
    def store_row(self):
        self.data.append([self.obsID,
                          self.ccdColour,
                          self.mapSampleOffset,
                          self.mapLineOffset,
                          self.coregSampleOffset,
                          self.coregLineOffset,
                          self.nsamples,
                          self.nlines])

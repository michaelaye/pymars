#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__ = "aye"
__date__ = "$Feb 10, 2010 12:18:05 AM$"

import csv
import os

class ROI():
    """region of interest data collector"""
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
        self.sOutputFileName = ''

    def write_out(self):
        sOutputFileName = "_".join([self.roi_name,
                                    self.CCDColour])
        outFile = open(resultFileName, 'wb')
        resultFileName = ""
    def writeRow(self,):
        pass
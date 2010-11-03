#!/usr/bin/python

from pds.core.common import open_pds
from pds.core.parser import Parser
from subprocess import Popen
import matplotlib.pyplot as plt
import os
import glob

def get_labels(fname):
    parser = Parser()
    labels = parser.parse(open_pds(fname))
    return labels

def print_labels_in_folder(folder, label):
    files = glob.glob(folder + "*.IMG")
    for f in files:
        print f
        labels = get_labels(f)
        print labels[label.upper()]
        
def plot_labels_in_folder(folder, label):
    files = glob.glob(folder + "*.IMG")
    data = []
    for f in files:
        print f
        labels = get_labels(f)
        value = labels[label.upper()]
        data.append(float(value.split()[0]))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(data)
    plt.show()

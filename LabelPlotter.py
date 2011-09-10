#!/usr/bin/python

from pds.core.common import open_pds
from pds.core.parser import Parser
import matplotlib.pyplot as plt
import glob
import csv

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

def read_atlas_report(atlas_filename):
    """Scan through atlas PDS search csv and return dictionary with all data."""
    with open(atlas_filename) as f:
        keys = f.readline()
        keys = [key.strip() for key in keys.split(',')]
        reader = csv.DictReader(f,fieldnames=keys)
        atlas_data = {}
        for row in reader:
            atlas_data[row['PRODUCT_ID'].strip()] = row
        return atlas_data
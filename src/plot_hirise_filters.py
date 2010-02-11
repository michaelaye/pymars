#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="aye"
__date__ ="$Feb 9, 2010 6:43:16 PM$"

import matplotlib.pyplot as plt
import numpy as np


def main():
    fig = plt.figure(figsize=(8,3))
    ax= fig.add_subplot(111)
    ygrids = ax.get_ygridlines()
    for line in ygrids:
        line.set_alpha(0.0)
    cyan = plt.Rectangle((400,0.25),200,0.5,
                            fill=True, facecolor='c',alpha='0.5')
    red = plt.Rectangle((550,1),300,0.5,fill=True,facecolor='darkred',alpha='0.8')
    nir = plt.Rectangle((800,1.75),200,0.5,fill=True,facecolor='r',alpha='0.2')
    plt.gca().add_patch(cyan)
    plt.gca().add_patch(red)
    plt.gca().add_patch(nir)
    plt.axis([300,1100,0,2.5])
    plt.xlabel('Wavelength [nm]')
    plt.yticks(visible=False)
    plt.title('HiRISE Filters')
    plt.text(500,0.5, 'BlueGreen', horizontalalignment = 'center',
                verticalalignment = 'center')
    plt.text(700,1.25, 'Red', horizontalalignment = 'center',
                verticalalignment = 'center')
    plt.text(900,2.0, 'Near IR', horizontalalignment = 'center',
                verticalalignment = 'center')

    plt.show()


if __name__ == "__main__":
    main()
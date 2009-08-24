'''
Created on Jul 28, 2009

@author: aye
'''

from subprocess import *

output = Popen(["catlab -h"], shell=True,stdout=PIPE).communicate()[0]

print output

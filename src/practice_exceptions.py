'''
Created on Aug 5, 2009

@author: aye
'''

import sys, subprocess
from multiprocessing import Process


def myCaller(psArgs):
    try:
        output = subprocess.Popen(psArgs, stdout=subprocess.PIPE).communicate()[0]
        for elem in output:
            if "ERROR" in elem:
                raise subprocess.CalledProcessError(output)
    except OSError as inst:
        print "Caught OSError from inside. Did you forget to start_isis?"
        print inst
        raise OSError
    except subprocess.CalledProcessError as inst:
        print inst
        print "Process returned non-zero exit status. Command was called but did not succeed."
    else:
        print "printing output: ", output
#        raise subprocess.CalledProcessError
 
 
for i in range(5):
    try:
        p = Process(target=myCaller, args=(['stats','-abc'],))
    except OSError as inst:
        print inst
        print "Caught OSError from above. Did you forget to use start_isis?"
    except subprocess.CalledProcessError:
        print "program returned non-zero error exit status"
    else:
        p.start()

print "after calling"
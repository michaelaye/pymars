'''
Created on Jul 20, 2009

@author: aye
'''

def func():
    global index
    if index < 10:
        print index
        index +=1
        

index = 0    
print 'calling func'
func()

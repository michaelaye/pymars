from numpy import genfromtxt, mean, nan
from little_helpers.define_my_consts import ro_CO2

def get_fname(lat, lon, Ls, values_of_interest): 
    ### INPUTS: values_of_interest = 'tau', 'TPsurf', or 'dCO2'
    if Ls < 10.0:
        Ls = 360.0
    Ls_str = str(int(Ls))[:-1]+'0'    
    if values_of_interest == 'tau':         
        fname04 ='-9999.00.024.01taunonenonenoneoffoffoffjetNoneNone80.0off.txt'
        directory = '/Users/Anya/Desktop/MCD_NorthPole/tau/'
        #fname[61:62] = 'tau'
    elif values_of_interest == 'TPsurf':
        fname04 = '-9999.00.024.01tsurfpsnonenoneoffoffoffjetNoneNone80.0off.txt'
        directory = '/Users/Anya/Desktop/MCD_NorthPole/tsurfps/'
        #fname[61:66] = 'tsurfps'
    elif values_of_interest == 'dCO2':
        fname04 = '-9999.00.024.01co2icenonenonenoneoffoffoffjetNoneNone80.0off.txt'
        directory = '/Users/Anya/Desktop/MCD_NorthPole/dCO2/'
        #fname[61:65] = 'co2ice'
    else:
        print( '-!- wrong identifyer for MCD value of interest ')
    fname01 = 'v5_32.0NoneNone'
    fname01a = '%0.1f'%lon
    fname02 = 'NoneNone'
    fname02a = '%0.1f'%lat
    fname03 ='NoneNone11'    
    fname03a = Ls_str+'.0'    
    local_dir = str(lon) + 'E' + str(lat)+'N/'
    filename = directory + local_dir + fname01+fname01a+fname02+fname02a+fname03+fname03a+fname04  ### "".join(fname)
    return filename

def read_MCD_daily_values(lat, lon, Ls, nr_vars):   ### Ls - string type for each 10 deg ls; nr_var - how many of variables to read: 1 - only T, 2 - T, P, 3 - T, P, tau
    file = get_fname(lat, lon, Ls, 'TPsurf')
    
    everything = genfromtxt(file, comments='###')
    if nr_vars == 1:
        cl1 = everything[0:25, 0]
        cl2 = everything[0:25, 1]        
        lines=['']
        f = open(file, 'r')
        for i in [0,1,2,3]:
            lines.append( f.readline() )
        f.close()
        units1 = lines[3][16:-1]
        units2 = lines[4][16:-1]
        return cl1, cl2, units1, units2
    elif nr_vars == 2:
        cl1 = everything[0:25, 0]
        cl2 = everything[0:25, 1]
        cl3 = everything[25:, 1]
        lines=['']
        f = open(file, 'r')
        for i in [0,1,2,3]:
            lines.append( f.readline() )
        for i in range(29):
            line = f.readline()
        f.close()
        units1 = lines[3][16:-1]
        units2 = lines[4][16:-1]
        units3 = line[16:-1]
          
    else:
        print( 'nr_vars must be <=2, more is not implemented yet')
    return cl1, cl2, cl3, units1, units2, units3 
        
def read_daily_average_optical_depth(lat, lon, Ls): # returns mean(tau) over one day
    file = get_fname(lat, lon, Ls, 'tau')
    everything = genfromtxt(file, comments='###')
    return mean(everything[0:25, 1])
    
def read_daily_average_CO2_depth(lat, lon, Ls): # returns mean (over one day) CO2 layer in m
    file = get_fname(lat, lon, Ls, 'dCO2')
    everything = genfromtxt(file, comments='###')
    return mean(everything[0:25, 1])/ro_CO2    
    
    
    
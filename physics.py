from scipy.constants import Boltzmann as kb
from scipy.constants import c,h
from numpy import exp

def B_freq(nu, T):
    term1 = (2 * h * nu**3) / c**2
    exponent = (h * nu) / (kb * T)
    term2 = 1 / ( exp(exponent) - 1 )
    return term1 * term2
    
def B_wave(wave, T):
    term1 = (2 * h * c**2) / (wave**5)
    exponent = (h * c) / (wave * kb * T)
    term2 = 1 / ( exp(exponent) - 1 )
    return term1 * term2


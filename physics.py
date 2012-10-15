from scipy.constants import Boltzmann as kb
from scipy.constants import c,h
from numpy import exp
from traits.api import CFloat, HasTraits

class Photon(HasTraits):
    """Collection of photon features.
    
    >>> photon = Photon()
    >>> "{0:g}".format(photon.frequency)
    '2.8176e+14'
    >>> "{0:g}".format(photon.energy)
    '1.86696e-19'
    """
    frequency = CFloat
    wavelength = CFloat
    energy = CFloat
    def __init__(self, wavelength=1064e-9, frequency=None):
        if frequency is not None:
            self.frequency = frequency
            self.wavelength = c / frequency
        else:
            self.wavelength = wavelength
            self.frequency = c / wavelength
        self.energy = self.get_energy()
    def _frequency_changed(self):
        self.wavelength = c / self.frequency
        self.energy = self.get_energy()
    def _wavelength_changed(self):
        self.frequency = c / self.wavelength
        self.energy = self.get_energy()
    def get_energy(self):
        # E = h * f = h * c / lambda
        return h * self.frequency

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

def B_phot(wave, T):
    rads = B_wave(wave,T)
    # E = h*c/lambdat, so N_ph = rads*wavel/(h*c)
    return (rads * wave) / (h * c)
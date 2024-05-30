from pfs.ga.pfsspec.stellar import StellarSpectrum
from .pfsspectrum import PfsSpectrum

class PfsStellarSpectrum(StellarSpectrum, PfsSpectrum):
    def __init__(self, orig=None):
        StellarSpectrum.__init__(self, orig=orig)
        PfsSpectrum.__init__(self, orig=orig)

    def get_param_names(self):
        params = PfsSpectrum.get_param_names(self)
        params += StellarSpectrum.get_param_names(self)
        return params
    
    def get_name(self):
        return PfsSpectrum.get_name(self)
from pfs.ga.pfsspec.stellar import StellarSpectrum
from .pfsspectrum import PfsSpectrum

class PfsStellarSpectrum(PfsSpectrum, StellarSpectrum):
    def __init__(self, orig=None):
        PfsSpectrum.__init__(self, orig=orig)
        StellarSpectrum.__init__(self, orig=orig)

    def get_param_names(self):
        params = PfsSpectrum.get_param_names(self)
        params += StellarSpectrum.get_param_names(self)
        return params
    
    def get_name(self):
        return PfsSpectrum.get_name(self)
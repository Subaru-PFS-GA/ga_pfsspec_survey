import numpy as np

from pfs.ga.pfsspec.core import Physics
from pfs.ga.pfsspec.core.obsmod.resampling import Binning

from .pfsspectrumreader import PfsSpectrumReader
from ..pfsstellarspectrum import PfsStellarSpectrum

class PfsStellarSpectrumReader(PfsSpectrumReader):
    def __init__(self, wave_lim=None, orig=None):
        super().__init__(wave_lim=wave_lim, orig=orig)

    # TODO: implement the usual functions
    #       it's tricky because reading from pfsMerged files requires
    #       looking up information from the pfsConfig files

        
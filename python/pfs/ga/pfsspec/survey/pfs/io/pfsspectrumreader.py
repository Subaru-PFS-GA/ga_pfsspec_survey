import os
import sys
import numpy as np
from astropy.io import fits

from pfs.ga.pfsspec.core.io import SpectrumReader
from pfs.datamodel import PfsSingle, PfsObject, PfsArm

class PfsSpectrumReader(SpectrumReader):
    def __init__(self, wave_lim=None, orig=None):
        super().__init__(wave_lim=wave_lim, orig=orig)

        if not isinstance(orig, PfsSpectrumReader):
            pass
        else:
            pass

    def add_args(self, parser):
        super().add_args(parser)

    def init_from_args(self, args):
        super().init_from_args(args)

    def read(self):
        raise NotImplementedError()

    def read_all(self):
        return [self.read(),]
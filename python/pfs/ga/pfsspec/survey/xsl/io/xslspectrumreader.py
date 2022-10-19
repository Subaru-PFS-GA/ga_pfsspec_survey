import os
import sys
import numpy as np
import requests
from astropy.io import fits

from pfs.ga.pfsspec.core.io import SpectrumReader
from ..xslspectrum import XslSpectrum

class XslSpectrumReader(SpectrumReader):
    """
    Reads X-Shooter Stellar Library spectra
    """

    def __init__(self, orig=None):
        super().__init__(orig=orig)

        if isinstance(orig, XslSpectrumReader):
            self.path = orig.path
        else:
            self.path = None

    def create_spectrum(self, hdus):
        return XslSpectrum()

    def read(self, hdus):
        # FLUX: observed flux
        # FLUX_SC: slit corrected flux
        # FLUX_DR: dereddened flux

        spec = self.create_spectrum(hdus)
        spec.wave = hdus[1].data['WAVE']
        if 'FLUX_SC' in hdus[1].data.columns.names:
            spec.flux = hdus[1].data['FLUX_SC']
        else:
            spec.flux = hdus[1].data['FLUX']
        spec.flux_err = hdus[1].data['ERR']
        if 'FLUX_DR' in hdus[1].data.columns.names:
            spec.flux_dered = hdus[1].data['FLUX_DR']
        else:
            spec.flux_dered = None
        return spec

    def read_header(self, hdus, spec):
        spec.id = spec.xsl_id = hdus[0].header['XSL_ID']
        spec.ra = hdus[0].header['RA']
        spec.dec = hdus[0].header['DEC']
        spec.mjd = hdus[0].header['MJD-OBS']

    def load_spectrum(self, filename):
        filename = os.path.join(self.path, filename)

        with fits.open(filename, memmap=False) as hdus:
            spec = self.read(hdus)
            self.read_header(hdus, spec)
            return spec

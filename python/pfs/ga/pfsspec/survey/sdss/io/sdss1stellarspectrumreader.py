from pfs.ga.pfsspec.survey.sdss.io import Sdss1SpectrumReader
from pfs.ga.pfsspec.survey.sdss.segue import SdssSegueSpectrum

class Sdss1StellarSpectrumReader(Sdss1SpectrumReader):
    def __init__(self, orig=None):
        super(Sdss1StellarSpectrumReader, self).__init__(orig=orig)

        if isinstance(orig, Sdss1StellarSpectrumReader):
            pass
        else:
            pass

    def create_spectrum(self, hdus):
        return SdssSegueSpectrum()

    def read_header(self, hdus, row, spec):
        super(Sdss1StellarSpectrumReader, self).read_header(hdus, row, spec)

        spec.T_eff = row['T_eff']
        spec.Fe_H = row['Fe_H']
        spec.log_g = row['log_g']
        spec.a_Fe = row['a_Fe']
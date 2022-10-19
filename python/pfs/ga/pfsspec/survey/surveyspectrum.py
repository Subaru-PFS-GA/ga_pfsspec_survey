from pfs.ga.pfsspec.core import Spectrum

class SurveySpectrum():
    """
    Mixin that implements parameters for survey data.
    """

    def __init__(self, orig=None):
        if isinstance(orig, SurveySpectrum):
            self.ra = orig.ra
            self.dec = orig.dec
            self.mjd = orig.mjd
        else:
            self.ra = None
            self.dec = None
            self.mjd = None

    def get_param_names(self):
        params = ['ra',
                  'dec',
                  'mjd']
        return params


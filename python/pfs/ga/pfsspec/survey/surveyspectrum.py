from pfs.ga.pfsspec.core import Spectrum

class SurveySpectrum():
    """
    Mixin that implements parameters for survey data.
    """

    def __init__(self, orig=None):
        if not isinstance(orig, SurveySpectrum):
            self.ra = None
            self.dec = None
            self.mjd = None
            self.alt = None
            self.az = None
            self.airmass = None
        else:
            self.ra = orig.ra
            self.dec = orig.dec
            self.mjd = orig.mjd
            self.alt = None
            self.az = None
            self.airmass = orig.airmass

    def get_param_names(self):
        params = ['ra',
                  'dec',
                  'mjd',
                  'alt',
                  'az',
                  'airmass']
        return params


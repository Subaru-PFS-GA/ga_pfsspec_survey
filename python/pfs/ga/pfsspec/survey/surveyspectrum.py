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
            self.seeing = None
            self.obs_time = None
            self.exp_time = None
            self.exp_count = None
        else:
            self.ra = orig.ra
            self.dec = orig.dec
            self.mjd = orig.mjd
            self.alt = orig.alt
            self.az = orig.az
            self.airmass = orig.airmass
            self.seeing = orig.seeing
            self.obs_time = orig.obs_time
            self.exp_time = orig.exp_time
            self.exp_count = orig.exp_count

    def get_param_names(self):
        params = ['ra',
                  'dec',
                  'mjd',
                  'alt',
                  'az',
                  'airmass',
                  'seeing',
                  'obs_time',
                  'exp_time',
                  'exp_count']
        return params


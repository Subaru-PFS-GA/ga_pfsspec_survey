from ..surveyspectrum import SurveySpectrum

class SdssSpectrum(SurveySpectrum):
    """
    Mixin that implements additional parameters for SDSS survey data.
    """

    def __init__(self, orig=None):
        super(SdssSpectrum, self).__init__(orig=orig)

        if isinstance(orig, SdssSpectrum):
            self.plate = orig.plate
            self.fiber = orig.fiber
        else:
            self.plate = None
            self.fiber = None

    def get_param_names(self):
        params = ['plate',
                  'fiber']
        return params
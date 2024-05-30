from ..surveyspectrum import SurveySpectrum

class PfsSpectrum(SurveySpectrum):
    """
    Mixin that implements additional parameters for PSF survey data.
    """

    def __init__(self, orig=None):
        super().__init__(orig=orig)

        if not isinstance(orig, PfsSpectrum):
            self.catId = None
            self.objId = None
            self.visit = None

            self.spectrograph = None
            self.fiberId = None
        else:
            self.catId = orig.catId
            self.objId = orig.objId
            self.visit = orig.visit

            self.spectrograph = orig.spectrograph
            self.fiberId = orig.fiberId

    def get_param_names(self):
        params = ['catId',
                  'objId',
                  'visit',
                  'spectrograph',
                  'fiberId',]
        return params
    
    def get_name(self):
        return f'catId={self.catId:05d}, objID={self.objId:016x}, visit={self.visit:06d}'
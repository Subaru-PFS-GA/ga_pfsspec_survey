from ..surveyspectrum import SurveySpectrum

class PfsSpectrum(SurveySpectrum):
    """
    Mixin that implements additional parameters for PSF survey data.
    """

    def __init__(self, orig=None):
        super().__init__(orig=orig)

        if not isinstance(orig, PfsSpectrum):
            self.target = None
            self.identity = None
        else:
            self.target = orig.target
            self.identity = orig.identity

    def get_param_names(self):
        params = []
        return params
    
    def get_name(self):
        return f'catId={self.catId:05d}, objID={self.objId:016x}, visit={self.visit:06d}'
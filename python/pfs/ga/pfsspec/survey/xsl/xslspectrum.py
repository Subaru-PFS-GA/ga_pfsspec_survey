from pfs.ga.pfsspec.stellar import StellarSpectrum
from pfs.ga.pfsspec.survey.surveyspectrum import SurveySpectrum

class XslSpectrum(StellarSpectrum, SurveySpectrum):
    """
    X-shooter Stellar Library spectrum
    """

    def __init__(self, orig=None):
        StellarSpectrum.__init__(self, orig=orig)
        SurveySpectrum.__init__(self, orig=orig)

        if not isinstance(orig, XslSpectrum):
            self.xsl_id = None
            self.obj_name = None
        else:
            self.xsl_id = orig.xsl_id
            self.obj_name = orig.obj_name

    def get_param_names(self):
        params = super(StellarSpectrum, self).get_param_names()
        params = params + ['xsl_id',
                        'obj_name']
        return params

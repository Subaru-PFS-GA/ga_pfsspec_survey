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
        return f'catId={self.identity.catId:05d}, objID={self.identity.objId:016x}, visit={self.identity.visit:06d}'
    
    def get_mask_bits(self, mask_flags):
        mask_flags = set(mask_flags)
        mask_bits = 0
        for i in range(len(self.mask_flags)):
            if self.mask_flags[i] in mask_flags:
                mask_bits |= 1
                mask_bits <<= 1
        return mask_bits
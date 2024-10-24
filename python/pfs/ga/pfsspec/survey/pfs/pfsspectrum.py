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
        name_parts = []

        if hasattr(self, 'target') and self.target is not None:
            name_parts.append(f'catId={self.target.catId:05d}')
            name_parts.append(f'objId={self.target.objId:016x}')

        # TODO: add arm, if available: identity.arm or observations.arms
        if hasattr(self, 'identity') and self.identity is not None:
            name_parts.append(f'visit={self.identity.visit:06d}')

        if hasattr(self, 'observations') and len(self.observations) == 1:
            name_parts.append(f'arm={self.observations.arm[0]}')
            
        return ', '.join(name_parts)
    
    def get_mask_bits(self, mask_flags):
        mask_flags = set(mask_flags)
        max_bit = max(self.mask_flags.keys())
        
        mask_bits = 0
        for i in range(max_bit, -1, -1):
            mask_bits <<= 1
            if i in self.mask_flags and self.mask_flags[i] in mask_flags:
                mask_bits |= 1
            
        return mask_bits
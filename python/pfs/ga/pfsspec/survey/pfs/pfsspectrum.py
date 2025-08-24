from pfs.ga.pfsspec.core.util.copy import safe_deep_copy
from ..surveyspectrum import SurveySpectrum

class PfsSpectrum(SurveySpectrum):
    """
    Mixin that implements additional parameters for PSF survey data.
    """

    # PFS masks:

    # BAD: the pixel is a known bad pixel
    # SAT: the pixel was saturated
    # INTRP: the pixel has been interpolated
    # CR: the pixel is believed to be affected by a cosmic ray
    # EDGE: the pixel is close to the edge of the image (from LSST; not relevant for PFS)
    # DETECTED: the pixel has a positive value over threshold (from LSST; not relevant for PFS)
    # DETECTED_NEGATIVE: the pixel has a negative value over threshold (from LSST; not relevant for PFS)
    # SUSPECT: the pixel is suspected to be non-linear
    # NO_DATA: there are no good value for this value
    # UNMASKEDNAN: the pixel contained a NAN
    # BAD_FLAT: the pixel is bad in the flat
    # FIBERTRACE: the pixel is part of a fiber trace
    # BAD_SKY: the pixel is bad in the sky model
    # BAD_FLUXCAL: the pixel is bad in the flux calibration
    # OVERLAP: the pixel is part of a wavelength overlap (dichroic)

    def __init__(self, orig=None):
        super().__init__(orig=orig)

        if not isinstance(orig, PfsSpectrum):
            self.target = None
            self.identity = None
            self.catid = None
            self.spectrograph = None
            self.fiberid = None
            self.observations = None
        else:
            self.target = orig.target
            self.identity = orig.identity
            self.catid = orig.catid
            self.spectrograph = orig.spectrograph
            self.fiberid = orig.fiberid
            self.observations = safe_deep_copy(orig.observations)

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
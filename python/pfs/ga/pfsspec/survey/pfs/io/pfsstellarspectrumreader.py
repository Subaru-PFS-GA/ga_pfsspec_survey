import numpy as np

from pfs.ga.pfsspec.core import Physics
from pfs.ga.pfsspec.core.obsmod.resampling import Binning

from .pfsspectrumreader import PfsSpectrumReader
from ..pfsstellarspectrum import PfsStellarSpectrum

class PfsStellarSpectrumReader(PfsSpectrumReader):
    def __init__(self, wave_lim=None, orig=None):
        super().__init__(wave_lim=wave_lim, orig=orig)

    def read_from_pfsSingle(self, pfsSingle, index=-1, /,
                            arm=None, arm_limits=None, arm_mask=None,
                            ref_mag=None):
        """
        Create a PfsStellarSpectrum object from a PfsSingle object.

        PfsSingle object contain the spectrum in the fluxTable attribute, which
        lists all pixels of all arms. This method extracts the spectrum of a
        single arm with either `arm_limits` or `arm_mask` specified.

        Parameters
        ----------
        pfsSingle : PfsSingle
            The PfsSingle object.
        index : int
            A value to assign to the index attribute of the PfsStellarSpectrum object.
        arm : str
            The arm to extract the spectrum from.
        arm_limits : tuple
            The wavelength limits of the arm.
        arm_mask : array-like
            A mask defining the pixels of the arm.
        ref_mag : str
            Magnitude to be used as reference for the target.
        """

        # TODO: What if the arms overlap?

        # TODO: What if arm doesn't exist for a certain exposure? How to tell?
        #       Is metadata consistent with the fluxtable?

        s = PfsStellarSpectrum()
    
        # Extract header information
        s.index = index
        s.arm = arm
        s.catId = pfsSingle.target.catId
        s.objId = pfsSingle.target.objId
        s.tract = pfsSingle.target.tract
        s.patch = pfsSingle.target.patch
        s.visit = pfsSingle.observations.visit[0]
        s.spectrograph = pfsSingle.observations.spectrograph[0]
        s.fiberid = pfsSingle.observations.fiberId[0]
        
        # TODO: where do we take these from?
        # s.exp_count = 1
        # s.exp_time = 0
        # s.seeing = 0
        # s.obs_time

        # Get coordinates, observation time, airmass
        s.ra = pfsSingle.target.ra
        s.dec = pfsSingle.target.dec

        # Extract the spectrum
        wave = Physics.nm_to_angstrom(pfsSingle.fluxTable.wavelength)
        # nJy -> erg s-1 cm-2 A-1
        flux = 1e-32 * Physics.fnu_to_flam(wave, pfsSingle.fluxTable.flux)
        flux_err = 1e-32 * Physics.fnu_to_flam(wave, pfsSingle.fluxTable.error)
        mask = pfsSingle.fluxTable.mask

        # Apply the arm mask
        if arm_mask is None:
            if arm_limits is not None:
                arm_mask = (wave >= arm_limits[0]) & (wave <= arm_limits[1])
            else:
                arm_mask = ()

        if arm_mask.sum() == 0:
            # TODO write warning
            return None

        s.wave = wave[arm_mask]
        s.wave_edges = Binning.find_wave_edges(s.wave)
        s.flux = flux[arm_mask]
        s.flux_err = flux_err[arm_mask]
        s.mask = mask[arm_mask]

        # Make sure pixels with nan and inf are masked
        s.mask = np.where(np.isnan(s.flux) | np.isinf(s.flux) | np.isnan(s.flux_err) | np.isinf(s.flux_err),
                          s.mask | pfsSingle.flags['UNMASKEDNAN'],
                          s.mask)
        
        s.mask_flags = self.__get_mask_flags(pfsSingle)

        # Target PSF magnitude from metadata
        if ref_mag in pfsSingle.target.fiberFlux:
            # Convert nJy to ABmag
            flux = 1e-9 * pfsSingle.target.fiberFlux[ref_mag]
            mag = Physics.jy_to_abmag(flux)
            s.mag = mag
        else:
            s.mag = np.nan

        return s
        
    def __get_mask_flags(self, pfsSingle):
        # For now, ignore mask_flags and copy all flags
        return { v: k for k, v in pfsSingle.flags.flags.items() }
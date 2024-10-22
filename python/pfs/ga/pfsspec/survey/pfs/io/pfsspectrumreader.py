import os
import sys
import numpy as np
from types import SimpleNamespace

import astropy.units as u

from pfs.ga.pfsspec.core import Astro, Physics
from pfs.ga.pfsspec.core.obsmod.resampling import Binning
from pfs.ga.pfsspec.core.io import SpectrumReader

from ..datamodel import *

class PfsSpectrumReader(SpectrumReader):
    def __init__(self, wave_lim=None, orig=None):
        super().__init__(wave_lim=wave_lim, orig=orig)

        if not isinstance(orig, PfsSpectrumReader):
            pass
        else:
            pass

    def add_args(self, parser):
        super().add_args(parser)

    def init_from_args(self, args):
        super().init_from_args(args)

    def read(self):
        raise NotImplementedError()

    def read_all(self):
        return [self.read(),]
    
    def read_from_product(self, data, spec):
        
        if isinstance(data, PfsFiberArray):
            self.read_from_pfsFiberArray(data, spec)
        elif isinstance(data, PfsFiberArraySet):
            self.read_from_pfsFiberArraySet(data, spec)
        else:
            raise NotImplementedError()

        return spec
    
    def read_from_pfsFiberArray(self, data, spec, /,
                                wave_limits=None, wave_mask=None):
        """
        Read a spectrum from a PfsFiberArray object (PfsSingle, PfsObject or PfsGAObject).

        These objects contain the spectrum in the fluxTable attribute, which
        lists all pixels of all arms. This method extracts the spectrum of a
        single arm with either `arm_limits` or `arm_mask` specified.

        Parameters
        ----------
        data : PfsFiberArray
            The PfsFiberArray object.
        spec : Spectrum
            The Spectrum object to fill.
        arm_limits : tuple
            The wavelength limits of the arm.
        arm_mask : array-like
            A mask defining the pixels of the arm.
        """

        # TODO: What if the arms overlap?

        # TODO: What if arm doesn't exist for a certain exposure? How to tell?
        #       Is metadata consistent with the fluxtable?

        if data.nVisit != 1:
            raise NotImplementedError('Only one visit per spectrum is supported')
        
        # Get coordinates, observation time, airmass
        spec.id = data.target.objId
        spec.catid = data.target.catId

        spec.ra = data.target.ra
        spec.dec = data.target.dec

        spec.redshift = np.nan
        spec.redshift_err = np.nan

        spec.exp_count = 1              # TODO
        spec.exp_time = np.nan
        spec.seeing = np.nan
        spec.ext = np.nan
        
        spec.mjd = np.nan
        spec.airmass = np.nan

        spec.snr = np.nan
        spec.mag = np.nan

        spec.spectrograph = data.observations.spectrograph[0]
        spec.fiberid = data.observations.fiberId[0]

        # Extract Pfs header information
        spec.identity = SimpleNamespace(**data.target.identity)
        spec.observations = data.observations

        # Extract the spectrum

        # nm -> A
        wave = Physics.nm_to_angstrom(data.fluxTable.wavelength)
        # nJy -> erg s-1 cm-2 A-1
        flux = 1e-32 * Physics.fnu_to_flam(wave, data.fluxTable.flux)
        flux_err = 1e-32 * Physics.fnu_to_flam(wave, data.fluxTable.error)

        # TODO: covariances?

        # Apply the arm mask
        if wave_mask is None:
            if wave_limits is not None:
                wave_mask = (wave >= wave_limits[0]) & (wave <= wave_limits[1])
            else:
                wave_mask = ()

        if wave_mask.sum() == 0:
            # TODO write warning
            return None

        spec.wave = wave[wave_mask]
        spec.wave_edges = Binning.find_wave_edges(spec.wave)
        spec.flux = flux[wave_mask]
        spec.flux_err = flux_err[wave_mask]
        spec.mask = data.fluxTable.mask[wave_mask]

        # Make sure pixels with nan and inf are masked
        spec.mask = np.where(np.isnan(spec.flux) | np.isinf(spec.flux) | np.isnan(spec.flux_err) | np.isinf(spec.flux_err),
                             spec.mask | data.flags['UNMASKEDNAN'],
                             spec.mask)
        
        spec.mask_bits = 0
        spec.mask_flags = self.__get_mask_flags(data)

        spec.resolution = np.round(np.median(0.5 * (spec.wave[1:] + spec.wave[:-1]) / np.diff(spec.wave)), -3)
        spec.is_wave_regular = False
        spec.is_wave_lin = False
        spec.is_wave_log = False

        filename = data.filenameFormat % dict(**data.target.identity, visit=data.observations.visit[0])
        spec.history.append(f'Loaded from PfsFiberArraySet `{filename}`.')
    
    def read_from_pfsDesign(self, data: PfsDesign, spec, index=None, fiberid=None):
        """
        Read the spectrum header from a PfsDesign or PfsConfig object. This information is
        not available in the PfsFiberArraySet objects.
        """
        
        if index is None:
            index = np.where(data.fiberId == fiberid)[0][0]
        elif fiberid is None:
            fiberid = data.fiberId[index]

        spec.id = data.objId[index]
        spec.catid = data.catId[index]

        spec.ra = data.ra[index]
        spec.dec = data.dec[index]

        spec.redshift = np.nan
        spec.redshift_err = np.nan

        spec.exp_count = 1              # TODO
        spec.exp_time = np.nan
        spec.seeing = np.nan
        spec.ext = np.nan
        
        spec.mjd = np.nan
        spec.airmass = np.nan

        spec.snr = np.nan
        spec.mag = np.nan

        spec.spectrograph = data.spectrograph[fiberid]
        spec.fiberid = data.fiberId[index]

        # Extract Pfs header information
        spec.identity = SimpleNamespace(
            catId = data.catId[index],
            objId = data.objId[index],
            tract = data.tract[index],
            patch = data.patch[index],
        )

        spec.observations = SimpleNamespace(
            visit = data.visit,
            arm = data.arms,
            spectrograph = data.spectrograph[fiberid],
            pfsDesignId = data.pfsDesignId,
            fiberId = data.fiberId[index],
            pfiNominal = data.pfiNominal[index],
            pfiCenter = data.pfiCenter[index],
            obsTime = None,
            expTime = np.nan,
            num = 1
        )

        filename = data.fileNameFormat % (data.pfsDesignId, data.visit)
        spec.history.append(f'Loaded from PfsFiberArraySet `{filename}`, index={index}.')
    
    def read_from_pfsFiberArraySet(self, data, spec, fiberid=None, index=None,
                                   wave_limits=None, wave_mask=None):
    
        if index is None:
            index = np.where(data.fiberId == fiberid)[0][0]
        elif fiberid is None:
            fiberid = data.fiberId[index]
        
        # Extract the spectrum

        # nm -> A
        wave = Physics.nm_to_angstrom(data.wavelength[index])
        # nJy -> erg s-1 cm-2 A-1
        flux = data.flux[index]
        flux_err = np.sqrt(data.variance[index])
        flux_sky = data.sky[index]

        mask = data.mask[index]
        
        # TODO: covariances? norm?
        # data.covar - (nfiber, 3, nwave) flux covariance band matrix, still all nan
        # data.norm - normalization factor for each spectrum - can we use it for anything?

        # Apply the arm mask
        if wave_mask is None:
            if wave_limits is not None:
                wave_mask = (wave >= wave_limits[0]) & (wave <= wave_limits[1])
            else:
                wave_mask = ()

        if wave_mask.sum() == 0:
            # TODO write warning
            return None

        spec.wave = wave[wave_mask]
        spec.wave_edges = Binning.find_wave_edges(spec.wave)
        spec.flux = flux[wave_mask]
        spec.flux_err = flux_err[wave_mask]
        spec.flux_sky = flux_sky[wave_mask]
        spec.mask = mask[wave_mask]

        # Make sure pixels with nan and inf are masked
        spec.mask = np.where(np.isnan(spec.flux) | np.isinf(spec.flux) | np.isnan(spec.flux_err) | np.isinf(spec.flux_err),
                             spec.mask | data.flags['UNMASKEDNAN'],
                             spec.mask)
        
        spec.mask_bits = 0
        spec.mask_flags = self.__get_mask_flags(data)

        spec.resolution = np.round(np.median(0.5 * (spec.wave[1:] + spec.wave[:-1]) / np.diff(spec.wave)), -3)
        spec.is_wave_regular = False
        spec.is_wave_lin = False
        spec.is_wave_log = False

        filename = data.getFilename(data.identity)
        spec.history.append(f'Loaded from PfsFiberArraySet `{filename}`, index={index}.')
        
    def __get_mask_flags(self, pfsSingle):
        # For now, ignore mask_flags and copy all flags
        return { v: k for k, v in pfsSingle.flags.flags.items() }
import os
import sys
import numpy as np
from datetime import datetime
import pytz
from types import SimpleNamespace

import astropy.units as u

from pfs.ga.pfsspec.core import Astro, Physics
from pfs.ga.pfsspec.core.obsmod.resampling import Binning
from pfs.ga.pfsspec.core.io import SpectrumReader

from ..datamodel import *
from ..utils import *

from ..setup_logger import logger

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

    def is_available(self, data, arm=None, objid=None, fiberid=None, index=None):
        """
        Verify if the requested arm is available, at least according to the metadata.
        """

        def get_type_string():
            return f'{type(data).__name__}'

        def get_id_string():
            id = ''

            if isinstance(data, PfsFiberArray):
                raise NotImplementedError()
            
            if isinstance(data, PfsFiberArraySet):
                raise NotImplementedError()
            
            if isinstance(data, PfsDesign):
                id = f'pfsDesignId={data.pfsDesignId:016x}, '

            if isinstance(data, PfsConfig):
                id += f'visit={data.visit:06d}, '
            
            if objid is not None:
                id += f'objId={objid:016x}, '

            if fiberid is not None:
                id += f'fiberId={fiberid:03d}, '

            return id

        if isinstance(data, PfsFiberArray):                         # pfsSingle
            raise NotImplementedError()
        elif isinstance(data, PfsFiberArraySet):                    # PfsMerged
            if arm is not None and arm not in data.identity.arm:
                logger.warning(f'Arm {arm} not available in {get_type_string()} object.')
                return False

            if fiberid is not None and fiberid not in data.fiberId:
                logger.warning(f'Fiber {fiberid} not available in {get_type_string()} object.')
                return False
            
            if index is not None and index >= len(data.fiberId):
                logger.warning(f'Index {index} out of range in {get_type_string()} object.')
                return False
        elif isinstance(data, PfsDesign):
            if arm is not None and arm not in data.arms:
                logger.warning(f'Arm {arm} not available in {get_type_string()} object with {get_id_string()}.')
                return False

            if objid is not None and objid not in data.objId:
                logger.warning(f'Object {objid} not available in {get_type_string()} object with {get_id_string()}.')
                return False

            if fiberid is not None and fiberid not in data.fiberId:
                logger.warning(f'Fiber {fiberid} not available in {get_type_string()} object with {get_id_string()}.')
                return False
            
            if index is not None and index >= len(data.fiberId):
                logger.warning(f'Index {index} out of range in {get_type_string()} object with {get_id_string()}.')
                return False
        else:
            raise NotImplementedError()
        
        return True

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
    
    def read_from_pfsFiberArray(self, data, spec, arm=None,
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

        spec.target = data.target
        spec.observations = data.observations

        # Override arm if reading a single-arm spectrum
        if arm is not None:
            spec.observations.arm = [ arm for a in data.observations.arm ]

        if len(data.observations) == 1:
            spec.identity = Identity(
                visit = data.observations.visit[0],
                arm = arm if arm is not None else data.observations.arm[0],
                spectrograph = data.observations.spectrograph[0],
                pfsDesignId = data.observations.pfsDesignId[0],
                obsTime = data.observations.obsTime[0],
                expTime = data.observations.expTime[0],
            )
        else:
            logger.warning(f'Multiple observations in PfsFiberArray object for spectrum {spec.get_name()}, cannot generate a single identity.')
            spec.identity = None

        # Extract the spectrum

        # nm -> A
        wave = Physics.nm_to_angstrom(data.fluxTable.wavelength)

        # nJy -> erg s-1 cm-2 A-1
        flux = 1e-32 * Physics.fnu_to_flam(wave, data.fluxTable.flux)
        flux_err = 1e-32 * Physics.fnu_to_flam(wave, data.fluxTable.error)
        flux_sky = None
        mask = data.fluxTable.mask

        # TODO: covariances?

        # TODO: Check class type here if necessary. PfsSingle and PfsObject are both flux-calibrated.
        spec.is_flux_calibrated = True

        spec.mask_bits = 0
        spec.mask_flags = self.__get_mask_flags(data)

        self.__set_data_vectors(spec, wave, flux, flux_err, flux_sky,
                                mask, data.flags['UNMASKEDNAN'],
                                wave_mask, wave_limits)

        filename = data.filenameFormat % dict(**data.target.identity, visit=data.observations.visit[0])
        spec.history.append(f'Loaded from PfsFiberArraySet `{filename}`.')
    
    def read_from_pfsDesign(self, data: PfsDesign, spec, arm=None, objid=None, fiberid=None, index=None):
        """
        Read the spectrum header from a PfsDesign or PfsConfig object. This information is
        not available in the PfsFiberArraySet objects.
        """
        
        if index is None:
            if fiberid is not None:
                index = np.where(data.fiberId == fiberid)[0][0]
            elif objid is not None:
                index = np.where(data.objId == objid)[0][0]
            else:
                raise ValueError('Either fiberId or objId must be specified if index is None.')

        if fiberid is None:
            fiberid = data.fiberId[index]

        if objid is None:
            objid = data.objId[index]

        spec.id = objid
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

        spec.target = Target(
            catId = data.catId[index],
            tract = data.tract[index],
            patch = data.patch[index],
            objId = data.objId[index],
            ra = data.ra[index],
            dec = data.dec[index],
            targetType = data.targetType[index],
        )

        spec.observations = Observations(
            visit = np.atleast_1d(data.visit),
            arm = np.atleast_1d(arm if arm is not None else data.arms),
            spectrograph = np.atleast_1d(data.spectrograph[fiberid]),
            pfsDesignId = np.atleast_1d(data.pfsDesignId),
            fiberId = np.atleast_1d(data.fiberId[index]),
            pfiNominal = np.atleast_2d(data.pfiNominal[index]),
            pfiCenter = np.atleast_2d(data.pfiCenter[index]),
            obsTime = np.atleast_1d(Identity.defaultObsTime),
            expTime = np.atleast_1d(Identity.defaultExpTime),
        )

        # Extract Pfs header information, this is different what the
        # data model uses for the identity, we collect all fields here that
        # are necessary to uniquely identify the spectrum
        identity = Identity(
            visit = data.visit,
            arm = arm if arm is not None else data.arms,
            spectrograph = data.spectrograph[fiberid],
            pfsDesignId = data.pfsDesignId,
            obsTime = Identity.defaultObsTime,
            expTime = Identity.defaultExpTime
        )
        
        if spec.identity is None:
            spec.identity = identity
        else:
            spec.identity = merge_identity(spec.identity, identity, arm=arm)
            

        filename = data.fileNameFormat % (data.pfsDesignId, data.visit)
        spec.history.append(f'Loaded from PfsFiberArraySet `{filename}`, index={index}.')
    
    def read_from_pfsFiberArraySet(self, data, spec, arm=None,
                                   fiberid=None, index=None,
                                   wave_limits=None, wave_mask=None):
    
        if index is None:
            if fiberid is not None:
                index = np.where(data.fiberId == fiberid)[0][0]
            else:
                raise ValueError('Either fiberId or objId must be specified if index is None.')
        
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

        # TODO: Check class type here if necessary. PfsMerged and PfsArm are both uncalibrated
        spec.is_flux_calibrated = False
       
        spec.mask_bits = 0
        spec.mask_flags = self.__get_mask_flags(data)

        self.__set_data_vectors(spec, wave, flux, flux_err, flux_sky,
                        mask, data.flags['UNMASKEDNAN'],
                        wave_mask, wave_limits)
        
        if spec.identity is None:
            spec.identity = data.identity
        else:
            spec.identity = merge_identity(spec.identity, data.identity, arm=arm)

        filename = data.getFilename(data.identity)
        spec.history.append(f'Loaded from PfsFiberArraySet `{filename}`, index={index}.')

    def __set_data_vectors(self, spec,
                           wave, flux, flux_err, flux_sky,
                           mask, unmasked_nan_flag,
                           wave_mask, wave_limits):
        
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
        self.flux_sky = flux_sky[wave_mask] if flux_sky is not None else None
        spec.mask = mask[wave_mask]

        # Make sure pixels with nan and inf are masked
        spec.mask = np.where(np.isnan(spec.flux) | np.isinf(spec.flux) | np.isnan(spec.flux_err) | np.isinf(spec.flux_err),
                             spec.mask | unmasked_nan_flag,
                             spec.mask)

        spec.resolution = np.round(np.median(0.5 * (spec.wave[1:] + spec.wave[:-1]) / np.diff(spec.wave)), -3)
        spec.is_wave_regular = False
        spec.is_wave_lin = False
        spec.is_wave_log = False
        
    def __get_mask_flags(self, pfsSingle):
        # Get the dictionary from the PFS data model object because we need to be
        # compatible with the rest of the GA spectrum library
        return { v: k for k, v in pfsSingle.flags.flags.items() }
    
    def __calculate_params(self, spec):
        # TODO: read MJD from somewhere
        # Convert datetime to MJD using astropy
        # Create datetime with UTC time zone (Hawaii: UTC - 10)
        spec.mjd = Astro.datetime_to_mjd(datetime(2023, 7, 24, 14, 0, 0, tzinfo=pytz.timezone('UTC')))
        spec.alt, spec.az = Astro.radec_to_altaz(spec.ra, spec.dec, spec.mjd)
        spec.airmass = 1 / np.cos(np.radians(90 - spec.alt))
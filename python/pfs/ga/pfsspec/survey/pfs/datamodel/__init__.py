from ..setup_logger import logger

# Imports from pfs.datamodel

try:
    from pfs.datamodel import PfsFiberArray, PfsFiberArraySet, PfsSingle, PfsObject, PfsArm, PfsMerged, PfsCoadd
    from pfs.datamodel.pfsTargetSpectra import PfsTargetSpectra
    from pfs.datamodel import PfsConfig, PfsDesign
    from pfs.datamodel import PfsStar, PfsStarCatalog
    from pfs.datamodel import Target, Identity, Observations
    from pfs.datamodel import TargetType, FiberStatus, MaskHelper
    from pfs.datamodel.utils import calculatePfsVisitHash, calculate_pfsDesignId
    from .pfscalibrated import PfsCalibrated
    from .pfscalibratedlsf import PfsCalibratedLsf
except ImportError as ex:
    logger.warning('Cannot import PFS data model. Is package `pfs.datamodel` available?')
    logger.exception(ex)

    PfsFiberArray = object()
    PfsFiberArraySet = object()
    PfsSingle = object()
    PfsObject = object()
    PfsArm = object()
    PfsMerged = object()
    PfsCalibrated = object()
    PfsCalibratedLsf = object()
    PfsCoadd = object()
    PfsTargetSpectra = object()
    PfsConfig = object()
    PfsDesign = object()
    PfsStar = object()
    PfsStarCatalog = object()
    Target = object()
    Identity = object()
    Observations = object()
    TargetType = object()
    FiberStatus = object()
    MaskHelper = object()
    calculatePfsVisitHash = object()
    calculate_pfsDesignId = object()

# Optional imports from pfs.drp.stella

try:
    from pfs.drp.stella import DetectorMap
except ImportError as ex:
    logger.warning('Cannot import DetectorMap from pfs.drp.stella. Is package `pfs.drp.stella` available?')
    logger.exception(ex)

    class DetectorMap:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError('DetectorMap is not available because pfs.drp.stella is not installed.')
from ..setup_logger import logger

try:
    from pfs.datamodel import PfsFiberArray, PfsFiberArraySet, PfsSingle, PfsObject, PfsArm, PfsMerged, PfsCalibrated, PfsCoadd
    from pfs.datamodel import PfsConfig, PfsDesign
    from pfs.datamodel import PfsGAObject
    from pfs.datamodel import Target, Identity, Observations
    from pfs.datamodel import TargetType, MaskHelper
    from pfs.datamodel.utils import calculatePfsVisitHash, calculate_pfsDesignId
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
    PfsCoadd = object()
    PfsConfig = object()
    PfsDesign = object()
    PfsGAObject = object()
    Target = object()
    Identity = object()
    Observations = object()
    TargetType = object()
    MaskHelper = object()
    calculatePfsVisitHash = object()
    calculate_pfsDesignId = object()
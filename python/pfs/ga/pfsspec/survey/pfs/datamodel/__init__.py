try:
    from pfs.datamodel import PfsFiberArray, PfsFiberArraySet, PfsSingle, PfsObject, PfsArm, PfsMerged
    from pfs.datamodel import PfsConfig, PfsDesign
    from pfs.datamodel import PfsGAObject
    from pfs.datamodel import Target, Identity, Observations
    from pfs.datamodel import MaskHelper
    from pfs.datamodel.utils import calculatePfsVisitHash, calculate_pfsDesignId
except ImportError:
    PfsFiberArray = object()
    PfsFiberArraySet = object()
    PfsSingle = object()
    PfsObject = object()
    PfsArm = object()
    PfsMerged = object()
    PfsConfig = object()
    PfsDesign = object()
    PfsGAObject = object()
    Target = object()
    Identity = object()
    Observations = object()
    MaskHelper = object()
    calculatePfsVisitHash = object()
    calculate_pfsDesignId = object()
try:
    from pfs.datamodel import PfsFiberArray, PfsFiberArraySet, PfsSingle, PfsObject, PfsArm, PfsMerged
    from pfs.datamodel import PfsConfig, PfsDesign
    from pfs.datamodel import PfsGAObject
    from pfs.datamodel import Target, Identity, Observations
except ImportError:
    PfsFiberArray = None
    PfsFiberArraySet = None
    PfsSingle = None
    PfsObject = None
    PfsArm = None
    PfsMerged = None
    PfsConfig = None
    PfsDesign = None
    PfsGAObject = None
    Target = None
    Identity = None
    Observations = None
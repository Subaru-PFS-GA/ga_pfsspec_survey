try:
    from pfs.datamodel import PfsFiberArray, PfsFiberArraySet, PfsSingle, PfsObject, PfsArm, PfsMerged
    from pfs.datamodel import PfsConfig, PfsDesign
except ImportError:
    PfsFiberArray = None
    PfsFiberArraySet = None
    PfsSingle = None
    PfsObject = None
    PfsArm = None
    PfsMerged = None
    PfsConfig = None
    PfsDesign = None
from types import SimpleNamespace

from ..setup_logger import logger

try:
    from pfs.datamodel import PfsCalibrated as PfsCalibratedBase
except ImportError as ex:
    logger.warning('Cannot import PFS data model. Is package `pfs.datamodel` available?')
    logger.exception(ex)

    PfsCalibratedBase = None

class PfsCalibrated(PfsCalibratedBase):
    """
    A collection of PfsSingle (calibrated spectra) indexed by target
    """

    def extract(self):
        # TODO: what if the container has different types of spectra?
        pfsSingle = []
        ids = []
        for k, s in self._byObjId.items():
            id = SimpleNamespace(
                catId = s.target.identity['catId'],
                tract = s.target.identity['tract'],
                patch = s.target.identity['patch'],
                objId = s.target.identity['objId'],
                visit = s.observations.visit[0],
                fiberId = s.observations.fiberId[0],
                targetType = s.target.targetType,
                # proposalId = s.target.proposalId,
                # obCode = s.target.obCode,
            )
            pfsSingle.append(s)
            ids.append(id)
        
        return pfsSingle, ids
        
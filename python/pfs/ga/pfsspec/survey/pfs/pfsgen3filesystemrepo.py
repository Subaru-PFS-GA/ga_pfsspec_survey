import numpy as np
from types import SimpleNamespace

from ..repo import *
from .pfsgen3filesystemconfig import PfsGen3FileSystemConfig
from .datamodel import *

class PfsGen3FileSystemRepo(FileSystemRepo):
    """
    Implements PFS specific function to discover data products
    stored in the file system without Butler.
    """

    def __init__(self):
        super().__init__(config=PfsGen3FileSystemConfig)

    def find_object(self, **kwargs):
        
        """
        Find individual objects by looking them up in the config files.
        """

        params = SimpleNamespace(
            visit = IntFilter(name='visit', format='{:06d}'),
            date = DateFilter(name='date', format='{:%Y%m%d}'),
            fiberId = IntFilter(name='fiberId'),
            catId = IntFilter(name='catId'),
            proposalId = StringFilter(name='proposalId'),
            objId = HexFilter(name='objId', format='{:016x}'),
            obCode = StringFilter(name='objCode'),
            targetType = IntFilter(name='targetType'),
        )

        # Update the parameters with the values
        for k, v in kwargs.items():
            if hasattr(params, k) and v is not None:
                getattr(params, k).values = v

        # Load the config files for each visit
        files, ids = self.find_product(PfsConfig, visit=params.visit, date=params.date)

        configs = {}
        for file in files:
            config, id, fn = self.load_product(PfsConfig, filename=file)
            configs[id.visit] = config

        identities = {}
        for visit, config in configs.items():
            # Find objects matching the criteria
            mask = np.full(config.fiberId.shape, True)

            mask &= params.fiberId.mask(config.fiberId)
            mask &= params.catId.mask(config.catId)
            mask &= params.objId.mask(config.objId)
            mask &= params.targetType.mask(config.targetType)
            mask &= params.proposalId.mask(config.proposalId)
            mask &= params.obCode.mask(config.obCode)

            n = mask.sum()
            if n > 0:
                identities[visit] = SimpleNamespace(
                    visit = n * [visit],
                    pfsDesignId = n * [config.pfsDesignId],
                    fiberId = list(config.fiberId[mask]),
                    proposalId = list(config.proposalId[mask]),
                    catId = list(config.catId[mask]),
                    objId = list(config.objId[mask]),
                    targetType = list(config.targetType[mask]),
                    obCode = list(config.obCode[mask]),
                )

        return identities

        
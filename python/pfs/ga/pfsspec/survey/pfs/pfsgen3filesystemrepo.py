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

        self.__object_filters = SimpleNamespace(
            # visit = IntFilter(name='visit', format='{:06d}'),
            # date = DateFilter(name='date', format='{:%Y%m%d}'),
            fiberId = IntFilter(name='fiberId'),
            # catId = IntFilter(name='catId'),
            proposalId = StringFilter(name='proposalId'),
            # objId = HexFilter(name='objId', format='{:016x}'),
            obCode = StringFilter(name='objCode'),
            targetType = EnumFilter(name='targetType', enum_type=TargetType),
        )

    #region Properties

    def __get_object_filters(self):
        return self.__object_filters
    
    object_filters = property(__get_object_filters)

    #endregion

    def add_args(self, script, include_variables=True, include_filters=True):
        super().add_args(script, include_variables=include_variables, include_filters=include_filters)

        for k, p in self.__object_filters.__dict__.items():
            script.add_arg(f'--{k.lower()}', type=str, nargs='*', help=f'Filter on {k}')
        
    def init_from_args(self, script):
        super().init_from_args(script)

        for k, p in self.__object_filters.__dict__.items():
            if script.is_arg(k.lower()):
                p.parse(script.get_arg(k.lower()))

    def find_object(self, groupby='visit', **kwargs):
        
        """
        Find individual objects by looking them up in the config files.
        """

        # Update the parameters with the values
        for k, v in kwargs.items():
            if hasattr(self.filters, k) and v is not None:
                getattr(self.filters, k).values = v
            if hasattr(self.__object_filters, k) and v is not None:
                getattr(self.__object_filters, k).values = v

        # Load the config files for each visit
        files, ids = self.find_product(PfsConfig, visit=self.filters.visit, date=self.filters.date)

        configs = {}
        for file in files:
            config, id, fn = self.load_product(PfsConfig, filename=file)
            configs[id.visit] = config

        identities = {}
        for visit, config in configs.items():
            # Find objects matching the criteria
            mask = np.full(config.fiberId.shape, True)

            mask &= self.__object_filters.fiberId.mask(config.fiberId)
            mask &= self.filters.catId.mask(config.catId)
            mask &= self.filters.objId.mask(config.objId)
            mask &= self.__object_filters.targetType.mask(config.targetType)
            mask &= self.__object_filters.proposalId.mask(config.proposalId)
            mask &= self.__object_filters.obCode.mask(config.obCode)

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

        if groupby == 'visit':
            return identities
        elif groupby == 'objid':
            raise NotImplementedError()
        elif groupby == 'none':
            # Concatenate everything into a single namespace
            results = None
            for v, ids in identities.items():
                if results is None:
                    results = ids
                else:
                    for k, v in ids.__dict__.items():
                        getattr(results, k).extend(v)
            return results
        else:
            raise NotImplementedError()

        
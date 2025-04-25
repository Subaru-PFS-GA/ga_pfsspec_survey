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

    def __init__(self, config=PfsGen3FileSystemConfig):
        super().__init__(config=config)

        self.__object_filters = SimpleNamespace(
            # visit = IntFilter(name='visit', format='{:06d}'),
            # date = DateFilter(name='date', format='{:%Y%m%d}'),
            fiberId = IntFilter(name='fiberId'),
            # catId = IntFilter(name='catId'),
            proposalId = StringFilter(name='proposalId'),
            # objId = HexFilter(name='objId', format='{:016x}'),
            obCode = StringFilter(name='obCode'),
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

    def filters_match_object(self, identity, **kwargs):
        """
        Match an identity against the filters.
        """

        # Update the parameters with the values
        # TODO: this actually destroys the original class-level values
        #       consider making copies
        for k, v in kwargs.items():
            if hasattr(self.filters, k) and v is not None:
                getattr(self.filters, k).values = v
            if hasattr(self.__object_filters, k) and v is not None:
                getattr(self.__object_filters, k).values = v

        # Check if the identity matches the filters
        match = not hasattr(identity, 'fiberId') or self.__object_filters.fiberId.mask(identity.fiberId)
        match &= not hasattr(identity, 'catId') or self.filters.catId.mask(identity.catId)
        match &= not hasattr(identity, 'objId') or self.filters.objId.mask(identity.objId)
        match &= not hasattr(identity, 'targetType') or self.__object_filters.targetType.mask(identity.targetType)
        match &= not hasattr(identity, 'proposalId') or self.__object_filters.proposalId.mask(identity.proposalId)
        match &= not hasattr(identity, 'obCode') or self.__object_filters.obCode.mask(identity.obCode)

        return match

    def find_objects(self, product=PfsConfig, configs=None, groupby='visit', **kwargs):
        
        """
        Find individual objects by looking them up in the config files.
        """

        # Update the parameters with the values
        # TODO: this actually destroys the original class-level values
        #       consider making copies
        for k, v in kwargs.items():
            if hasattr(self.filters, k) and v is not None:
                getattr(self.filters, k).values = v
            if hasattr(self.__object_filters, k) and v is not None:
                getattr(self.__object_filters, k).values = v

        # We either look up objects in PfsConfig files or look for the available PfsSingle files
        if product == PfsConfig:
            # If not provided, load the config files for each visit
            if configs is None:
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
                        obstime = n * [config.obstime],
                        exptime = n * [None],
                        fiberId = list(config.fiberId[mask]),
                        spectrograph = list(config.spectrograph[mask]),
                        arms = n * [config.arms],
                        fiberStatus = list(config.fiberStatus[mask]),
                        proposalId = list(config.proposalId[mask]),
                        catId = list(config.catId[mask]),
                        objId = list(config.objId[mask]),
                        tract = list(config.tract[mask]),
                        patch = list(config.patch[mask]),
                        targetType = list(config.targetType[mask]),
                        obCode = list(config.obCode[mask]),
                    )
        elif product == PfsSingle:
            raise NotImplementedError()

        if groupby == 'visit':
            return self.__group_objects_by_visit(identities)
        elif groupby == 'objid':
            return self.__group_objects_by_objid(identities)
        elif groupby == 'none':
            return self.__group_objects_by_none(identities)
        else:
            raise NotImplementedError()

    def __group_objects_by_visit(self, identities):
        return identities

    def __group_objects_by_objid(self, identities):
        results = {}
        for visit, ids in identities.items():
            for i in range(len(ids.fiberId)):
                objid = ids.objId[i]

                # Exclude engineering fibers
                if objid != -1:
                    id = SimpleNamespace(
                        visit = [ visit ],
                        pfsDesignId = [ids.pfsDesignId[i]],
                        obstime = [ids.obstime[i]],
                        exptime = [ids.exptime[i]],
                        fiberId = [ids.fiberId[i]],
                        spectrograph = [ids.spectrograph[i]],
                        arms = [ids.arms[i]],
                        fiberStatus = [ids.fiberStatus[i]],
                        proposalId = [ids.proposalId[i]],
                        catId = [ids.catId[i]],
                        objId = [ids.objId[i]],
                        tract = [ids.tract[i]],
                        patch = [ids.patch[i]],
                        targetType = [ids.targetType[i]],
                        obCode = [ids.obCode[i]],
                    )

                    if objid not in results:
                        results[objid] = id
                    else:
                        # Merge lists
                        r = results[objid]
                        for k, v in id.__dict__.items():
                            getattr(r, k).extend(v)

        return results
    
    def __group_objects_by_none(self, identities):
        # Concatenate everything into a single namespace
        results = None
        for v, ids in identities.items():
            if results is None:
                results = ids
            else:
                for k, v in ids.__dict__.items():
                    getattr(results, k).extend(v)
        return results

    
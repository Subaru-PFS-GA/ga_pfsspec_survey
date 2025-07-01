import re
from types import SimpleNamespace
from copy import deepcopy
import numpy as np

from ..repo import *
from .pfsgen3filesystemconfig import PfsGen3FileSystemConfig
from .datamodel import *

class PfsGen3Repo():
    """
    Wraps a data repository object to implement a PFS specific
    interface for accessing data products.
    """

    def __init__(self, repo_type=ButlerRepo, config=PfsGen3FileSystemConfig):
        # Initizalize the repository
        self.__repo = self.__init_repo(repo_type, config)
        self.__object_filters = self.__init_object_filters()

    def __init_repo(self, repo_type, config):
        return repo_type(config)

    def __getattr__(self, name):
        """
        Forwards attribute access to the wrapped object. This will allow
        calling methods and accessing properties of the wrapped repository.

        This function is only called for attributes that are not defined
        in this class, so it will not interfere with the properties defined
        in the wrapper.
        """

        return getattr(self.__repo, name)
        
    #region Properties

    def __get_repo(self):
        return self.__repo
    
    repo = property(__get_repo)

    def __get_object_filters(self):
        return self.__object_filters
    
    object_filters = property(__get_object_filters)

    def __get_ignore_missing_files(self):
        return self.__repo.ignore_missing_files
    
    def __set_ignore_missing_files(self, value):
        self.__repo.ignore_missing_files = value

    ignore_missing_files = property(__get_ignore_missing_files, __set_ignore_missing_files)

    #endregion

    def add_args(self,
                 script,
                 include_variables=True,
                 include_filters=True,
                 ignore_duplicates=False):
        
        self.__repo.add_args(script,
                             include_variables=include_variables,
                             include_filters=include_filters,
                             ignore_duplicates=ignore_duplicates)

        for k, p in self.__object_filters.__dict__.items():
            script.add_arg(f'--{k.lower()}',
                           type=str,
                           nargs='*',
                           help=f'Filter on {k}',
                           ignore_duplicate=ignore_duplicates)
        
    def init_from_args(self, script):
        self.__repo.init_from_args(script)

        for k, p in self.__object_filters.__dict__.items():
            if script.is_arg(k.lower()):
                p.parse(script.get_arg(k.lower()))

    def __init_object_filters(self):
        # Instantiate target object search filters
        # TODO: extend these if Butler has support for more filters
        # NOTE: filters commented out are handled by the wrapped class
        object_filters = SimpleNamespace(
            visit = IntFilter(name='visit', format='{:06d}'),
            date = DateFilter(name='date', format='{:%Y%m%d}'),
            fiberId = IntFilter(name='fiberId'),
            catId = IntFilter(name='catId'),
            proposalId = StringFilter(name='proposalId'),
            objId = HexFilter(name='objId', format='{:016x}'),
            obCode = StringFilter(name='obCode'),
            targetType = EnumFilter(name='targetType', enum_type=TargetType),
        )

        return object_filters

    def match_object_filters(self, identity, **kwargs):
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
        match &= not hasattr(identity, 'catId') or self.__object_filters.catId.mask(identity.catId)
        match &= not hasattr(identity, 'objId') or self.__object_filters.objId.mask(identity.objId)
        match &= not hasattr(identity, 'targetType') or self.__object_filters.targetType.mask(identity.targetType)
        match &= not hasattr(identity, 'proposalId') or self.__object_filters.proposalId.mask(identity.proposalId)
        match &= not hasattr(identity, 'obCode') or self.__object_filters.obCode.mask(identity.obCode)

        return match

    def match_container_product_type(self, filename):
        # Try to match each product regex pattern against the filename
        for product, config in self.repo.config.products.items():
            if isinstance(product, tuple):
                for regex in config.params_regex:
                    if re.search(regex, filename):
                        return product

    #region Wrapper functions

    def parse_product_type(self, *args, **kwargs):
        return self.__repo.parse_product_type(*args, **kwargs)

    def parse_product_identity(self, *args, **kwargs):
        return self.__repo.parse_product_identity(*args, **kwargs)

    def find_product(self, *args, **kwargs):
        return self.__repo.find_product(*args, **kwargs)

    def locate_product(self, *args, **kwargs):
        return self.__repo.locate_product(*args, **kwargs)

    def load_product(self, *args, **kwargs):
        return self.__repo.load_product(*args, **kwargs)

    def save_product(self, *args, **kwargs):
        return self.__repo.save_product(*args, **kwargs)

    #endregion
    #region Object search

    def find_objects(self, product=PfsConfig, configs=None, groupby='visit', **kwargs):
        
        """
        Find individual objects by looking them up in the config files.
        """

        # Update the parameters with the values provided in kwargs

        repo_filters = deepcopy(self.__repo.filters)
        object_filters = deepcopy(self.__object_filters)
        
        for k, v in kwargs.items():
            if hasattr(repo_filters, k) and v is not None:
                getattr(repo_filters, k).values = v

            if hasattr(object_filters, k) and v is not None:
                getattr(object_filters, k).values = v

        # We either look up objects in PfsConfig files or look for the available PfsSingle files
        if product == PfsConfig:
            # If not provided, load the config files for each visit
            if configs is None:
                files, ids = self.find_product(PfsConfig, visit=repo_filters.visit, date=repo_filters.date)

                configs = {}
                for file in files:
                    config, id, fn = self.load_product(PfsConfig, filename=file)

                    # If the file is missing, and ignore_missing_files is True,
                    # the function silently returns a None, so simply skip it
                    if config is not None:
                        configs[id.visit] = config

            identities = {}
            for visit, config in configs.items():
                # Find objects matching the criteria
                mask = np.full(config.fiberId.shape, True)

                mask &= object_filters.fiberId.mask(config.fiberId)
                mask &= repo_filters.catId.mask(config.catId)
                mask &= repo_filters.objId.mask(config.objId)
                mask &= object_filters.targetType.mask(config.targetType)
                mask &= object_filters.proposalId.mask(config.proposalId)
                mask &= object_filters.obCode.mask(config.obCode)

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

    #endregion
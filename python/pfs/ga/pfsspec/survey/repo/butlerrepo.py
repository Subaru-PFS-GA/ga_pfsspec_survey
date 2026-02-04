from types import SimpleNamespace
from numbers import Number

from ..setup_logger import logger

try:
    from lsst.daf.butler import Butler, EmptyQueryResultError
except ImportError:
    logger.warning("Butler is not available. Ensure that the lsst.daf.butler package is installed.")
    Butler = None

from ..constants import Constants
from .repo import Repo
from .intfilter import IntFilter
from .hexfilter import HexFilter
from .datefilter import DateFilter
from .stringfilter import StringFilter

class ButlerRepo(Repo):
    def __init__(self,
                 config=None,
                 orig=None):
    
        super().__init__(config=config, orig=orig)

        self.__butler = Butler(
            config = self.get_resolved_variable('butlerconfigdir'),
            collections = self.get_resolved_variable('butlercollections').split(':'),
            writeable = False)
        
    #region Properties

    def __get_butler(self):
        return self.__butler
    
    butler = property(__get_butler)

    def __get_is_filesystem_repo(self):
        return False

    is_filesystem_repo = property(__get_is_filesystem_repo)

    #endregion

    def __find_datasets(self, product_name, params_regex, params, param_values, variables):

        # Unwrap the parameters
        params = { k: p.copy() for k, p in params.__dict__.items() }

        # Update the parameters with the values
        for k, v in param_values.items():
            if k in params:
                if v is not None:
                    params[k].values = v
                elif hasattr(self.filters, k):
                    params[k].values = getattr(self.filters, k)

        # Generate the where clause from the parameters
        where = []
        for k, p in params.items():
            if not p.is_none:
                ww = []
                for v in p.values:
                    if isinstance(v, tuple):
                        ww.append(f'{v[0]} <= {k} AND {k} <= {v[1]}')
                    elif isinstance(v, Number):
                        ww.append(f'{k} = {v}')
                    elif isinstance(v, str):
                        ww.append(f'{k} = "{v}"')
                if len(ww) > 0:
                    where.append('(' + ' OR '.join(ww) + ')')
        where = ' AND '.join(where)

        try:
            datasetRefs = self.__butler.query_datasets(
                product_name,
                where = where
            )
        except EmptyQueryResultError:
            logger.warning(f'No datasets found for product {product_name} with parameters: {params}.')
            datasetRefs = []

        # Convert Butler datasets into file paths and identities
        filenames = []
        identities = { p: [] for p in params }
        for dsref in datasetRefs:
            # Get the file path
            uri = self.__butler.getURI(dsref)
            if uri.scheme == 'file':
                filenames.append(uri.ospath)
            else:
                filenames.append(str(uri))

            # Get the identity
            for p in params:
                if p in dsref.dataId:
                    identities[p].append(dsref.dataId[p])
                else:
                    identities[p].append(None)

        identities = SimpleNamespace(**identities)

        return filenames, identities
    
    def has_product(self, product):
        """
        Checks if the repository has the specified product.

        Arguments
        ---------
        product : type
            Type of the product to check.

        Returns
        -------
        bool
            True if the product is available in the repository, False otherwise.
        """

        try:
            # Butler is case-sensitive, ensure product names match exactly
            name = product.__name__
            name = name[0].lower() + name[1:]  # Convert first letter to lowercase

            self.__butler.get_dataset_type(name)
            return True
        except Exception:
            return False

    def find_product(self, product, variables=None, **kwargs):
        """
        Finds product files that match the specified filters.

        Arguments
        ---------
        product : type
            Type of the product to find.
        variables : dict
            Dictionary of variables that can be expanded in the file paths.
        kwargs : dict
            Additional parameters to match the product identity. Can be of one of scalar type,
            or a SearchFilter instance.

        Returns
        -------
        list of str
            List of paths to the files that match the query.
        SimpleNamespace
            List of identities that match the query.
        """

        # Use all specified filters with function arguments taking precedence
        params = { k: p.copy() for k, p in self.filters.__dict__.items() }
        params.update(kwargs)

        logger.debug(f'Finding product {self.config.products[product].name} with parameters: {params}.')

        # TODO: implement finding sub-products in container products

        return self.__find_datasets(
            self.config.products[product].name,
            params_regex = self.config.products[product].params_regex,
            params = self.config.products[product].params,
            param_values = params,
            variables = variables
        )
    
    def save_product(self, data, filename=None, identity=None, variables=None, create_dir=True):
        raise NotImplementedError()
import os
import re
import inspect
from types import SimpleNamespace

from ..setup_logger import logger

class Repo():
    """
    Implements generic functions to access a data repository.
    """

    __expandvars_regex = re.compile(r'\$(\w+|\{[^}]*\})', re.ASCII)

    def __init__(self, config=None, orig=None):

        if not isinstance(orig, Repo):
            self.__ignore_missing_files = False

            self.__config = config
            self.__variables = self._init_variables()
            self.__filters = self._init_filters()
        else:
            self.__ignore_missing_files = orig.__ignore_missing_files

            self.__config = config if config is not None else orig.__config
            self.__variables = orig.__variables
            self.__filters = self._init_filters()
            
    def _init_variables(self):
        # Enumerate all variables that appear in the config and make a 
        # unique dictionary of them
        all_vars = {}
        for k, v in self.__config.variables.items():
            all_vars[k] = v

        return all_vars

    def _init_filters(self):
        # Enumerate all parameters that appear in the config and make a 
        # unique dictionary of them
        all_filters = {}
        for product in self.__config.products.values():
            for k, p in product.params.__dict__.items():
                all_filters[k] = p.copy()
        return SimpleNamespace(**all_filters)

    #region Properties

    def __get_ignore_missing_files(self):
        return self.__ignore_missing_files
    
    def __set_ignore_missing_files(self, value):
        self.__ignore_missing_files = value

    ignore_missing_files = property(__get_ignore_missing_files, __set_ignore_missing_files)

    def __get_config(self):
        return self.__config
    
    config = property(__get_config)

    def __get_filters(self):
        return self.__filters
    
    filters = property(__get_filters)

    def __get_variables(self):
        return self.__variables
    
    variables = property(__get_variables)

    #endregion
    #region Command-line arguments

    def add_args(self, script, include_variables=True, include_filters=True, ignore_duplicates=False):
        script.add_arg('--ignore-missing-files', action='store_true',
                       default=None,
                        help='Ignore missing data files.',
                        ignore_duplicate=ignore_duplicates)

        # Add arguments for the variables
        if include_variables:
            for k, v in self.__config.variables.items():
                script.add_arg(f'--{k.lower()}', type=str, help=f'Set variable {k}',
                               ignore_duplicate=ignore_duplicates)

        # Add arguments for the filters
        if include_filters:
            for k, p in self.__filters.__dict__.items():
                script.add_arg(f'--{k.lower()}', type=str, nargs='*', help=f'Filter on {k}',
                               ignore_duplicate=ignore_duplicates)

    def init_from_args(self, script):
        self.__ignore_missing_files = script.get_arg('ignore_missing_files', default=self.__ignore_missing_files)

        # Parse variables
        for k, v in self.__config.variables.items():
            if script.is_arg(k.lower()):
                self.__variables[k] = script.get_arg(k.lower())

        # Parse the filter parameters
        for k, p in self.__filters.__dict__.items():
            if script.is_arg(k.lower()):
                p.parse(script.get_arg(k.lower()))

    #endregion
    #region Utility functions

    def _throw_or_warn(self, message, required, exception_type=ValueError):
        """
        If required is True, raises an exception with the specified message, otherwise logs a warning.

        Arguments
        ---------
        message : str
            Message to log or raise.
        required : bool
            If True, an exception is raised. Otherwise, a warning is logged.
        exception_type : Exception
            Type of the exception to raise. Default is ValueError.
        """

        if required:
            raise exception_type(message)
        else:
            logger.warning(message)

    def _ensure_one_arg(self, **kwargs):
        """
        Ensures that only one parameter is specified in the keyword arguments.

        Arguments
        ---------
        kwargs : dict
            Keyword arguments to check.

        Returns
        -------
        str
            Name of the parameter that is specified.
        """

        if sum([1 for x in kwargs.values() if x is not None]) > 1:
            names = ', '.join(kwargs.keys())
            raise ValueError(f'Only one of the parameters {names} can be specified .')

    #endregion
    #region Variables

    def set_variable(self, name, value):
        """
        Sets the value of a variable.

        Arguments
        ---------
        name : str
            Name of the variable.
        value : str
            Value of the variable.
        """

        self.__variables[name] = value

    def get_variable(self, name):
        """
        Returns the value of a variable.

        Arguments
        ---------
        name : str
            Name of the variable.
        """

        return self.__variables[name]

    def get_resolved_variable(self, name, variables=None):
        """
        Returns the value of a variable with all $ variables expanded, including
        the ones defined in the config and in the environment.
        """

        path = f'${name}'
        path = self.expand_variables(path, variables)
        path = self.expand_variables(path, self.__variables)
        path = self.expand_variables(path, os.environ)
        return path

    def expand_variables(self, path, variables: dict):
        """
        Expand shell variables of form $var and ${var}.  Unknown variables
        are left unchanged. Stolen from os.path.expandvars.
        """

        if variables is None:
            return path

        path = os.fspath(path)
        
        if '$' not in path:
            return path
        
        search = Repo.__expandvars_regex.search
        start = '{'
        end = '}'

        i = 0
        while True:
            m = search(path, i)
            if not m:
                break
            i, j = m.span(0)
            name = m.group(1)
            if name.startswith(start) and name.endswith(end):
                name = name[1:-1]
            try:
                value = variables[name]
            except KeyError:
                i = j
            else:
                tail = path[j:]
                path = path[:i] + value
                i = len(path)
                path += tail

        return path

    #endregion
    #region Products

    def __parse_identity(self, regex, path: str, params: SimpleNamespace):
        """
        Parses parameters from the filename using the specified regex pattern.

        Arguments
        ---------
        path : str
            Path to the file.
        """

        # Match the filename pattern to find the IDs
        match = re.search(regex, path)
        if match is not None:
            groups = match.groupdict()
            values = { k: p.parse_value(groups[k]) for k, p in params.items() if k in groups }

            logger.debug(f'Parsed identity: {values} from {path}.')

            return SimpleNamespace(**values)
        else:
            return None

    def _get_single_file(self, files, identities):
        """
        Given a list of files and a list of identifiers, returns the single file that matches the query.
        If more than one file is found, an exception is raised. If no files are found, an exception is raised.

        Arguments
        ---------
        files : list of str
            List of paths to the files that match the query.
        identities : SimpleNamespace
            List of identifiers that match the query.

        Returns
        -------
        str
            Path to the file that matches the query.
        SimpleNamespace
            Identifiers that match the query.
        """

        if len(files) == 0:
            raise FileNotFoundError(f'No file found matching the query.')
        elif len(files) > 1:
            raise FileNotFoundError(f'Multiple files found matching the query.')
        else:
            return files[0], SimpleNamespace(**{ k: v[0] for k, v in identities.__dict__.items() })

    def has_product(self, product):
        """
        Checks if the repository has a product of the specified type.

        Arguments
        ---------
        product : type
            Type of the product to check.

        Returns
        -------
        bool
            True if the product is available, False otherwise.
        """

        return product in self.__config.products

    def match_product_type(self, filename):
        """
        Parses the product type from the filename.

        Arguments
        ---------
        filename : str
            Path to the file.
        
        Returns
        -------
        type
            Type of the product.
        """

        # Try to match each product regex pattern against the filename
        for product, config in self.__config.products.items():
            for regex in config.params_regex:
                if re.search(regex, filename):
                    return product

    def parse_product_type(self, product):
        """
        Based on a string, figure out the product type.

        Arguments
        ---------
        product : str
            String representation of the product type.
        """

        product = product.lower()
        parts = product.split(',')

        for t in self.__config.products.keys():
            if isinstance(t, tuple) and len(t) == 2 and len(parts) == 2:
                # This is a container product
                if t[0].__name__.lower() == parts[0] and t[1].__name__.lower() == parts[1]:
                    return t
            elif inspect.isclass(t) and t.__name__.lower() == product:
                # This is a single product
                return t
            
        raise ValueError(f'Product type not recognized: {product}')

    def parse_product_identity(self, product, path: str, required=True):
        """
        Parses parameters from the filename using the specified regex pattern.

        Arguments
        ---------
        path : str
            Path to the file.
        params : SimpleNamespace
            Parameters to parse from the filename.
        regex : str
            Regular expression pattern to match the filename. The regex should contain named groups
            that correspond to the parameters in the SimpleNamespace.

        Returns
        -------
        SimpleNamespace
            Parsed identity parameters, or None, when the filename does not match the expected format.
        """

        # Unwrap the parameters
        params = self.__config.products[product].params.__dict__

        # Try to parse with each regular expression defined in the config
        for regex in self.__config.products[product].params_regex:
            identity = self.__parse_identity(regex, path, params)
            if identity is not None:
                return identity
        
        # If no match is found
        self._throw_or_warn(f'Filename does not match expected format: {path}', required)
        return None

    def get_identity(self, data):
        """
        Returns the identity of the product.

        Arguments
        ---------
        data : object
            Product data.
        """

        return self.__config.products[type(data)].identity(data)

    def find_product(self, product, variables=None, **kwargs):
        raise NotImplementedError()

    def locate_product(self, product=None, variables=None, **kwargs):
        raise NotImplementedError()

    def load_product(self,
                     product=None,
                     filename=None,
                     identity=None,
                     variables=None,
                     ignore_missing_files=None,
                     **kwargs):
        
        """
        Loads a product from a file or based on identity.

        Arguments
        ---------
        product : type
            Type of the product to load.
        filename : str
            Path to the file to load.
        identity : SimpleNamespace
            Identity of the product to load. If it is a container product, it should 
            only contain the parameters of the container and all other parameters
            should be passed as keyword arguments.
        variables : dict
            Dictionary of variables that can be expanded in the file paths.
        ignore_missing_files: bool
            If True, missing files are ignored and None is returned instead of raising an exception.
        kwargs : dict
            Additional parameters to pass to the load function of the product.

        Returns
        -------
        object
            Loaded product.
        SimpleNamespace
            Identity of the product.
        str
            Path to the file that was loaded.
        """

        self._ensure_one_arg(filename=filename, identity=identity)
        ignore_missing_files = ignore_missing_files if ignore_missing_files is not None else self.__ignore_missing_files

        if product is None and filename is not None:
            product = self.match_product_type(filename)

        if isinstance(product, str):
            product = self.parse_product_type(product)

        # Some products cannot be loaded by filename, so we need to parse the identity. If the
        # identity is not provided, use the filters.
        if filename is not None:
            identity = self.parse_product_identity(product, filename, required=True)
            params = identity.__dict__
        elif isinstance(identity, dict):
            params = identity
        elif isinstance(identity, SimpleNamespace):
            params = identity.__dict__
        else:
            params = { k: p.copy() for k, p in self.filters.__dict__.items() if not p.is_none }
           
        # The file name might not contain all information necessary to load the
        # product, so given the parsed identity, we need to locate the file.
        filename, identity = self.locate_product(product, variables=variables, **params)
        dir = os.path.dirname(filename)

        # Load the product via the dispatcher
        logger.debug(f'Loading product {self.config.products[product].name} from {filename}.')
        try:
            data = self.config.products[product].load(identity, filename, dir, **kwargs)
        except FileNotFoundError as ex:
            if ignore_missing_files:
                logger.warning(f'File not found: {filename}. Ignoring missing file.')
                return None, None, filename
            else:
                raise ex

        return data, identity, filename

    def load_products_from_container(self,
                                     container,
                                     product,
                                     filename=None,
                                     identity=None,
                                     variables=None,
                                     ignore_missing_files=None,
                                     **kwargs):

        """
        Load data products that are subproducts of a container product.

        Arguments
        ---------
        container : type
            Type of the container product.
        product : type
            Type of the product to load from the container.
        filename : str
            Path to the container file to load. If None, the identity is used to locate the file.
        identity : SimpleNamespace
            Identity of the product to load.
        variables : dict
            Dictionary of variables that can be expanded in the file paths by the repository.
        ignore_missing_files: bool
            If True, missing files are ignored and None is returned instead of raising an exception.
        kwargs : dict
            Additional parameters to pass to the load function of the product.
        """

        if filename is not None:
            cid = self.parse_product_identity(container, filename, required=True)
            params = cid.__dict__
        elif isinstance(identity, dict):
            params = identity
        elif isinstance(identity, SimpleNamespace):
            params = identity.__dict__
        else:
            params = { k: p.value for k, p in self.filters.__dict__.items() if p.is_constant }
           
        # The file name might not contain all information necessary to load the
        # product, so given the parsed identity, we need to locate the file.
        filename, cid = self.locate_product(container, variables=variables, **params)
        dir = os.path.dirname(filename)

        # At this point cid contains the parameters that are associated with the container only,
        # but any additional filters that are defined on the class need to be applied.
        # Since we don't expect that the load function supports range filters, we only pass in
        # the constants
        for k, p in self.filters.__dict__.items():
            if p.is_constant:
                params[k] = p.value

        # Load the product via the dispatcher
        logger.debug(f'Loading product {self.config.products[(container, product)].name} from {filename}.')
        try:
            # load function expects an identity, it isn't supposed to support filters
            # so pass in filters as part of the identity and assumed that there are no
            # range filter in the list
            identity = SimpleNamespace(**params)
            data = self.config.products[(container, product)].load(identity, filename, dir, **kwargs)
        except FileNotFoundError as ex:
            if ignore_missing_files:
                logger.warning(f'File not found: {filename}. Ignoring missing file.')
                return None
            else:
                raise ex

        return [ (d, id, filename) for d, id in data ]

    def save_product(self, data, filename=None, identity=None, variables=None,
                     exist_ok=True,
                     create_dir=True):
        raise NotImplementedError()

    #region
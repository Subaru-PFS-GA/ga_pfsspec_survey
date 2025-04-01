import os
import re
from glob import glob
from types import SimpleNamespace
import inspect

import pfs.datamodel
from pfs.datamodel import *

from ..setup_logger import logger

from ..constants import Constants
from .intfilter import IntFilter
from .hexfilter import HexFilter
from .datefilter import DateFilter
from .stringfilter import StringFilter

class FileSystemRepo():
    """
    Implements routines to find data products in the file system.
    This is a replacement of Butler etc. for local development.

    The class works by querying the file system with glob for files that match the specified parameters.
    The parameters can either be defined on the class level or passed as arguments to the methods.
    Method arguments always take precedence over class-level parameters.

    Variables
    ---------
    config : SimpleNamespace
        Configuration object that contains the product definitions.
    product : type
        Type of the product to work with.
    variables : dict
        Dictionary of variables that can be expanded in the file paths.
    filters : dict
        Namespace of all parameters filter that appear in the config and can be
        used to filter the products.
    """

    __expandvars_regex = re.compile(r'\$(\w+|\{[^}]*\})', re.ASCII)

    def __init__(self,
                 config=None,
                 orig=None):
        
        if not isinstance(orig, FileSystemRepo):
            self.__config = config
            self.__product = None
            self.__variables = self.__init_variables()
            self.__filters = self.__init_filters()
        else:
            self.__config = config if config is not None else orig.__config
            self.__product = orig.__product
            self.__variables = orig.__variables
            self.__filters = self.__init_filters()

    def __init_variables(self):
        # Enumerate all variables that appear in the config and make a 
        # unique dictionary of them
        all_vars = {}
        for k, v in self.__config.variables.items():
            all_vars[k] = v

        return all_vars

    def __init_filters(self):
        # Enumerate all parameters that appear in the config and make a 
        # unique dictionary of them
        all_filters = {}
        for product in self.__config.products.values():
            for k, p in product.params.__dict__.items():
                all_filters[k] = p.copy()
        return SimpleNamespace(**all_filters)

    #region Properties

    def __get_config(self):
        return self.__config
    
    config = property(__get_config)

    def __get_product(self):
        return self.__product
    
    def __set_product(self, value):
        self.__product = value
    
    product = property(__get_product, __set_product)

    def __get_filters(self):
        return self.__filters
    
    filters = property(__get_filters)

    def __get_variables(self):
        return self.__variables
    
    variables = property(__get_variables)

    #endregion
    #region Command-line arguments

    def add_args(self, script, include_variables=True, include_filters=True):
        # Add arguments for the variables
        if include_variables:
            for k, v in self.__config.variables.items():
                script.add_arg(f'--{k.lower()}', type=str, help=f'Set variable {k}')

        # Add arguments for the filters
        if include_filters:
            for k, p in self.__filters.__dict__.items():
                script.add_arg(f'--{k.lower()}', type=str, nargs='*', help=f'Filter on {k}')

    def init_from_args(self, script):
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

    def __throw_or_warn(self, message, required, exception_type=ValueError):
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

    def __ensure_one_arg(self, **kwargs):
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
        
    def __expandvars(self, path, variables: dict):
        """
        Expand shell variables of form $var and ${var}.  Unknown variables
        are left unchanged. Stolen from os.path.expandvars.
        """

        if variables is None:
            return path

        path = os.fspath(path)
        
        if '$' not in path:
            return path
        
        search = FileSystemRepo.__expandvars_regex.search
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

    def __find_files_and_match_params(self,
                                      patterns: list,
                                      params: SimpleNamespace,
                                      param_values: dict,
                                      params_regex: list,
                                      variables: dict):
        """
        Given a list of directory name glob pattern template strings, substitute the parameters
        and find files that match the glob pattern. Match IDs is in the file names with the
        parameters and return the matched IDs, as well as the paths to the files. The final
        list is filtered by the parameters.

        Arguments
        ---------
        patterns : str
            List of directory name glob pattern template strings.
        params : SimpleNamespace
            Parameters to match the IDs in the file names.
        param_values : dict
            Values of the parameters to match the IDs in the file names.
        params_regex : str
            Regular expression patterns to match the filename. The regex should contain named groups
            that correspond to the parameters of the product identity. The list should consist of
            more restrictive patterns first.
        variables : dict
            Dictionary of variables that can be expanded in the file paths.

        Returns
        -------
        list of str
            List of paths to the files that match the query.
        SimpleNamespace
            List of identifiers that match the query.
        """

        # Unwrap the parameters
        params = { k: p.copy() for k, p in params.__dict__.items() }

        # Update the parameters with the values
        for k, v in param_values.items():
            if k in params:
                if v is not None:
                    params[k].values = v
                elif hasattr(self.__filters, k):
                    params[k].values = getattr(self.__filters, k)

        # Substitute patterns in  variables with environment variables
        vars = {}
        if self.__variables is not None:
            for k, v in self.__variables.items():
                vars[k] = self.__expandvars(v, os.environ)
        if variables is not None:
            for k, v in variables.items():
                vars[k] = self.__expandvars(v, os.environ)

        # Substitute config variables into the glob pattern
        patts = []
        for p in patterns:
            p = self.__expandvars(p, vars)
            p = self.__expandvars(p, os.environ)
            patts.append(p)

        # Evaluate the glob pattern for each filter parameter
        glob_pattern_parts = { k: p.get_glob_pattern() for k, p in params.items() }

        # Compose the full glob pattern
        glob_pattern = os.path.join(*[ p.format(**glob_pattern_parts) for p in patts ])

        # Find the files that match the glob pattern
        # Set breakpoint here to debug issues regarding files not found
        logger.debug(f'Finding files with glob using pattern: `{glob_pattern}`.')
        paths = glob(glob_pattern)
        
        logger.debug(f'Found {len(paths)} files matching the pattern, starting filtering.')
        logger.debug(f'Filtering files matching the params {params}.')

        ids = { k: [] for k in params.keys() }
        values = { k: None for k in params.keys() }
        filenames = []
        for path in paths:
            for regex in params_regex:
                # Match the filename pattern to find the IDs
                match = re.search(regex, path)
                
                if match is not None:
                    # If all parameters match the param filters, add the IDs to the list
                    good = True
                    for k, param in params.items():
                        # Parse the string value from the match and convert it to the correct type
                        values[k] = param.parse_value(match.group(k))

                        # Match the parameter against the filter. This is a comparison
                        # against the values and value ranges specified in the filter.
                        good &= param.match(values[k])

                    if good:
                        filenames.append(path)
                        for k, v in values.items():
                            ids[k].append(v)
                        
                    break # for regex in regex_list

        logger.debug(f'Found {len(filenames)} files matching the query.')

        return filenames, SimpleNamespace(**ids)
    
    def __get_single_file(self, files, identities):
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
        
    #endregion
    #region Products

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
        path = self.__expandvars(path, variables)
        path = self.__expandvars(path, self.__variables)
        path = self.__expandvars(path, os.environ)
        return path

    def parse_product_type(self, product):
        """
        Based on a string, figure out the product type.

        Arguments
        ---------
        product : str
            String representation of the product type.
        """

        product = product.lower()

        for t in self.__config.products.keys():
            if inspect.isclass(t) and t.__name__.lower() == product:
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
        self.__throw_or_warn(f'Filename does not match expected format: {path}', required)
        return None
    
    def find_product(self, product=None, variables=None, **kwargs):
        """
        Finds product files that match the specified filters.

        Arguments
        ---------
        product : type
            Type of the product to find.
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

        product = product if product is not None else self.__product

        # Use all specified filters with function arguments taking precedence
        params = { k: p.copy() for k, p in self.__filters.__dict__.items() if not p.is_none }
        params.update(kwargs)

        logger.debug(f'Finding product {product.__name__} with parameters: {params}.')

        return self.__find_files_and_match_params(
            patterns = [
                self.__config.products[product].dir_format,
                self.__config.products[product].filename_format,
            ],
            params_regex = self.__config.products[product].params_regex,
            params = self.__config.products[product].params,
            param_values = params,
            variables = variables)
    
    def locate_product(self, product=None, variables=None, **kwargs):
        """
        Finds a specific product file.

        Arguments
        ---------
        product : type
            Type of the product to locate.
        kwargs : dict
            Additional parameters to match the product identity. Can be of one of scalar type,
            or a SearchFilter instance.

        Returns
        -------
        str
            Path to the file that matches the query.
        SimpleNamespace
            The identity of the product that matches the query.
        """

        product = product if product is not None else self.__product

        files, ids = self.find_product(product, variables=variables, **kwargs)
        return self.__get_single_file(files, ids)
    
    def load_product(self, product=None, filename=None, identity=None, variables=None):
        """
        Loads a product from a file or based on identity.

        Arguments
        ---------
        product : type
            Type of the product to load.
        filename : str
            Path to the file to load.
        identity : SimpleNamespace
            Identity of the product to load.
        variables : dict
            Dictionary of variables that can be expanded in the file paths.

        Returns
        -------
        object
            Loaded product.
        SimpleNamespace
            Identity of the product.
        str
            Path to the file that was loaded.
        """

        self.__ensure_one_arg(filename=filename, identity=identity)

        product = product if product is not None else self.__product

        # Some products cannot be loaded by filename, so we need to parse the identity
        if filename is not None:
            identity = self.parse_product_identity(product, filename, required=True)
            params = identity.__dict__
        elif isinstance(identity, dict):
            params = identity
        elif isinstance(identity, SimpleNamespace):
            params = identity.__dict__
        else:
            params = { k: p.copy() for k, p in self.__filters.__dict__.items() if p.value is not None }
           
        # The file name might not contain all information necessary to load the
        # product, so given the parsed identity, we need to locate the file.
        filename, identity = self.locate_product(product, variables=variables, **params)
        dir = os.path.dirname(filename)

        # Load the product via the dispatcher
        logger.debug(f'Loading product {product.__name__} from {filename}.')
        data = self.__config.products[product].load(identity, filename, dir)

        return data, identity, filename
    
    def save_product(self, data, filename=None, identity=None, variables=None, create_dir=True):
        """
        Saves a product to a file. The filename is either provided or constructed based on the identity.

        Arguments
        ---------
        product : object
            Product to save.
        filename : str
            Path to the file to save.
        identity : SimpleNamespace
            Identity of the product.
        variables : dict
            Dictionary of variables that can be expanded in the file paths.

        Returns
        -------
        SimpleNamespace
            Identity of the product.
        str
            Path to the file that was saved.
        """

        product = type(data)
        identity = self.get_identity(data) if identity is None else identity

        # These are the intended locations that might be overriden if filename is provided
        if filename is None:
            dir = self.format_dir(product, identity, variables=variables)
            filename = self.format_filename(product, identity, variables=variables) if filename is None else filename
            filename = os.path.join(dir, filename)
        else:
            dir = os.path.dirname(filename)

        if create_dir and not os.path.exists(dir):
            logger.debug(f'Creating directory {dir}.')
            os.makedirs(dir, exist_ok=True)

        # Save the product via the dispatcher
        logger.debug(f'Savinging product {product.__name__} to {filename}.')
        self.__config.products[product].save(data, identity, filename, dir)

        return identity, filename
    
    def __format_path(self, product, identity, format_string, variables=None):
        params = self.__config.products[product].params.__dict__
        identity = identity.__dict__
        values = { k: p.format.format(identity[k]) for k, p in params.items() if k in identity }
        path = format_string.format(**values)
        path = self.__expandvars(path, variables)
        path = self.__expandvars(path, self.__variables)
        path = self.__expandvars(path, os.environ)
        return path
    
    def format_dir(self, product, identity, variables=None):
        """
        Formats the directory path for the given product and identity.

        Arguments
        ---------
        product : type
            Type of the product.
        identity : SimpleNamespace
            Identity of the product.
        """

        format_string = self.__config.products[product].dir_format
        return self.__format_path(product, identity, format_string, variables=variables)
    
    def format_filename(self, product, identity, variables=None):
        """
        Formats the filename for the given product and identity.

        Arguments
        ---------
        product : type
            Type of the product.
        identity : SimpleNamespace
            Identity of the product.
        """

        format_string = self.__config.products[product].filename_format
        return self.__format_path(product, identity, format_string, variables=variables)
    
    def get_identity(self, data):
        """
        Returns the identity of the product.

        Arguments
        ---------
        data : object
            Product data.
        """

        return self.__config.products[type(data)].identity(data)

    #endregion

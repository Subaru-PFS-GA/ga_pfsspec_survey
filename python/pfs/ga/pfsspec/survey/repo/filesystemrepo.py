import os
import re
from glob import glob
from types import SimpleNamespace

from ..setup_logger import logger

from ..constants import Constants
from .repo import Repo
from .intfilter import IntFilter
from .hexfilter import HexFilter
from .datefilter import DateFilter
from .stringfilter import StringFilter

class FileSystemRepo(Repo):
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

    def __init__(self,
                 config=None,
                 orig=None):
        
        super().__init__(config=config, orig=orig)

    #region Properties

    def __get_is_filesystem_repo(self):
        return True

    is_filesystem_repo = property(__get_is_filesystem_repo)

    #endregion
    #region Utility functions

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
                elif hasattr(self.filters, k):
                    params[k].values = getattr(self.filters, k)

        # Substitute patterns in variables with environment variables
        vars = {}
        if self.variables is not None:
            for k, v in self.variables.items():
                vars[k] = self.expand_variables(v, os.environ)
        if variables is not None:
            for k, v in variables.items():
                vars[k] = self.expand_variables(v, os.environ)

        # Substitute config variables into the glob pattern
        patts = []
        for p in patterns:
            p = self.expand_variables(p, vars)
            p = self.expand_variables(p, os.environ)
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
                    # Some parameters are allowed to be missing because they might not be part of the filename
                    good = True
                    groups = match.groupdict()
                    for k, param in params.items():
                        if k in groups:
                            # Parse the string value from the match and convert it to the correct type
                            values[k] = param.parse_value(groups[k])

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
        
    #endregion
    #region Products
    
    def find_product(self, product=None, variables=None, **kwargs):
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
        params = { k: p.copy() for k, p in self.filters.__dict__.items() if not p.is_none }
        params.update(kwargs)

        logger.debug(f'Finding product {self.config.products[product].name} with parameters: {params}.')

        return self.__find_files_and_match_params(
            patterns = [
                self.config.products[product].dir_format,
                self.config.products[product].filename_format,
            ],
            params_regex = self.config.products[product].params_regex,
            params = self.config.products[product].params,
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

        files, ids = self.find_product(product, variables=variables, **kwargs)
        return self._get_single_file(files, ids)
    
    def save_product(self, data, filename=None, identity=None, variables=None,
                     exist_ok=True, create_dir=True):
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
        dir, filename, identity = self.get_data_path(data, filename=filename,
                                                     identity=identity,
                                                     variables=variables)

        # These are the intended locations that might be overriden if filename is provided
        if filename is None:
            dir = self.format_dir(product, identity, variables=variables)
            filename = self.format_filename(product, identity, variables=variables) if filename is None else filename
            filename = os.path.join(dir, filename)
        else:
            dir = os.path.dirname(filename)

        if not exist_ok and os.path.exists(filename):
            raise FileExistsError(f'File {filename} already exists. Use `exist_ok=True` to overwrite it.')

        if create_dir and not os.path.exists(dir):
            logger.debug(f'Creating directory {dir}.')
            os.makedirs(dir, exist_ok=True)

        # Save the product via the dispatcher
        logger.debug(f'Saving product {product.__name__} to {filename}.')
        self.config.products[product].save(data, identity, filename, dir)

        return identity, filename
    
    def __format_path(self, product, identity, format_string, variables=None):
        params = self.config.products[product].params.__dict__
        if not isinstance(identity, dict):
            identity = identity.__dict__
        values = { k: p.format.format(identity[k]) for k, p in params.items() if k in identity }
        path = format_string.format(**values)
        path = self.expand_variables(path, variables)
        path = self.expand_variables(path, self.variables)
        path = self.expand_variables(path, os.environ)
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

        format_string = self.config.products[product].dir_format
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

        format_string = self.config.products[product].filename_format
        return self.__format_path(product, identity, format_string, variables=variables)

    def get_data_path(self, data, filename=None, identity=None, variables=None):
        product = type(data)
        identity = self.get_identity(data) if identity is None else identity

        if filename is None:
            dir = self.format_dir(product, identity, variables=variables)
            filename = self.format_filename(product, identity, variables=variables) if filename is None else filename
            filename = os.path.join(dir, filename)
        else:
            dir = os.path.dirname(filename)

        return dir, filename, identity

    #endregion

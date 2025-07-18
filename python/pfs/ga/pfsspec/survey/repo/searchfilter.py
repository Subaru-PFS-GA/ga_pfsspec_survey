from collections.abc import Iterable
import numpy as np

class SearchFilter():
    """
    Implements an argument parser for ID filters and logic to match
    ranges of IDs within file names.

    ID filters are used to select a subset of files based on their IDs and are
    specified on the command-line as strings which are parsed into a list of strings
    by `ArgParse`. The strings within a list can be single IDs or ranges of IDs
    separated by a hyphen. For example, the argument `--visit 120 123-127` would be
    parsed into the list `['123', ('123', '127')]`.
    """

    def __init__(self, *values, name=None, format=None, orig=None):
        if not isinstance(orig, SearchFilter):
            self._name = name
            self._format = format if format is not None else '{}'
            self._values = self._normalize_values(values)
        else:
            self._name = name if name is not None else orig._name
            self._format = format if format is not None else orig._format
            self._values = self._normalize_values(values if values is not None and len(values) > 0 else orig._values)

    def copy(self):
        return type(self)(orig=self)

    def _normalize_values(self, values):
        """
        Normalize the values of the filter.
        """

        if values is None:
            return None
        elif isinstance(values, SearchFilter):
            return values.values
        elif isinstance(values, str):
            return [values]
        elif isinstance(values, Iterable):
            if len(values) == 0:
                return None
            elif len(values) == 1 and isinstance(values[0], SearchFilter):
                return values[0].values
            else: # list of scalars, hopefully
                return list(values)
        else: # scalar, hopefully
            return [values]

    def __str__(self):
        """
        Convert the ID filter into a string.
        """
        
        if self._values is not None:
            r = ''
            for a in self._values:
                if r != '':
                    r += ' '

                if isinstance(a, tuple):
                    r += '{}-{}'.format(self._format.format(a[0]), self._format.format(a[1]))
                else:
                    r += self._format.format(a)
            return r
        else:
            return ''
    
    def __repr__(self):
        if self._values is not None:
            r = ', '.join(repr(a) for a in self._values)
        else:
            r = 'None'

        if self._name is not None:
            r += f', name=\'{self._name}\''

        return f'{self.__class__.__name__}({r})'

    def __get_name(self):
        return self._name
    
    def __set_name(self, value):
        self._name = value

    name = property(__get_name, __set_name)

    def __get_format(self):
        return self._format
    
    def __set_format(self, value):
        self._format = value

    format = property(__get_format, __set_format)

    def __get_values(self):
        return self._values
    
    def __set_values(self, value):
        self._values = self._normalize_values(value)
    
    values = property(__get_values, __set_values)

    def __get_value(self):
        if self._values is None:
            return None
        elif len(self._values) == 1 and not isinstance(self._values[0], tuple):
            return self._values[0]
        else:
            raise ValueError('Filter has multiple values')
        
    value = property(__get_value)

    def __is_none(self):
        return self._values is None or len(self._values) == 0
    
    is_none = property(__is_none)

    def __is_constant(self):
        return self._values is not None and \
            len(self._values) == 1 and \
            not isinstance(self._values[0], tuple)

    is_constant = property(__is_constant)

    def _parse_value(self, value):
        raise NotImplementedError()
    
    def parse_value(self, value):
        return self._parse_value(value)

    def _parse(self, arg: list):
        """
        Parse a list of arguments into individual IDs and ID ranges.
        """

        self._values = []

        if arg is not None:
            for a in arg:
                if '-' in a:
                    start, end = a.split('-')
                    self._values.append((self._parse_value(start), self._parse_value(end)))
                else:
                    self._values.append(self._parse_value(a))

    def parse(self, arg: list):
        self._parse(arg)

    def render(self, lower=False, upper=False):
        """
        Render the filter as a command-line argument string.
        """

        if self._values is None or len(self._values) == 0:
            return None
        else:
            if lower:
                args = f'--{self._name.lower()}'
            elif upper:
                args = f'--{self._name.upper()}'
            else:
                args = f'--{self._name}'
            
            # Override format strings here because
            for v in self._values:
                if isinstance(v, tuple):
                    args += f' {self._format.format(v[0])}-{self._format.format(v[1])}'
                else:
                    args += f' {self._format.format(v)}'
            return args

    def match(self, arg):
        """
        Return True if `arg` matches the filter. Arg can have various data types.
        
        The value matches the filter if the filter is empty or the value
        is equal to one of the values or within the inclusive range of one
        of the ranges in the filter.
        """

        if isinstance(arg, str):
            value = self._parse_value(arg)
        else:
            value = arg

        if self._values is None or len(self._values) == 0:
            return True
        else:
            for v in self._values:
                if isinstance(v, tuple) and value >= v[0] and value <= v[1]:
                        return True
                elif value == v:
                        return True

            return False

    def mask(self, values):
        """
        Create a boolean mask with True where the values match the filter.

        The values matche the filter if the filter is empty or the value
        is equal to one of the values or within the inclusive range of one
        of the ranges in the filter. 
        """

        mask = np.full_like(values, True, dtype=bool)

        if self._values is None or len(self._values) == 0:
            return mask
        else:
            for v in self._values:
                if isinstance(v, tuple):
                    mask &= (values >= v[0]) & (values <= v[1])
                else:
                    mask &= values == v

        return mask
            
    def get_glob_pattern(self):
        """
        Return a glob pattern that matches all IDs in the filter.
        """

        if self._values is not None and len(self._values) == 1 and not isinstance(self._values[0], tuple):
            return self._format.format(self._values[0])
        else:
            return '*'
        
    def get_regex_pattern(self):
        raise NotImplementedError()
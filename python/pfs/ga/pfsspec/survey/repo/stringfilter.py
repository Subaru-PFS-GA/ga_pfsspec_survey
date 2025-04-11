from collections.abc import Iterable
from fnmatch import fnmatch
import numpy as np

from .searchfilter import SearchFilter

class StringFilter(SearchFilter):
    """
    Implemented an argument parser for string filters and logic to match strings
    within file names.
    """
    
    def _parse_value(self, value):
        return value
    
    def match(self, arg):
        """
        Return True if `arg` matches the filter.
        
        The value matches the filter if the filter is empty or the value
        is equal to one of the values or within the inclusive range of one
        of the ranges in the filter.
        """

        if isinstance(arg, str):
            value = arg
        else:
            value = str(arg)

        if self._values is None or len(self._values) == 0:
            return True
        else:
            for v in self._values:
                # Check if value matches v based on wildcards
                if fnmatch(value, v):
                    return True

            return False

    def mask(self, values):
        mask = np.full_like(values, True, dtype=bool)

        if self._values is None or len(self._values) == 0:
            return mask
        else:
            for idx in np.ndindex(values.shape):
                mask[idx] = self.match(values[idx])

            return mask
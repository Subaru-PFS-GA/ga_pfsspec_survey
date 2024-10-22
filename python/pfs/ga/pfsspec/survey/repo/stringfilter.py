from collections.abc import Iterable

from .searchfilter import SearchFilter

class StringFilter(SearchFilter):
    """
    Implemented an argument parser for string filters and logic to match strings
    within file names.
    """
    
    def _parse_value(self, value):
        return value
    


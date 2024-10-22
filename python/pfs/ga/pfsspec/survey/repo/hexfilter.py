from .searchfilter import SearchFilter

class HexFilter(SearchFilter):
    """
    Implements an argument parser for hex ID filters and logic to match
    ranges of hex IDs within file names.
    """

    def __init__(self, *values, name=None, format=None, orig=None):

        super().__init__(*values, name=name, format=format, orig=orig)

        if not isinstance(orig, HexFilter):
            format = format if format is not None else '{:x}'
        else:
            format = format if format is not None else orig._format
       
    def _parse_value(self, value):
        return int(value, 16)
from .searchfilter import SearchFilter
from datetime import date
import dateutil.parser as dateparser

class DateFilter(SearchFilter):
    """
    Implements an argument parser for date filters and logic to match
    ranges of dates within file names.
    """

    FORMAT_GLOB_PATTERNS = {
        "%Y": "[0-9][0-9][0-9][0-9]",  # Match a 4-digit year
        "%m": "[0-1][0-9]",            # Match a 2-digit month
        "%d": "[0-3][0-9]",            # Match a 2-digit day
        "%H": "[0-2][0-9]",            # Match a 2-digit hour
        "%M": "[0-5][0-9]",            # Match a 2-digit minute
        "%S": "[0-5][0-9]",            # Match a 2-digit second
    }

    def __init__(self, *values, name=None, format=None, orig=None):

        if not isinstance(orig, DateFilter):
            format = format if format is not None else '{:%Y-%m-%d}'
        else:
            format =  format if format is not None else orig.format

        super().__init__(*values, name=name, format=format, orig=orig)

    def _parse_value(self, value):
        return dateparser.parse(value).date()
    
    def _parse(self, arg: list):
        """
        Parse a list of strings into a list of dates or date intervals.
        """
        
        self._values = []

        if arg is not None:
            for a in arg:
                # Count the number of dashes in the argument
                dashes = a.count('-')

                if dashes == 1:
                    # Range of dates, no separator
                    parts = a.split('-')
                    start, end = parts[0], parts[1]
                    self._values.append((self._parse_value(start), self._parse_value(end)))
                if dashes == 5:
                    # Range of dates, split at the third dash
                    parts = a.split('-')
                    start, end = '-'.join(parts[:3]), '-'.join(parts[3:])
                    self._values.append((self._parse_value(start), self._parse_value(end)))
                else:
                    # Single date
                    self._values.append(self._parse_value(a))

    def get_glob_pattern(self):
        """
        Return a glob pattern that matches all dates in the filter.
        """

        if self._values is not None and len(self._values) == 1 and not isinstance(self._values[0], tuple):
            return self.format.format(self._values[0])
        else:
            # TODO: this is specific to the default format string
            glob_pattern = self.format[2:-1]
            for key, value in DateFilter.FORMAT_GLOB_PATTERNS.items():
                glob_pattern = glob_pattern.replace(key, value)

            return glob_pattern
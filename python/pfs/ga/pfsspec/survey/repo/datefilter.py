from .searchfilter import SearchFilter
from datetime import date

class DateFilter(SearchFilter):
    """
    Implements an argument parser for date filters and logic to match
    ranges of dates within file names.
    """

    def __init__(self, *values, name=None, format=None, orig=None):

        format = format if format is not None else '{:%Y-%m-%d}'

        super().__init__(*values, name=name, format=format, orig=orig)

    def _parse_value(self, value):
        # Parse value as a date
        return date.fromisoformat(value)
    
    def _parse(self, arg: list):
        """
        Parse a list of strings into a list of dates or date intervals.
        """
        
        self._values = []

        if arg is not None:
            for a in arg:
                # Count the number of dashes in the argument
                dashes = a.count('-')

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
            return '????-??-??'
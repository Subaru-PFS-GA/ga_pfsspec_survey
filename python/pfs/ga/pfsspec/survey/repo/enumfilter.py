from enum import IntEnum

from .searchfilter import SearchFilter

class EnumFilter(SearchFilter):
    """
    Implements an argument parser for enum filters and logic to match
    ranges of enum values.
    """

    def __init__(self, *values, enum_type=IntEnum, name=None, format=None, orig=None):
        super().__init__(*values, name=name, format=format, orig=orig)

        if not isinstance(orig, EnumFilter):
            self.__enum_type = enum_type
        else:
            self.__enum_type = enum_type if enum_type is not None else orig.enum_type

    def _parse_value(self, value):
        try:
            return int(value)
        except ValueError:
            return getattr(self.__enum_type, value)
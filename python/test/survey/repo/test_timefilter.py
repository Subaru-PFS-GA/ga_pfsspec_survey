import os
from datetime import datetime
from dateutil.tz import tz
from unittest import TestCase

from pfs.ga.pfsspec.survey.repo import TimeFilter

class TestTimeFilter(TestCase):
    def test_init(self):
        d = TimeFilter(datetime(2024, 6, 1))
        self.assertEqual([datetime(2024, 6, 1)], d.values)

        d = TimeFilter((datetime(2024, 6, 1), datetime(2024, 6, 4)))
        self.assertEqual([(datetime(2024, 6, 1), datetime(2024, 6, 4))], d.values)

        d = TimeFilter(datetime(2024, 6, 1), datetime(2024, 6, 4))
        self.assertEqual([datetime(2024, 6, 1), datetime(2024, 6, 4)], d.values)

    def test_parse(self):
        filter = TimeFilter()

        filter.parse(['2024-01-02'])
        self.assertEqual([datetime(2024, 1, 2)], filter.values)

        filter.parse(['2024-01-02', '2025-03-04'])
        self.assertEqual([datetime(2024, 1, 2), datetime(2025, 3, 4)], filter.values)
        
        filter.parse(['2024-01-02-2025-03-04'])
        self.assertEqual([(datetime(2024, 1, 2), datetime(2025, 3, 4))], filter.values)

        filter.parse(['20250301T073809'])
        self.assertEqual([datetime(2025, 3, 1, 7, 38, 9)], filter.values)

        filter.parse(['20250301T073809Z'])
        self.assertEqual([datetime(2025, 3, 1, 7, 38, 9, tzinfo=tz.tzutc())], filter.values)
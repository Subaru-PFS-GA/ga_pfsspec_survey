import os
from datetime import date
from unittest import TestCase

from pfs.ga.pfsspec.survey.repo import DateFilter

class TestDateFilter(TestCase):
    def test_init(self):
        d = DateFilter(date(2024, 6, 1))
        self.assertEqual([date(2024, 6, 1)], d.values)

        d = DateFilter((date(2024, 6, 1), date(2024, 6, 4)))
        self.assertEqual([(date(2024, 6, 1), date(2024, 6, 4))], d.values)

        d = DateFilter(date(2024, 6, 1), date(2024, 6, 4))
        self.assertEqual([date(2024, 6, 1), date(2024, 6, 4)], d.values)

    def test_parse(self):
        filter = DateFilter()

        filter.parse(['20240102'])
        self.assertEqual([date(2024, 1, 2)], filter.values)

        filter.parse(['2024-01-02'])
        self.assertEqual([date(2024, 1, 2)], filter.values)

        filter.parse(['2024-01-02', '2025-03-04'])
        self.assertEqual([date(2024, 1, 2), date(2025, 3, 4)], filter.values)
        
        filter.parse(['2024-01-02-2025-03-04'])
        self.assertEqual([(date(2024, 1, 2), date(2025, 3, 4))], filter.values)
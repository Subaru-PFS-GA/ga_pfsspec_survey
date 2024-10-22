import os
from unittest import TestCase

from pfs.ga.pfsspec.survey.repo import IntFilter

class TestIntFilter(TestCase):
    def test_init(self):
        pass

    def test_parse(self):
        filter = IntFilter()

        filter.parse(['12345'])
        self.assertEqual([12345], filter.values)

        filter.parse(['12345', '23456'])
        self.assertEqual([12345, 23456], filter.values)
        
        filter.parse(['12345-12348'])
        self.assertEqual([(12345, 12348)], filter.values)

    def test_str(self):
        filter = IntFilter()
        
        filter.values = None
        self.assertEqual('', str(filter))

        filter.values = [12345]
        self.assertEqual('12345', str(filter))

        filter.values = [12345, 23456]
        self.assertEqual('12345 23456', str(filter))

        filter.values = [(12345, 12348)]
        self.assertEqual('12345-12348', str(filter))

    def test_repr(self):
        filter = IntFilter()
        
        filter.values = None
        self.assertEqual('IntFilter(None)', repr(filter))

        filter.values = [12345]
        self.assertEqual('IntFilter(12345)', repr(filter))

        filter.values = [12345, 23456]
        self.assertEqual('IntFilter(12345, 23456)', repr(filter))

        filter.values = [(12345, 12348)]
        self.assertEqual('IntFilter((12345, 12348))', repr(filter))
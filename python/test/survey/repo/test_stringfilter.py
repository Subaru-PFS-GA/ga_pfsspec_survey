import os
from unittest import TestCase

from pfs.ga.pfsspec.survey.repo import StringFilter

class TestStringFilter(TestCase):
    def test_init(self):
        pass

    def test_str(self):
        filter = StringFilter()
        
        filter.values = None
        self.assertEqual('', str(filter))

        filter.values = ['12345']
        self.assertEqual('12345', str(filter))

        filter.values = ['12345', '23456']
        self.assertEqual('12345 23456', str(filter))

        filter.values = [('12345', '12348')]
        self.assertEqual('12345-12348', str(filter))

    def test_repr(self):
        filter = StringFilter()
        
        filter.values = None
        self.assertEqual('StingFilter(None)', repr(filter))

        filter.values = ['12345']
        self.assertEqual('StringFilter(\'12345\')', repr(filter))

        filter.values = ['12345', '23456']
        self.assertEqual('StringFilter(\'12345\', \'23456\')', repr(filter))

        filter.values = [('12345', '12348')]
        self.assertEqual('StringFilter((\'12345\', \'12348\'))', repr(filter))

    def test_match(self):
        filter = StringFilter()

        filter.values = None
        self.assertTrue(filter.match('12345'))

        filter.values = ['12345']
        self.assertTrue(filter.match('12345'))
        self.assertFalse(filter.match('12346'))

        filter.values = ['12345', '23456']
        self.assertTrue(filter.match('12345'))
        self.assertTrue(filter.match('23456'))

        filter.values = ['123???456']
        self.assertFalse(filter.match('12345'))
        self.assertTrue(filter.match('123abc456'))

        filter.values = ['123*456']
        self.assertTrue(filter.match('123456'))
        self.assertTrue(filter.match('123abc456'))
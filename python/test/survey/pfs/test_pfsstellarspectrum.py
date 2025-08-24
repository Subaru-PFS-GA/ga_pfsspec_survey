import os
from datetime import date
from unittest import TestCase

from pfs.ga.pfsspec.survey.pfs import PfsStellarSpectrum

class TestPfsStellarSpectrum(TestCase):
    def test_copy(self):
        s = PfsStellarSpectrum()
        s.target = type('target', (), {'catId': 12345, 'objId': 0xabcdef})()
        s.identity = type('identity', (), {'visit': 42})()
        s.catid = 7
        s.spectrograph = 8
        s.fiberid = 9

        s2 = s.copy()
        self.assertIsInstance(s2, PfsStellarSpectrum)
        self.assertEqual(s2.target.catId, 12345)
        self.assertEqual(s2.target.objId, 0xabcdef)
        self.assertEqual(s2.identity.visit, 42)
        self.assertEqual(s2.catid, 7)
        self.assertEqual(s2.spectrograph, 8)
        self.assertEqual(s2.fiberid, 9)

import os
from datetime import date
from unittest import TestCase

from pfs.datamodel import *

from pfs.ga.pfsspec.survey.pfs.pfsspectrum import PfsSpectrum

class TestPfsSpectrum(TestCase):
    def test_get_mask_bits(self):
        s = PfsSpectrum()
        s.mask_flags = {
            0: 'BAD', 11: 'BAD_FIBERTRACE', 9: 'BAD_FLAT', 13: 'BAD_FLUXCAL',
            12: 'BAD_SKY', 3: 'CR', 5: 'DETECTED', 6: 'DETECTED_NEGATIVE',
            4: 'EDGE', 10: 'FIBERTRACE', 2: 'INTRP'
        }

        mask_bits = s.get_mask_bits(['BAD', 'BAD_FLUXCAL', 'DETECTED', 'INTRP'])
        self.assertEqual(mask_bits, 0b0010000000100101)



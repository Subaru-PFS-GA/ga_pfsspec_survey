import os
from astropy.io import fits

from test.pfs.ga.pfsspec.core import TestBase
from pfs.ga.pfsspec.survey.pfs.io import PfsSpectrumReader
from pfs.ga.pfsspec.survey.pfs.datamodel import *
from pfs.ga.pfsspec.survey.pfs import PfsStellarSpectrum

class TestPfsSpectrumReader(TestBase):
    def test_read_pfsFiberArray(self):
        filename = '/datascope/subaru/data/commissioning/rerun/run17/20240604/pfsSingle/10015/00001/1,1/pfsSingle-10015-00001-1,1-0000000000005d3e-111483.fits'
        pfsSingle = PfsSingle.readFits(filename)

        r = PfsSpectrumReader()
        s = PfsStellarSpectrum()
        r.read_from_pfsFiberArray(pfsSingle, s, wave_limits=[4000, 6000])

        self.assertEqual(s.id, 23870)
        self.assertEqual(s.catid, 10015)
        self.assertEqual(s.identity.catId, 10015)
        self.assertEqual(s.identity.objId, 23870)

    def test_read_from_pfsDesign(self):
        filename = '/datascope/subaru/data/commissioning/pfsConfig/2024-06-01/pfsConfig-0x6d832ca291636984-111483.fits'
        dir = os.path.dirname(filename)
        pfsConfig = PfsConfig.read(0x6d832ca291636984, 111483, dirName=dir)

        r = PfsSpectrumReader()
        s = PfsStellarSpectrum()
        r.read_from_pfsDesign(pfsConfig, s, index=1946)

        self.assertEqual(s.id, 23870)
        self.assertEqual(s.catid, 10015)
        self.assertEqual(s.identity.catId, 10015)
        self.assertEqual(s.identity.objId, 23870)

    def test_read_from_pfsFiberArraySet(self):
        filename = '/datascope/subaru/data/commissioning/rerun/run17/20240604/pfsMerged/2024-06-02/v111637/pfsMerged-111637.fits'
        pfsMerged = PfsMerged.readFits(filename)

        r = PfsSpectrumReader()
        s = PfsStellarSpectrum()
        r.read_from_pfsFiberArraySet(pfsMerged, s, index=1946, wave_limits=[4000, 6000])
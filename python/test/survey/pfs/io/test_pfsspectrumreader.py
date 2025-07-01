import os
from types import SimpleNamespace
from astropy.io import fits
import numpy as np

from test.pfs.ga.pfsspec.core import TestBase
from pfs.ga.pfsspec.survey.pfs.io import PfsSpectrumReader
from pfs.ga.pfsspec.survey.pfs.datamodel import *
from pfs.ga.pfsspec.survey.pfs import PfsStellarSpectrum

class TestPfsSpectrumReader(TestBase):
    def test_read_pfsFiberArray(self):
        filename = '/datascope/subaru/data/commissioning/gen2/rerun/run17/20240604/pfsSingle/10015/00001/1,1/pfsSingle-10015-00001-1,1-0000000000005d3e-111483.fits'
        pfsSingle = PfsSingle.readFits(filename)

        r = PfsSpectrumReader()
        s = PfsStellarSpectrum()
        r.read_from_pfsFiberArray(pfsSingle, s, wave_limits=[4000, 6000])

        self.assertEqual('catId=10015, objId=0000000000005d3e, visit=111483, arm=bmn', s.get_name())
        self.assertEqual(s.id, 23870)
        self.assertEqual(s.target.catId, 10015)
        self.assertEqual(s.target.objId, 23870)
        self.assertEqual(s.identity.visit, 111483)
        self.assertEqual(s.observations.num, 1)

    def test_read_from_pfsConfig(self):
        filename = '/datascope/subaru/data/commissioning/gen2/pfsConfig/2024-06-01/pfsConfig-0x6d832ca291636984-111483.fits'
        dir = os.path.dirname(filename)
        pfsConfig = PfsConfig.read(0x6d832ca291636984, 111483, dirName=dir)

        r = PfsSpectrumReader()
        s = PfsStellarSpectrum()
        r.read_from_pfsConfig(pfsConfig, s, index=1946)

        self.assertEqual('catId=10015, objId=0000000000005d3e, visit=111483, arm=bnm', s.get_name())
        self.assertEqual(s.id, 23870)
        self.assertEqual(s.catid, 10015)
        self.assertEqual(s.target.catId, 10015)
        self.assertEqual(s.target.objId, 23870)
        self.assertEqual(s.observations.num, 1)

    def test_read_from_pfsFiberArraySet(self):
        filename = '/datascope/subaru/data/commissioning/gen2/rerun/run17/20240604/pfsMerged/2024-06-02/v111637/pfsMerged-111637.fits'
        pfsMerged = PfsMerged.readFits(filename)

        r = PfsSpectrumReader()
        s = PfsStellarSpectrum()
        r.read_from_pfsFiberArraySet(pfsMerged, s, index=1946, wave_limits=[4000, 6000])

    def test_read_from_both(self):
        filename = '/datascope/subaru/data/commissioning/gen2/pfsConfig/2024-06-01/pfsConfig-0x6d832ca291636984-111483.fits'
        dir = os.path.dirname(filename)
        pfsConfig = PfsConfig.read(0x6d832ca291636984, 111483, dirName=dir)

        filename = '/datascope/subaru/data/commissioning/gen2/rerun/run17/20240604/pfsMerged/2024-06-01/v111483/pfsMerged-111483.fits'
        pfsMerged = PfsMerged.readFits(filename)

        r = PfsSpectrumReader()
        
        # Normal
        s = PfsStellarSpectrum()
        r.read_from_pfsFiberArraySet(pfsMerged, s, index=1946, wave_limits=[4000, 6000])
        r.read_from_pfsConfig(pfsConfig, s, index=1946)

        self.assertEqual(111483, s.identity.visit)
        self.assertEqual('bmn', s.identity.arm)
        self.assertEqual(4, s.identity.spectrograph)
        self.assertEqual(0x6d832ca291636984, s.identity.pfsDesignId)
        self.assertEqual("UNKNOWN", s.identity.obsTime)
        self.assertTrue(np.isnan(s.identity.expTime))

        # Opposite order
        s = PfsStellarSpectrum()
        r.read_from_pfsConfig(pfsConfig, s, index=1946)
        r.read_from_pfsFiberArraySet(pfsMerged, s, index=1946, wave_limits=[4000, 6000])
        
        self.assertEqual(111483, s.identity.visit)
        self.assertEqual('bnm', s.identity.arm)
        self.assertEqual(4, s.identity.spectrograph)
        self.assertEqual(0x6d832ca291636984, s.identity.pfsDesignId)
        self.assertEqual("UNKNOWN", s.identity.obsTime)
        self.assertTrue(np.isnan(s.identity.expTime))
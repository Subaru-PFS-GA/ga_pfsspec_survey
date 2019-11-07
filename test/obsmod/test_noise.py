import os
import numpy as np
from test.test_base import TestBase

from pfsspec.obsmod.error import Error

class TestNoise(TestBase):
    def test_read(self):
        filename = os.path.join(self.PFSSPEC_DATA_PATH, 'subaru/pfs/noise/sim8hr.dat')
        noise = Error()
        noise.read(filename)
        noise.plot()

        self.assertEqual((12288,), noise.wave.shape)
        self.assertEqual((12288,), noise.sigma.shape)

        self.save_fig()

    def test_resample(self):
        filename = os.path.join(self.PFSSPEC_DATA_PATH, 'subaru/pfs/noise/sim8hr.dat')
        noise = Error()
        noise.read(filename)
        noise.plot()

        nwave = np.linspace(3810, 12590, 3600)
        noise.resample(nwave)

        self.assertEqual((3600,), noise.wave.shape)
        self.assertEqual((3600,), noise.sigma.shape)

        self.save_fig()
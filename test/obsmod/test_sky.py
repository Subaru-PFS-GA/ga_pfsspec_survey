import os
import numpy as np
from test.test_base import TestBase

from pfsspec.obsmod.sky import Sky

class TestError(TestBase):
    def test_read(self):
        filename = os.path.join(self.PFSSPEC_DATA_PATH, 'sky/sdss.txt')
        sky = Sky()
        sky.read(filename)
        sky.plot()

        self.assertEqual((9999,), sky.wave.shape)
        self.assertEqual((9999,), sky.flux.shape)

        self.save_fig()
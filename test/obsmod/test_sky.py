import os
import numpy as np
from test.test_base import TestBase

from pfsspec.obsmod.sky import Sky

class TestError(TestBase):
    def test_read(self):
        filename = os.path.join(self.PFSSPEC_DATA_PATH, 'sky/mk_opt.dat')
        sky = Sky()
        sky.read(filename)
        sky.plot()

        self.assertEqual((2511,), sky.wave.shape)
        self.assertEqual((2511,), sky.flux.shape)

        self.save_fig()
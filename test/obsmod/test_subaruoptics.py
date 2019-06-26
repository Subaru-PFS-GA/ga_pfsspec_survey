from test.testbase import TestBase
import os

from pfsspec.obsmod.subaruoptics import SubaruOptics

class TestFilter(TestBase):
    def test_read(self):
        filename = os.path.join(self.PFSSPEC_DATA_PATH, 'subaru/telescope/subaru_m1_r_20190605.txt')
        mirror = SubaruOptics()
        mirror.read(filename)
        mirror.plot()

        self.assertEqual((582,), mirror.wave.shape)
        self.assertEqual((582,), mirror.throughput.shape)

        self.save_fig()

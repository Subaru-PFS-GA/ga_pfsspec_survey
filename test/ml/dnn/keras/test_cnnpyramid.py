import os
import numpy as np
from test.test_base import TestBase

from pfsspec.io.dataset import Dataset
from pfsspec.ml.dnn.keras.cnnpyramid import CnnPyramid

class TestCnnPyramid(TestBase):
    def test_train(self):
        dataset = Dataset()
        dataset.load(os.path.join(self.PFSSPEC_DATA_PATH, 'pfs_spec_test', 'sdss_test', 'dataset.dat'))

        input = dataset.flux
        labels = np.array(dataset.params['log_g'])

        model = CnnPyramid(levels=2)
        model.train(input, labels)
        model.predict(dataset.flux)


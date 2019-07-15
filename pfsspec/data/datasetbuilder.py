import sys
import logging
import pandas as pd

from pfsspec.parallel import srl_map, prll_map
from pfsspec.data.dataset import Dataset

class DatasetBuilder():
    def __init__(self, orig=None):
        if orig is not None:
            self.parallel = orig.parallel
            self.params = orig.params
            self.pipeline = orig.pipeline
        else:
            self.parallel = True
            self.params = None
            self.pipeline = None

    def get_spectrum_count(self):
        raise NotImplementedError()

    def get_wave_count(self):
        raise NotImplementedError()

    def create_dataset(self):
        self.dataset = Dataset()
        self.dataset.init_storage(self.get_wave_count(), self.get_spectrum_count())
        # This is used with surveys
        logging.info('Creating dataset with shapes {} {}.'.format(self.dataset.wave.shape, self.dataset.flux.shape))

    def process_item(self, i):
        raise NotImplementedError()

    def build(self):
        self.create_dataset()

        if self.parallel:
            spectra = prll_map(self.process_item, range(self.get_spectrum_count()), verbose=True)
        else:
            spectra = srl_map(self.process_item, range(self.get_spectrum_count()), verbose=True)

        for i in range(len(spectra)):
            self.dataset.flux[i, :] = spectra[i].flux

        if self.params is not None:
            self.dataset.params = self.params
        else:
            columns = spectra[0].get_param_names()
            data = []
            for p in columns:
                data.append([ getattr(s, p) for s in spectra ])

            self.dataset.params = pd.DataFrame(list(zip(data)), columns)

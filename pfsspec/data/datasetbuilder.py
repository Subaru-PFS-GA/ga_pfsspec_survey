import sys
import logging
import numpy as np
import pandas as pd

from pfsspec.parallel import srl_map, prll_map
from pfsspec.data.dataset import Dataset

class DatasetBuilder():
    def __init__(self, orig=None):
        if orig is not None:
            self.dataset = orig.dataset
            self.parallel = orig.parallel
            self.params = orig.params
            self.pipeline = orig.pipeline
        else:
            self.dataset = None
            self.parallel = True
            self.params = None
            self.pipeline = None

    def add_args(self, parser):
        pass

    def init_from_args(self, args):
        self.parallel = not args['debug']
        if not self.parallel:
            logging.info('Dataset builder running in sequential mode.')

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
            self.dataset.error[i, :] = spectra[i].flux_err

        if self.params is not None:
            self.dataset.params = self.params
        else:
            columns = spectra[0].get_param_names()
            names = []
            data = []
            for p in columns:
                v = getattr(spectra[0], p)
                # If parameter is an array, assume it's equal length and copy to
                # pandas as a set of columns instead of a single column
                if isinstance(v, np.ndarray):
                    if len(v.shape) > 1:
                        raise Exception('Can only serialize one-dimensional arrays')
                    for i in range(v.shape[0]):
                        names.append('{}_{}'.format(p, i))
                        data.append([getattr(s, p)[i] for s in spectra])
                else:
                    names.append(p)
                    data.append([getattr(s, p) for s in spectra])
            self.dataset.params = pd.DataFrame(list(zip(*data)), columns=names)
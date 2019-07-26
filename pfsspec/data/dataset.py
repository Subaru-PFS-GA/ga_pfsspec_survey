import logging
import numpy as np
import pandas as pd
import gzip, pickle

class Dataset():
    def __init__(self, orig=None):
        if orig is None:
            self.params = None
            self.wave = None
            self.flux = None
            self.error = None
        else:
            self.params = orig.params.copy()
            self.wave = orig.wave
            self.flux = orig.flux
            self.error = orig.error

    def init_storage(self, wcount, scount):
        self.wave = np.empty(wcount)
        self.flux = np.empty((scount, wcount))
        self.error = np.empty((scount, wcount))

    def save(self, filename, format='pickle'):
        logging.info("Saving dataset to file {}...".format(filename))

        if format == 'pickle':
            with gzip.open(filename, 'wb') as f:
                self.save_items(f)
        else:
            raise NotImplementedError()

        logging.info("Saved dataset.")

    def save_items(self, f):
        pickle.dump(self.params, f, protocol=4)
        pickle.dump(self.wave, f, protocol=4)
        pickle.dump(self.flux, f, protocol=4)
        pickle.dump(self.error, f, protocol=4)

    def save_items_h5(self, f):
        f.create_dataset()

    def load(self, filename):
        logging.info("Loading dataset from file {}...".format(filename))

        with gzip.open(filename, 'rb') as f:
            self.load_items(f)

        logging.info("Loaded dataset with shapes:")
        logging.info("  params:  {}".format(self.params.shape))
        logging.info("  wave:    {}".format(self.wave.shape))
        logging.info("  flux:    {}".format(self.flux.shape))
        logging.info("  columns: {}".format(self.params.columns))

    def load_items(self, f):
        self.params = pickle.load(f)
        self.wave = pickle.load(f)
        self.flux = pickle.load(f)
        self.error = pickle.load(f)

    def reset_index(self, df):
        df.index = pd.RangeIndex(len(df.index))

    def get_split_index(self, split_value):
        split_index = int((1 - split_value) *  self.flux.shape[0])
        return split_index

    def get_split_ranges(self, split_index):
        a_range = [i for i in range(0, split_index)]
        b_range = [i for i in range(split_index, self.flux.shape[0])]
        return a_range, b_range

    def split(self, split_value):
        a = Dataset()
        b = Dataset()

        split_index = self.get_split_index(split_value)
        a_range, b_range = self.get_split_ranges(split_index)

        a.params = self.params.iloc[a_range]
        self.reset_index(a.params)
        a.wave = self.wave
        a.flux = self.flux[a_range]
        a.error = self.error[a_range]

        b.params = self.params.iloc[b_range]
        self.reset_index(b.params)
        b.wave = self.wave
        b.flux = self.flux[b_range]
        b.error = self.error[b_range]

        return split_index, a, b

    def filter(self, f):
        a = Dataset()
        b = Dataset()

        a.params = self.params.ix[f]
        self.reset_index(a.params)
        a.wave = self.wave
        a.flux = self.flux[f]
        a.error = self.error[f]

        b.params = self.params.ix[~f]
        self.reset_index(b.params)
        b.wave = self.wave
        b.flux = self.flux[~f]
        b.error = self.error[~f]

        return a, b

    def merge(self, b):
        a = Dataset()

        a.params = pd.concat([self.params, b.params], axis=0)
        self.reset_index(a.params)
        a.wave = self.wave
        a.flux = np.concatenate([self.flux, b.flux], axis=0)
        a.error = np.concatenate([self.error, b.error], axis=0)

        return a

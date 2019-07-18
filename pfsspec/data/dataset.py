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
        else:
            self.params = orig.params
            self.wave = orig.wave
            self.flux = orig.flux

    def init_storage(self, wcount, scount):
        self.wave = np.empty(wcount)
        self.flux = np.empty((scount, wcount))

    def save(self, filename):
        logging.info("Saving dataset to file {}...".format(filename))

        with gzip.open(filename, 'wb') as f:
            self.save_items(f)

        logging.info("Saved dataset.")

    def save_items(self, f):
        pickle.dump(self.params, f)
        pickle.dump(self.wave, f)
        pickle.dump(self.flux, f)

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

        b.params = self.params.iloc[b_range]
        self.reset_index(b.params)
        b.wave = self.wave
        b.flux = self.flux[b_range]

        return split_index, a, b

    def filter(self, f):
        a = Dataset()
        b = Dataset()

        a.params = self.params.ix[f]
        self.reset_index(a.params)
        a.wave = self.wave
        a.flux = self.flux[f]

        b.params = self.params.ix[~f]
        self.reset_index(b.params)
        b.wave = self.wave
        b.flux = self.flux[~f]

        return a, b

    def merge(self, b):
        a = Dataset()

        a.params = pd.concat([self.params, b.params], axis=0)
        self.reset_index(a.params)
        a.wave = self.wave
        a.flux = np.concatenate([self.flux, b.flux], axis=0)

        return a

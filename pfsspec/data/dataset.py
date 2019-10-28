import logging
import numpy as np
import pandas as pd

from pfsspec.pfsobject import PfsObject

class Dataset(PfsObject):
    def __init__(self, orig=None):
        self.top = None

        if orig is None:
            self.params = None
            self.wave = None
            self.flux = None
            self.error = None
            self.U = None
            self.S = None
            self.V = None
            self.PC = None
        else:
            self.params = orig.params.copy()
            self.wave = orig.wave
            self.flux = orig.flux
            self.error = orig.error
            self.U = None
            self.S = None
            self.V = None
            self.PC = None

    def init_storage(self, wcount, scount):
        self.wave = np.empty(wcount)
        self.flux = np.empty((scount, wcount))
        self.error = np.empty((scount, wcount))

    def save_items(self):
        self.save_item('params', self.params)
        self.save_item('wave', self.wave)
        self.save_item('flux', self.flux)
        self.save_item('error', self.error)

    def load(self, filename, format='pickle'):
        super(Dataset, self).load(filename, format)

        logging.info("Loaded dataset with shapes:")
        logging.info("  params:  {}".format(self.params.shape))
        logging.info("  wave:    {}".format(self.wave.shape))
        logging.info("  flux:    {}".format(self.flux.shape))
        logging.info("  columns: {}".format(self.params.columns))

    def load_items(self, slice=None):
        self.params = self.load_item('params', pd.DataFrame)
        self.wave = self.load_item('wave', np.ndarray)
        self.flux = self.load_item('flux', np.ndarray)
        self.error = self.load_item('error', np.ndarray)

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
        if self.error is not None:
            a.error = self.error[a_range]

        b.params = self.params.iloc[b_range]
        self.reset_index(b.params)
        b.wave = self.wave
        b.flux = self.flux[b_range]
        if self.error is not None:
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

    def run_pca(self, truncate=None):
        C = np.dot(self.flux.transpose(), self.flux)
        self.U, self.S, self.V = np.linalg.svd(C)

        if truncate is not None:
            self.PC = np.dot(self.flux, self.U[:, 0:truncate])
        else:
            self.PC = np.dot(self.flux, self.U[:, :])

        self.wave = np.arange(self.PC.shape[1])
        self.flux = self.PC
        self.error = np.zeros(self.flux.shape)

    def save_pca(self, filename, format='pickle'):
        # TODO: review this and compare with PfsObject.save
        logging.info("Saving PCA eigensystem to file {}...".format(filename))

        self.filename = filename
        self.fileformat = format
        self.save_pca_items()

        logging.info("Saved PCA eigensystem.")

    def save_pca_items(self):
        self.save_item('U', self.U)
        self.save_item('S', self.S)
        self.save_item('V', self.V)

    def load_pca(self, filename, format='pickle'):
        # TODO: review this and compare with PfsObject.load
        #       Probably pass a callback to PfsObject.load instead of load_items
        logging.info("Loading PCA eigensystem from file {}...".format(filename))

        self.filename = filename
        self.fileformat = format
        self.load_pca_items()

        logging.info("Loaded PCA eigensystem.")

    def load_pca_items(self):
        self.U = self.load_item('U', np.ndarray)
        self.S = self.load_item('S', np.ndarray)
        self.V = self.load_item('V', np.ndarray)


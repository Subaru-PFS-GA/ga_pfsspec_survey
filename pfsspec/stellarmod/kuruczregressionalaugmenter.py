import os
import numpy as np

from pfsspec.util import *
from pfsspec.data.regressionaldatasetaugmenter import RegressionalDatasetAugmenter
from pfsspec.stellarmod.kuruczaugmenter import KuruczAugmenter

class KuruczRegressionalAugmenter(RegressionalDatasetAugmenter, KuruczAugmenter):
    def __init__(self):
        RegressionalDatasetAugmenter.__init__(self)
        KuruczAugmenter.__init__(self)

    @classmethod
    def from_dataset(cls, dataset, labels, coeffs, weight=None, batch_size=1, shuffle=True, seed=None):
        d = super(KuruczRegressionalAugmenter, cls).from_dataset(dataset, labels, coeffs, weight,
                                  batch_size=batch_size, shuffle=shuffle, seed=seed)
        return d

    def add_args(self, parser):
        RegressionalDatasetAugmenter.add_args(self, parser)
        KuruczAugmenter.add_args(self, parser)

    def init_from_args(self, args):
        RegressionalDatasetAugmenter.init_from_args(self, args)
        KuruczAugmenter.init_from_args(self, args)

    def augment_batch(self, idx):
        flux, labels, weight = RegressionalDatasetAugmenter.augment_batch(self, idx)
        flux, labels, weight = KuruczAugmenter.augment_batch(self, self.dataset, idx, flux, labels, weight)
        return flux, labels, weight
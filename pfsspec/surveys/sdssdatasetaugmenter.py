import numpy as np

from pfsspec.ml.dnn.keras.kerasdatagenerator import KerasDataGenerator

class SdssDatasetAugmenter(KerasDataGenerator):
    def __init__(self, dataset, labels, coeffs, batch_size=1, shuffle=True, seed=0):
        self.dataset = dataset
        self.labels = labels
        self.coeffs = coeffs

        input_shape = self.dataset.flux.shape
        labels_shape = (len(self.labels),)
        super(SdssDatasetAugmenter, self).__init__(input_shape, labels_shape,
                                                   batch_size=batch_size, shuffle=shuffle, seed=seed)

        self.include_wave = False
        self.multiplicative_bias = False
        self.additive_bias = False

    def next_batch(self, batch_index):
        if self.batch_size * (batch_index + 1) > self.input_shape[0]:
            bs = self.input_shape[0] % self.batch_size
        else:
            bs = self.batch_size

        flux = np.array(self.dataset.flux[self.index[batch_index * self.batch_size:batch_index * self.batch_size + bs]], copy=True, dtype=np.float)
        labels = np.array(self.dataset.params[self.labels].iloc[self.index[batch_index * self.batch_size:batch_index * self.batch_size + bs]], copy=True, dtype=np.float)

        flux, labels = self.augment_batch(self.dataset.wave, flux, labels)
        labels /= self.coeffs

        if self.include_wave:
            nflux = np.zeros((bs, self.dataset.flux.shape[1], 2))
            nflux[:, :, 0] = flux
            nflux[:, :, 1] = self.dataset.wave
            flux = nflux

        return flux, labels

    def augment_batch(self, wave, flux, labels):

        if self.multiplicative_bias:
            bias = np.random.uniform(0.8, 1.2, (flux.shape[0], 1))
            flux = flux * bias

        if self.additive_bias:
            bias = np.random.normal(0, 1.0, (flux.shape[0], 1))
            flux = flux + bias

        return flux, labels

import numpy as np

from pfsspec.ml.dnn.keras.kerasdatagenerator import KerasDataGenerator

class SdssAugmenter(KerasDataGenerator):
    def __init__(self, dataset, labels, coeffs, batch_size=1, shuffle=True, seed=0):
        self.dataset = dataset
        self.labels = labels
        self.coeffs = coeffs

        input_shape = self.dataset.flux.shape
        labels_shape = (len(self.labels),)
        super(SdssAugmenter, self).__init__(input_shape, labels_shape,
                                            batch_size=batch_size, shuffle=shuffle, seed=seed)

        self.include_wave = False
        self.multiplicative_bias = False
        self.additive_bias = False

    def next_batch(self, batch_index):
        bs = self.next_batch_size(batch_index)

        input = np.array(self.dataset.flux[self.index[batch_index * self.batch_size:batch_index * self.batch_size + bs]], copy=True, dtype=np.float)
        output = np.array(self.dataset.params[self.labels].iloc[self.index[batch_index * self.batch_size:batch_index * self.batch_size + bs]], copy=True, dtype=np.float)

        input, output = self.augment_batch(self.dataset.wave, input, output)

        if self.include_wave:
            nflux = np.zeros((bs, self.dataset.flux.shape[1], 2))
            nflux[:, :, 0] = input
            nflux[:, :, 1] = self.dataset.wave
            input = nflux

        return input, output

    def scale_output(self, output):
        return output / self.coeffs

    def rescale_output(self, output):
        return output * self.coeffs

    def augment_batch(self, wave, flux, labels):
        if self.multiplicative_bias:
            bias = np.random.uniform(0.8, 1.2, (flux.shape[0], 1))
            flux = flux * bias
        if self.additive_bias:
            bias = np.random.normal(0, 1.0, (flux.shape[0], 1))
            flux = flux + bias
        return flux, labels

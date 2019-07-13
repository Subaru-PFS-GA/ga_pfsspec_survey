import numpy as np

from pfsspec.data.datasetaugmenter import DatasetAugmenter

class SdssAugmenter(DatasetAugmenter):
    def __init__(self, dataset, labels, coeffs, batch_size=1, shuffle=True, seed=0):
        input_shape = dataset.flux.shape
        output_shape = (len(labels),)
        super(SdssAugmenter, self).__init__(dataset, labels, coeffs,
                                            input_shape, output_shape,
                                            batch_size=batch_size, shuffle=shuffle, seed=seed)

        self.include_wave = False
        self.multiplicative_bias = False
        self.additive_bias = False

    def scale_output(self, output):
        return output / self.coeffs

    def rescale_output(self, output):
        return output * self.coeffs

    def augment_batch(self, batch_index):
        flux = np.array(self.dataset.flux[batch_index], copy=True, dtype=np.float)
        labels = np.array(self.dataset.params[self.labels].iloc[batch_index], copy=True, dtype=np.float)

        if self.multiplicative_bias:
            bias = np.random.uniform(0.8, 1.2, (flux.shape[0], 1))
            flux = flux * bias
        if self.additive_bias:
            bias = np.random.normal(0, 1.0, (flux.shape[0], 1))
            flux = flux + bias

        if self.include_wave:
            nflux = np.zeros((len(batch_index), self.dataset.flux.shape[1], 2))
            nflux[:, :, 0] = flux
            nflux[:, :, 1] = self.dataset.wave
            flux = nflux

        return flux, labels

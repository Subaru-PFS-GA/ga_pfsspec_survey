import os
import sys

import pfs.ga.pfsspec.core.util as util
from pfs.ga.pfsspec.core.util import SmartParallel
from pfs.ga.pfsspec.core.io import Importer
from ..survey import Survey

class SurveyReader(Importer):
    """
    Implements function to read spectra of a survey.
    """

    def __init__(self, orig=None):
        super(SurveyReader, self).__init__(orig=orig)

        if isinstance(orig, SurveyReader):
            self.outdir = orig.outdir
        else:
            self.outdir = None

    def add_args(self, parser, config):
        super().add_args(parser, config)

    def init_from_args(self, config, args):
        super().init_from_args(config, args)

    def open_data(self, args, indir, outdir):
        fn = os.path.join(outdir, 'spectra.dat')

        self.outdir = outdir
        self.survey = self.create_survey()
        self.survey.filename = fn
        self.survey.fileformat = 'pickle'

    def save_data(self, args, output_path):
        self.survey.save()

    def create_survey(self):
        raise NotImplementedError()

    def create_spectrum_reader(self):
        raise NotImplementedError()

    def load_spectrum(self, index, row):
        return self.reader.load_spectrum(index, row)

    def process_item(self, ix_row):
        index, row = ix_row
        try:
            return self.load_spectrum(index, row)
        except Exception as e:
            self.logger.error(e)
            return None

    def store_item(self, ix_row, spec):
        # TODO: When optimizing memory use to process larger surveys,
        #       implement this function similarly to DatasetBuilder.store_item
        raise NotImplementedError()

    def load_survey(self, params):
        self.survey.params = params
        self.survey.spectra = []

        # TODO: this requires loading everything into memory
        #       consider redesigning the storage and read the spectra on
        #       multiple threads instead

        rows = [(index, row) for index, row in params.iterrows()]
        with SmartParallel(verbose=self.verbose, parallel=self.parallel, threads=self.threads) as p:
            self.survey.spectra = [r for r in p.map(self.process_item, rows)]
        
        # In case errors happened we get Nones
        self.survey.spectra = list(filter(lambda s: s is not None, self.survey.spectra))
        
        # Parallel will likely shuffle the spectra    
        self.survey.spectra.sort(key=lambda s: s.index)

    def run(self):
        raise NotImplementedError()

    def execute_notebooks(self, script):
        pass
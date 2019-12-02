import sys

from pfsspec.data.spectrumreader import SpectrumReader
from pfsspec.surveys.survey import Survey
from pfsspec.parallel import SmartParallel

class SurveySpectrumReader(SpectrumReader):
    def __init__(self):
        super(SurveySpectrumReader, self).__init__()

    def load_spectrum(self, row):
        raise NotImplementedError()

    def load_spectrum_wrapper(self, row):
        try:
            return self.load_spectrum(row)
        except Exception as e:
            print(e, file=sys.stderr)   # TODO
            return None

    def load_survey(self, params):
        survey = Survey()
        survey.params = params
        survey.spectra = []

        # TODO: rewrite to SmartParallel
        raise NotImplementedError()
        #rows = [rows for index, rows in params.iterrows()]
        #q, rng = prll_map(None, self.load_spectrum_wrapper, rows, verbose=True)
        ## TODO: test
        #survey.spectra = [q.get()[1] for x in rng]

        return survey
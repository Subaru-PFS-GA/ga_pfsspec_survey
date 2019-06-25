from pfsspec.io.spectrumreader import SpectrumReader
from pfsspec.surveys.survey import Survey
from pfsspec.parallel import prll_map

class SurveySpectrumReader(SpectrumReader):
    def __init__(self):
        super(SurveySpectrumReader, self).__init__()

    def load_spectrum(self, row):
        raise NotImplementedError()

    def load_survey(self, params):
        survey = Survey()
        survey.params = params
        survey.spectra = []

        rows = [rows for index, rows in params.iterrows()]
        survey.spectra = prll_map(self.load_spectrum, rows, verbose=True)

        return survey
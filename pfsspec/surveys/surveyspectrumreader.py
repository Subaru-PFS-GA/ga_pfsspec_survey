import sys
import click

from pfsspec.io.spectrumreader import SpectrumReader
from pfsspec.surveys.survey import Survey

class SurveySpectrumReader(SpectrumReader):
    def __init__(self):
        super(SurveySpectrumReader, self).__init__()

    def load_spectrum(self, survey, index, row):
        raise NotImplementedError()

    def load_survey(self, params):
        survey = Survey()
        survey.params = params
        survey.spectra = []

        with click.progressbar(params.iterrows(), file=sys.stderr, length=len(params)) as bar:
            for index, row in bar:
                spec = self.load_spectrum(index, row)
                survey.spectra.append(spec)

        return survey
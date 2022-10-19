import os
from pfs.ga.pfsspec.survey.xsl.io.xslsurveyreader import XslSurveyReader

from test.pfs.ga.pfsspec.core import TestBase
from pfs.ga.pfsspec.survey.xsl.io import XslSpectrumReader

class XslSurveyReaderTest(TestBase):
    def test_read(self):
        reader = XslSurveyReader()
        reader.indir = '/datascope/subaru/data/catalogs/xshooter'
        survey = reader.run()

        survey.save('/datascope/subaru/data/catalogs/xshooter/xsl.dat', format='pickle')


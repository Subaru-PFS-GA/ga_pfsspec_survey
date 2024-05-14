import os
import sys

import pfs.ga.pfsspec.core.util as util
from pfs.ga.pfsspec.core.util import SmartParallel
from pfs.ga.pfsspec.core.io import Downloader
from ..survey import Survey

class SurveyDownloader(Downloader):
    """
    Implements function to read spectra of a survey.
    """

    def __init__(self, orig=None):
        super().__init__(orig=orig)

        if not isinstance(orig, Downloader):
            self.outdir = None
        else:
            self.outdir = orig.outdir

    def add_subparsers(self, configurations, parser):
        return None

    def add_args(self, parser, config):
        super().add_args(parser, config)

    def init_from_args(self, script, config, args):
        super().init_from_args(script, config, args)

    def run(self):
        raise NotImplementedError()

    def execute_notebooks(self, script):
        pass
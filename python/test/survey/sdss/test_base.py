import os
from unittest import TestCase
import matplotlib.pyplot as plt

# from pfsspec.data.dataset import Dataset
# from pfsspec.data.arraygrid import ArrayGrid
# from pfsspec.stellarmod.modelgrid import ModelGrid
# from pfsspec.stellarmod.kuruczgrid import KuruczGrid
# from pfsspec.stellarmod.bosz import Bosz
# from pfsspec.obsmod.filter import Filter

# TODO: inherit from core.TestBase
class TestBase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestBase, cls)
        cls.PFSSPEC_SDSS_DATA_PATH = os.environ['PFSSPEC_SDSS_DATA'].strip('"') if 'PFSSPEC_SDSS_DATA' in os.environ else None
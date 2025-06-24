import os
from datetime import date
from unittest import TestCase

from pfs.ga.pfsspec.survey.pfs.datamodel import *
from pfs.ga.pfsspec.survey.repo import ButlerRepo
from pfs.ga.pfsspec.survey.pfs import PfsGen3Repo, PfsGen3ButlerConfig

class TestPfsGen3Repo_Butler(TestCase):

    def get_test_repo(self):
        return PfsGen3Repo(repo_type=ButlerRepo, config=PfsGen3ButlerConfig)

    def test_init(self):
        repo = self.get_test_repo()

    def test_find_product(self):
        repo = self.get_test_repo()

        files, ids = repo.find_product(PfsConfig)
        self.assertTrue(len(files) > 0)
        self.assertEqual(len(files), len(ids.pfs_design_id))
        self.assertEqual(len(files), len(ids.visit))
        self.assertEqual(len(files), len(ids.date))

    def test_locate_product(self):
        repo = self.get_test_repo()

        file, id = repo.locate_product(PfsConfig, visit=122794)

    def test_load_product(self):
        repo = self.get_test_repo()

        file, id = repo.locate_product(PfsConfig, visit=122794)
        pfsConfig = repo.load_product(PfsConfig, identity=id)

    def test_find_objects(self):
        repo = self.get_test_repo()

        # Find a bunch or outer disk science targets
        ids = repo.find_objects(visit=[(122794, 122799)], catId=10092)

        # Get observations of a specific object
        ids = repo.find_objects(visit=[(122794, 122799)], objId=154931150335344425)
        pass
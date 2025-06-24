import os
from datetime import date
from unittest import TestCase

from pfs.ga.pfsspec.survey.pfs.datamodel import *
from pfs.ga.pfsspec.survey.repo import FileSystemRepo
from pfs.ga.pfsspec.survey.pfs import PfsGen3Repo, PfsGen3FileSystemConfig

class TestPfsGen3Repo_FileSystem(TestCase):

    def get_test_repo(self):
        return PfsGen3Repo(repo_type=FileSystemRepo, config=PfsGen3FileSystemConfig)

    def test_init(self):
        repo = self.get_test_repo()

    def test_parse_product_identity(self):
        repo = self.get_test_repo()

        identity = repo.parse_product_identity(PfsDesign, 'pfsDesign-0x6d832ca291636984.fits')
        self.assertEqual(0x6d832ca291636984, identity.pfs_design_id)

    def test_find_product(self):
        repo = self.get_test_repo()

        files, ids = repo.find_product(PfsConfig)
        self.assertTrue(len(files) > 0)
        self.assertEqual(len(files), len(ids.pfs_design_id))
        self.assertEqual(len(files), len(ids.visit))
        self.assertEqual(len(files), len(ids.date))
        
    def test_find_objects(self):
        repo = self.get_test_repo()

        # Find a bunch or outer disk science targets
        ids = repo.find_objects(visit=[(120001, 120008)], catId=10088)

        # Get observations of a specific object
        ids = repo.find_objects(visit=[(120001, 120008)], objId=154931150335344425)
        pass
import os
from datetime import date
from unittest import TestCase

from pfs.datamodel import *
from pfs.ga.pfsspec.survey.pfs import PfsGen3FileSystemRepo

class TestPfsGen3FileSystemRepo(TestCase):

    def get_test_repo(self):
        return PfsGen3FileSystemRepo()

    def test_init(self):
        repo = self.get_test_repo()

    def test_parse_product_identity(self):
        repo = self.get_test_repo()

        identity = repo.parse_product_identity(PfsDesign, 'pfsDesign-0x6d832ca291636984.fits')
        self.assertEqual(0x6d832ca291636984, identity.pfsDesignId)

    def test_find_product(self):
        repo = self.get_test_repo()

        files, ids = repo.find_product(PfsConfig)
        self.assertTrue(len(files) > 0)
        # self.assertEqual(len(files), len(ids.pfsDesignId))
        self.assertEqual(len(files), len(ids.visit))
        self.assertEqual(len(files), len(ids.date))
        
    def test_find_object(self):
        repo = self.get_test_repo()

        # Find a bunch or outer disk science targets
        ids = repo.find_object(visit=[(120001, 120008)], catId=10088)

        # Get observations of a specific object
        ids = repo.find_object(visit=[(120001, 120008)], objId=154931150335344425)
        pass
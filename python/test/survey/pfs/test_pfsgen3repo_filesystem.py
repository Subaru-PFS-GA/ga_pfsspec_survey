from unittest import TestCase
from types import SimpleNamespace

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

    def test_locate_product(self):
        repo = self.get_test_repo()

        # Locate a specific product by visit
        file, id = repo.locate_product(PfsCalibrated, visit=123418)

        # Locate a specific container product with subproduct
        file, id = repo.locate_product((PfsCalibrated, PfsSingle), visit=123418)

    def test_find_product(self):
        repo = self.get_test_repo()

        files, ids = repo.find_product(PfsConfig)
        self.assertTrue(len(files) > 0)
        self.assertEqual(len(files), len(ids.pfs_design_id))
        self.assertEqual(len(files), len(ids.visit))
        self.assertEqual(len(files), len(ids.date))

    def test_load_product(self):
        repo = self.get_test_repo()

        # Load a specific product by visit
        file, id = repo.locate_product(PfsConfig, visit=122794)
        pfsConfig, id, file = repo.load_product(PfsConfig, identity=id)

        file, id = repo.locate_product(PfsCalibrated, visit=122794)
        pfsCalibrated, id, file = repo.load_product(PfsCalibrated, identity=id)

    def test_load_products_from_container(self):
        repo = self.get_test_repo()

        # Load a specific subproduct within a container product
        id = SimpleNamespace(visit=122794, objId=25769835249)
        [ (pfsSingle, id, file) ] = repo.load_products_from_container(*(PfsCalibrated, PfsSingle), identity=id)

        assert isinstance(pfsSingle, PfsSingle)
        assert isinstance(id, SimpleNamespace)
        assert file is not None

        # Load a container product and extract sub-products that match the specified filters
        id = SimpleNamespace(visit=122794)
        data = repo.load_products_from_container(*(PfsCalibrated, PfsSingle), identity=id)
        
        assert isinstance(data, list)
        assert len(data) > 1
        assert isinstance(data[0][0], PfsSingle)
        assert isinstance(data[0][1], SimpleNamespace)
        assert data[0][2] is not None
        
    def test_find_objects(self):
        repo = self.get_test_repo()

        # Find a bunch or outer disk science targets
        ids = repo.find_objects(visit=[(120001, 120008)], catId=10088)

        # Get observations of a specific object
        ids = repo.find_objects(visit=[(120001, 120008)], objId=154931150335344425)
        pass
import os
from datetime import date
from unittest import TestCase

from pfs.datamodel import *

from pfs.ga.pfsspec.survey.repo import FileSystemRepo
from pfs.ga.pfsspec.survey.pfs import PfsFileSystemConfig

class TestFileSystemRepo(TestCase):

    # TODO: this is obsolete

    def get_test_repo(self):
        return FileSystemRepo(PfsFileSystemConfig)

    def test_init(self):
        repo = self.get_test_repo()

    def test_parse_product_identity(self):
        repo = self.get_test_repo()

        identity = repo.parse_product_identity(PfsDesign, 'pfsDesign-0x6d832ca291636984.fits')
        self.assertEqual(0x6d832ca291636984, identity.pfsDesignId)


        identity = repo.parse_product_identity(PfsConfig, 'pfsConfig-0x6d832ca291636984-111483.fits')
        self.assertEqual(111483, identity.visit)
        self.assertEqual(0x6d832ca291636984, identity.pfsDesignId)
        self.assertFalse(hasattr(identity, 'date'))

        identity = repo.parse_product_identity(PfsConfig, '2024-06-01/pfsConfig-0x6d832ca291636984-111483.fits')
        self.assertEqual(111483, identity.visit)
        self.assertEqual(0x6d832ca291636984, identity.pfsDesignId)
        self.assertEqual(date(2024, 6, 1), identity.date)


        identity = repo.parse_product_identity(PfsSingle, 'pfsSingle-10015-00001-1,1-0000000000005d48-111317.fits')
        self.assertEqual(0x5d48, identity.objId)
        self.assertEqual(111317, identity.visit)
        self.assertEqual(10015, identity.catId)
        self.assertEqual(1, identity.tract)
        self.assertEqual('1,1', identity.patch)

    def test_find_product(self):
        repo = self.get_test_repo()

        files, ids = repo.find_product(PfsDesign)
        self.assertTrue(len(files) > 0)
        self.assertEqual(len(files), len(ids.pfsDesignId))


        files, ids = repo.find_product(PfsConfig)
        self.assertTrue(len(files) > 0)
        self.assertEqual(len(files), len(ids.pfsDesignId))
        self.assertEqual(len(files), len(ids.visit))
        self.assertEqual(len(files), len(ids.date))

        files, ids = repo.find_product(PfsConfig, date=(date(2024, 6, 1), date(2024, 6, 4)))
        self.assertTrue(len(files) > 0)
        self.assertEqual(len(files), len(ids.pfsDesignId))
        self.assertEqual(len(files), len(ids.visit))
        self.assertEqual(len(files), len(ids.date))

        files, ids = repo.find_product(PfsConfig, visit=111483)
        self.assertTrue(len(files) > 0)
        self.assertEqual(111483, ids.visit[0])

        files, ids = repo.find_product(PfsConfig, pfsDesignId=0x6d832ca291636984)
        self.assertTrue(len(files) > 0)


        files, ids = repo.find_product(PfsSingle, catId=10015, visit=111317)
        self.assertTrue(len(files) > 0)

        files, ids = repo.find_product(PfsSingle, catId=10015, visit=[111317, 111318])
        self.assertTrue(len(files) > 0)

        files, ids = repo.find_product(PfsSingle, catId=10015, visit=(111317, 111318))
        self.assertTrue(len(files) > 0)

    def test_locate_product(self):
        repo = self.get_test_repo()

        file, id = repo.locate_product(PfsDesign, pfsDesignId=0x6d832ca291636984)
        self.assertIsNotNone(file)
        self.assertEqual(0x6d832ca291636984, id.pfsDesignId)


        files = repo.locate_product(PfsConfig, visit=111636, pfsDesignId=0x6d832ca291636984)
        files = repo.locate_product(PfsConfig, visit=111636)

        # More than one file matching
        self.failureException(
            FileNotFoundError,
            lambda _: repo.locate_product(PfsConfig, pfsDesignId=0x6d832ca291636984))

        # No file matching
        self.failureException(
            FileNotFoundError,
            lambda _: repo.locate_product(PfsConfig, visit=111636, pfsDesignId=0x6d832ca291636985))


        file, identity = repo.locate_product(PfsSingle, catId=10015, tract=1, patch='1,1', objId=0x5d48, visit=111317)
        self.assertIsNotNone(file)

    def test_load_product(self):
        repo = self.get_test_repo()

        repo.variables['rerundir'] = 'run17/20240604'
        filename, identity = repo.locate_product(PfsDesign, pfsDesignId=0x6d832ca291636984)

        pfsDesign = repo.load_product(PfsDesign, filename=filename)
        pfsDesign = repo.load_product(PfsDesign, identity=identity)

        #

        filename, identity = repo.locate_product(PfsConfig, visit=111483)
        
        pfsConfig = repo.load_product(PfsConfig, filename=filename)
        pfsConfig = repo.load_product(PfsConfig, identity=identity)

        #

        repo.variables['rerundir'] = 'run08'
        filename, identity = repo.locate_product(PfsArm, visit=83249, arm='r', spectrograph=1)

        pfsArm = repo.load_product(PfsArm, filename=filename)
        pfsArm = repo.load_product(PfsArm, identity=identity)

        #

        repo.variables['rerundir'] = 'run08'
        filename, identity = repo.locate_product(PfsMerged, visit=83245)

        pfsMerged = repo.load_product(PfsMerged, filename=filename)
        pfsMerged = repo.load_product(PfsMerged, identity=identity)

        #

        repo.variables['rerundir'] = 'run17/20240604'
        filename, identity = repo.locate_product(PfsSingle, catId=10015, tract=1, patch='1,1', objId=0x5d48, visit=111317)

        pfsSingle = repo.load_product(PfsSingle, filename=filename)
        pfsSingle = repo.load_product(PfsSingle, identity=identity)
        
    def test_get_identity(self):
        repo = self.get_test_repo()

        repo.variables['rerundir'] = 'run17/20240604'
        filename, identity = repo.locate_product(PfsDesign, pfsDesignId=0x6d832ca291636984)
        pfsDesign, _, _ = repo.load_product(PfsDesign, filename=filename)

        identity = repo.get_identity(pfsDesign)
        self.assertEqual(pfsDesign.pfsDesignId, identity.pfsDesignId)

        #

        filename, identity = repo.locate_product(PfsConfig, visit=111483)        
        pfsConfig, _, _ = repo.load_product(PfsConfig, filename=filename)

        identity = repo.get_identity(pfsConfig)
        self.assertEqual(pfsConfig.pfsDesignId, identity.pfsDesignId)
        self.assertEqual(pfsConfig.visit, identity.visit)

        #

        repo.variables['rerundir'] = 'run08'
        filename, identity = repo.locate_product(PfsArm, visit=83249, arm='r', spectrograph=1)
        pfsArm, _, _ = repo.load_product(PfsArm, filename=filename)

        identity = repo.get_identity(pfsArm)
        self.assertEqual(pfsArm.identity.visit, identity.visit)
        self.assertEqual(pfsArm.identity.arm, identity.arm)
        self.assertEqual(pfsArm.identity.spectrograph, identity.spectrograph)

        #

        repo.variables['rerundir'] = 'run08'
        filename, identity = repo.locate_product(PfsMerged, visit=83245)
        pfsMerged, _, _ = repo.load_product(PfsMerged, filename=filename)

        identity = repo.get_identity(pfsMerged)
        self.assertEqual(pfsMerged.identity.visit, identity.visit)
        # TODO self.assertEqual(???, identity.date)

        #

        repo.variables['rerundir'] = 'run17/20240604'
        filename, identity = repo.locate_product(PfsSingle, catId=10015, tract=1, patch='1,1', objId=0x5d48, visit=111317)
        pfsSingle, _ , _ = repo.load_product(PfsSingle, filename=filename)

        identity = repo.get_identity(pfsSingle)
        self.assertEqual(pfsSingle.target.catId, identity.catId)
        self.assertEqual(pfsSingle.target.tract, identity.tract)
        self.assertEqual(pfsSingle.target.patch, identity.patch)
        self.assertEqual(pfsSingle.target.objId, identity.objId)
        self.assertEqual(pfsSingle.observations.visit[0], identity.visit)

import os
from datetime import date
from unittest import TestCase

from pfs.datamodel import *

from pfs.ga.pfsspec.survey.repo import FileSystemRepo
from pfs.ga.pfsspec.survey.pfs import PfsFileSystemConfig

class TestFileSystemConnector(TestCase):

    def get_test_connector(self):
        return FileSystemRepo(PfsFileSystemConfig)

    def test_init(self):
        connector = self.get_test_connector()

    def test_parse_product_identity(self):
        connector = self.get_test_connector()

        identity = connector.parse_product_identity(PfsDesign, 'pfsDesign-0x6d832ca291636984.fits')
        self.assertEqual(0x6d832ca291636984, identity.pfsDesignId)


        identity = connector.parse_product_identity(PfsConfig, 'pfsConfig-0x6d832ca291636984-111483.fits')
        self.assertEqual(111483, identity.visit)
        self.assertEqual(0x6d832ca291636984, identity.pfsDesignId)
        self.assertFalse(hasattr(identity, 'date'))

        identity = connector.parse_product_identity(PfsConfig, '2024-06-01/pfsConfig-0x6d832ca291636984-111483.fits')
        self.assertEqual(111483, identity.visit)
        self.assertEqual(0x6d832ca291636984, identity.pfsDesignId)
        self.assertEqual(date(2024, 6, 1), identity.date)


        identity = connector.parse_product_identity(PfsSingle, 'pfsSingle-10015-00001-1,1-0000000000005d48-111317.fits')
        self.assertEqual(0x5d48, identity.objId)
        self.assertEqual(111317, identity.visit)
        self.assertEqual(10015, identity.catId)
        self.assertEqual(1, identity.tract)
        self.assertEqual('1,1', identity.patch)

    def test_find_product(self):
        connector = self.get_test_connector()

        files, ids = connector.find_product(PfsDesign)
        self.assertTrue(len(files) > 0)
        self.assertEqual(len(files), len(ids.pfsDesignId))


        files, ids = connector.find_product(PfsConfig)
        self.assertTrue(len(files) > 0)
        self.assertEqual(len(files), len(ids.pfsDesignId))
        self.assertEqual(len(files), len(ids.visit))
        self.assertEqual(len(files), len(ids.date))

        files, ids = connector.find_product(PfsConfig, date=(date(2024, 6, 1), date(2024, 6, 4)))
        self.assertTrue(len(files) > 0)
        self.assertEqual(len(files), len(ids.pfsDesignId))
        self.assertEqual(len(files), len(ids.visit))
        self.assertEqual(len(files), len(ids.date))

        files, ids = connector.find_product(PfsConfig, visit=111483)
        self.assertTrue(len(files) > 0)
        self.assertEqual(111483, ids.visit[0])

        files, ids = connector.find_product(PfsConfig, pfsDesignId=0x6d832ca291636984)
        self.assertTrue(len(files) > 0)


        files, ids = connector.find_product(PfsSingle, catId=10015, visit=111317)
        self.assertTrue(len(files) > 0)

        files, ids = connector.find_product(PfsSingle, catId=10015, visit=[111317, 111318])
        self.assertTrue(len(files) > 0)

        files, ids = connector.find_product(PfsSingle, catId=10015, visit=(111317, 111318))
        self.assertTrue(len(files) > 0)

    def test_locate_product(self):
        connector = self.get_test_connector()

        file, id = connector.locate_product(PfsDesign, pfsDesignId=0x6d832ca291636984)
        self.assertIsNotNone(file)
        self.assertEqual(0x6d832ca291636984, id.pfsDesignId)


        files = connector.locate_product(PfsConfig, visit=111636, pfsDesignId=0x6d832ca291636984)
        files = connector.locate_product(PfsConfig, visit=111636)

        # More than one file matching
        self.failureException(
            FileNotFoundError,
            lambda _: connector.locate_product(PfsConfig, pfsDesignId=0x6d832ca291636984))

        # No file matching
        self.failureException(
            FileNotFoundError,
            lambda _: connector.locate_product(PfsConfig, visit=111636, pfsDesignId=0x6d832ca291636985))


        file, identity = connector.locate_product(PfsSingle, catId=10015, tract=1, patch='1,1', objId=0x5d48, visit=111317)
        self.assertIsNotNone(file)

    def test_load_product(self):
        connector = self.get_test_connector()

        connector.variables['rerundir'] = 'run17/20240604'
        filename, identity = connector.locate_product(PfsDesign, pfsDesignId=0x6d832ca291636984)

        pfsDesign = connector.load_product(PfsDesign, filename=filename)
        pfsDesign = connector.load_product(PfsDesign, identity=identity)

        #

        filename, identity = connector.locate_product(PfsConfig, visit=111483)
        
        pfsConfig = connector.load_product(PfsConfig, filename=filename)
        pfsConfig = connector.load_product(PfsConfig, identity=identity)

        #

        connector.variables['rerundir'] = 'run08'
        filename, identity = connector.locate_product(PfsArm, visit=83249, arm='r', spectrograph=1)

        pfsArm = connector.load_product(PfsArm, filename=filename)
        pfsArm = connector.load_product(PfsArm, identity=identity)

        #

        connector.variables['rerundir'] = 'run08'
        filename, identity = connector.locate_product(PfsMerged, visit=83245)

        pfsMerged = connector.load_product(PfsMerged, filename=filename)
        pfsMerged = connector.load_product(PfsMerged, identity=identity)

        #

        connector.variables['rerundir'] = 'run17/20240604'
        filename, identity = connector.locate_product(PfsSingle, catId=10015, tract=1, patch='1,1', objId=0x5d48, visit=111317)

        pfsSingle = connector.load_product(PfsSingle, filename=filename)
        pfsSingle = connector.load_product(PfsSingle, identity=identity)
        


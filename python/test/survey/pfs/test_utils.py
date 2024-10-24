import os
from datetime import date
from unittest import TestCase
import numpy as np
import numpy.testing as npt

from pfs.ga.pfsspec.survey.pfs.utils import *

class TestUtils(TestCase):
    def test_sort_arms(self):
        self.assertEqual('bmr', sort_arms('rmb'))
        self.assertEqual('bmr', sort_arms('rrmrb'))
        self.assertEqual('bmrn', sort_arms('rrnmrb'))
        self.assertEqual('brn', sort_arms('rbn'))
        self.assertEqual('bmn', sort_arms('mbn'))

    def test_merge_observations(self):
        obs1 = SimpleNamespace(visit=[1], arm=['b'], spectrograph=[1], pfsDesignId=[1], fiberId=[1], pfiNominal=[[1, 1]], pfiCenter=[[1, 1]], obsTime=[None], expTime=[np.nan])
        obs2 = SimpleNamespace(visit=[2], arm=['m'], spectrograph=[1], pfsDesignId=[1], fiberId=[2], pfiNominal=[[2, 2]], pfiCenter=[[2, 2]], obsTime=[None], expTime=[np.nan])
        obs3 = SimpleNamespace(visit=2, arm='n', spectrograph=1, pfsDesignId=1, fiberId=2, pfiNominal=[2, 2], pfiCenter=[2, 2], obsTime=None, expTime=np.nan)

        merged = merge_observations([obs3, obs2, obs1])
        npt.assert_equal(merged.visit, [1, 2])
        npt.assert_equal(merged.arm, ['b', 'mn'])
        npt.assert_equal(merged.spectrograph, [1, 1])
        npt.assert_equal(merged.pfsDesignId, [1, 1])
        npt.assert_equal(merged.fiberId, [1, 2])
        npt.assert_equal(merged.pfiNominal, [[1, 1], [2, 2]])
        npt.assert_equal(merged.pfiCenter, [[1, 1], [2, 2]])
        npt.assert_equal(merged.obsTime, [None, None])
        npt.assert_equal(merged.expTime, [np.nan, np.nan])

        merged = merge_observations([obs1, obs2, obs3])
        npt.assert_equal(merged.visit, [1, 2])
        npt.assert_equal(merged.arm, ['b', 'mn'])
        npt.assert_equal(merged.spectrograph, [1, 1])
        npt.assert_equal(merged.pfsDesignId, [1, 1])
        npt.assert_equal(merged.fiberId, [1, 2])
        npt.assert_equal(merged.pfiNominal, [[1, 1], [2, 2]])
        npt.assert_equal(merged.pfiCenter, [[1, 1], [2, 2]])
        npt.assert_equal(merged.obsTime, [None, None])
        npt.assert_equal(merged.expTime, [np.nan, np.nan])
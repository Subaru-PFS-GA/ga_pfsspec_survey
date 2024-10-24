from types import SimpleNamespace
from collections.abc import Iterable
import numpy as np

from .datamodel import *

def copy_target(target):
    return SimpleNamespace(
        catId = target.catId,
        tract = target.tract,
        patch = target.patch,
        objId = target.objId,
        ra = target.ra,
        dec = target.dec,
        targetType = target.targetType,
        fiberFlux = target.fiberFlux,
    )

def sort_arms(arms):
    """
    Sort the arms in a consistent order.

    Parameters
    ----------
    arms : list of str
        List of arms to sort.

    Returns
    -------
    list of str
        Sorted list of arms.
    """

    # Possible characters for arms: b m r n
    res = ''
    for a in 'bmrn':
        if a in arms:
            res += a
    return res

def get_observation(observations, i):
    """
    Extract a single observation from a list of observations.

    Parameters
    ----------
    observations : SimpleNamespace
        List of observations.

    Returns
    -------
    Observation
        A single observation extracted from the list.
    """

    obs = { k: np.atleast_1d(v[i]) for k, v in observations.__dict__() }
    return Observations(**obs)

def merge_observations(observations: list):
    """
    Merge a list of observations into a single observation.

    Parameters
    ----------
    observations : list of SimpleNamespace
        List of observations to merge.

    Returns
    -------
    SimpleNamespace
        A single merged observation.
    """

    merged = SimpleNamespace(
        visit = [],
        arm = [],
        spectrograph = [],
        pfsDesignId = [],
        fiberId = [],
        pfiNominal = [],
        pfiCenter = [],
        obsTime = [],
        expTime = [],
    )

    for i, obs in enumerate(observations):
        visit = obs.visit
        if isinstance(visit, Iterable):
            for j in range(len(visit)):
                if visit[j] in merged.visit:
                    # Only update the observed arms
                    k = merged.visit.index(visit[j])
                    if obs.arm[j] not in merged.arm[k]:
                        merged.arm[k] = merged.arm[k] + obs.arm[j]
                    continue
                else:
                    merged.visit.append(visit[j])
                    merged.arm.append(obs.arm[j])
                    merged.spectrograph.append(obs.spectrograph[j])
                    merged.pfsDesignId.append(obs.pfsDesignId[j])
                    merged.fiberId.append(obs.fiberId[j])
                    merged.pfiNominal.append(obs.pfiNominal[j])
                    merged.pfiCenter.append(obs.pfiCenter[j])
                    merged.obsTime.append(obs.obsTime[j])
                    merged.expTime.append(obs.expTime[j])
        else:
            if visit in merged.visit:
                # Only update the observed arms
                k = merged.visit.index(visit)
                if obs.arm not in merged.arm[k]:
                    merged.arm[k] = merged.arm[k] + obs.arm
                continue
            else:
                merged.visit.append(visit)
                merged.arm.append(obs.arm)
                merged.spectrograph.append(obs.spectrograph)
                merged.pfsDesignId.append(obs.pfsDesignId)
                merged.fiberId.append(obs.fiberId)
                merged.pfiNominal.append(obs.pfiNominal)
                merged.pfiCenter.append(obs.pfiCenter)
                merged.obsTime.append(obs.obsTime)
                merged.expTime.append(obs.expTime)

    sort_observations(merged)
    return Observations(**merged.__dict__)

def sort_observations(observations):
    """
    Sort the items in an Observations object by visit.
    """
    # Convert lists to numpy arrays and sort by visit
    # Also sort arms in a consistent order

    observations.visit = np.atleast_1d(observations.visit)
    idx = np.argsort(observations.visit)

    observations.visit = observations.visit[idx]
    observations.arm = np.atleast_1d(observations.arm)[idx]
    observations.spectrograph = np.atleast_1d(observations.spectrograph)[idx]
    observations.pfsDesignId = np.atleast_1d(observations.pfsDesignId)[idx]
    observations.fiberId = np.atleast_1d(observations.fiberId)[idx]
    observations.pfiNominal = np.atleast_2d(observations.pfiNominal)[idx]
    observations.pfiCenter = np.atleast_2d(observations.pfiCenter)[idx]
    observations.obsTime = np.atleast_1d(observations.obsTime)[idx]
    observations.expTime = np.atleast_1d(observations.expTime)[idx]

    for i in range(len(observations.arm)):
        observations.arm[i] = sort_arms(observations.arm[i])

def merge_identity(a, b, arm=None):
    """
    Merge two identities, by optionally overwriting the arm.
    """

    return Identity(
        visit = a.visit if a.visit is not None else b.visit,
        arm = arm if arm is not None else a.arm if a.arm != Identity.defaultArm else b.arms,
        spectrograph = a.spectrograph if a.spectrograph != Identity.defaultSpectrograph else b.spectrograph,
        pfsDesignId = a.pfsDesignId if a.pfsDesignId != Identity.defaultPfsDesignId else b.pfsDesignId,
        obsTime = a.obsTime if a.obsTime != Identity.defaultObsTime else b.obsTime,
        expTime = a.expTime if a.expTime != Identity.defaultExpTime else b.expTime,
    )


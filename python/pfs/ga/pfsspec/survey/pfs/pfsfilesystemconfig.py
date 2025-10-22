import os
import re
from types import SimpleNamespace

from .datamodel import *

from ..repo.intfilter import IntFilter
from ..repo.hexfilter import HexFilter
from ..repo.datefilter import DateFilter
from ..repo.stringfilter import StringFilter

# This is the old-style directory structure for PFS data.

PfsFileSystemConfig = SimpleNamespace(
    root = '$datadir',
    variables = {
        'datadir': '$PFSSPEC_PFS_DATADIR',
        'rerundir': '$PFSSPEC_PFS_RERUNDIR',
    },
    products = {
        PfsDesign: SimpleNamespace(
            name = 'pfsDesign',
            params = SimpleNamespace(
                pfsDesignId = HexFilter(name='pfsDesignId', format='{:016x}')
            ),
            params_regex = [
                re.compile(r'pfsDesign-(?P<pfsDesignId>0x[0-9a-fA-F]{16})\.(?:fits|fits\.gz)$'),
            ],
            dir_format = '$datadir/pfsDesign',
            filename_format = 'pfsDesign-0x{pfsDesignId}.fits',
            identity = lambda data:
                SimpleNamespace(pfsDesignId=data.pfsDesignId),
            load = lambda identity, filename, dir:
                PfsDesign.read(pfsDesignId=identity.pfsDesignId, dirName=dir),
        ),
        PfsConfig: SimpleNamespace(
            name = 'pfsConfig',
            params = SimpleNamespace(
                pfsDesignId = HexFilter(name='pfsDesignId', format='{:016x}'),
                visit = IntFilter(name='visit', format='{:06d}'),
                date = DateFilter(name='date', format='{:%Y-%m-%d}'),
            ),
            params_regex = [
                re.compile(r'(?P<date>\d{4}-\d{2}-\d{2})/pfsConfig-(?P<pfsDesignId>0x[0-9a-fA-F]{16})-(?P<visit>\d{6})\.(fits|fits\.gz)$'),
                re.compile(r'pfsConfig-(?P<pfsDesignId>0x[0-9a-fA-F]{16})-(?P<visit>\d{6})\.(fits|fits\.gz)$')
            ],
            dir_format = '$datadir/pfsConfig/{date}/',
            filename_format = 'pfsConfig-0x{pfsDesignId}-{visit}.fits',
            identity = lambda data:
                SimpleNamespace(pfsDesignId=data.pfsDesignId, visit=data.visit),
            load = lambda identity, filename, dir: 
                PfsConfig.read(pfsDesignId=identity.pfsDesignId, visit=identity.visit, dirName=dir),
        ),
        PfsArm: SimpleNamespace(
            name = 'pfsArm',
            params = SimpleNamespace(
                visit = IntFilter(name='visit', format='{:06d}'),
                arm = StringFilter(name='arm'),
                spectrograph = IntFilter(name='spectrograph', format='{:1d}'),
                date = DateFilter(name='date', format='{:%Y-%m-%d}'),
            ),
            params_regex = [
                re.compile(r'(?P<date>\d{4}-\d{2}-\d{2})/v(\d{6})/pfsArm-(?P<visit>\d{6})-(?P<arm>[brnm])(?P<spectrograph>\d)\.(fits|fits\.gz)$'),
                re.compile(r'pfsArm-(?P<visit>\d{6})-(?P<arm>[brnm])(?P<spectrograph>\d)\.(fits|fits\.gz)$')
            ],
            dir_format = '$datadir/$rerundir/pfsArm/{date}/v{visit}/',
            filename_format = 'pfsArm-{visit}-{arm}{spectrograph}.fits',
            identity = lambda data:
                SimpleNamespace(visit=data.identity.visit, arm=data.identity.arm, spectrograph=data.identity.spectrograph),
            load = lambda identity, filename, dir:
                PfsArm.read(Identity(identity.visit, arm=identity.arm, spectrograph=identity.spectrograph), dirName=dir),
        ),
        PfsMerged: SimpleNamespace(
            name = 'pfsMerged',
            params = SimpleNamespace(
                visit = IntFilter(name='visit', format='{:06d}'),
                date = DateFilter(name='date', format='{:%Y-%m-%d}'),
            ),
            params_regex = [
                re.compile(r'(?P<date>\d{4}-\d{2}-\d{2})/v(\d{6})/pfsMerged-(?P<visit>\d{6})\.(fits|fits\.gz)$'),
                re.compile(r'pfsMerged-(?P<visit>\d{6})\.(fits|fits\.gz)$'),
            ],
            dir_format = '$datadir/$rerundir/pfsMerged/{date}/v{visit}/',
            filename_format = 'pfsMerged-{visit}.fits',
            identity = lambda data:
                SimpleNamespace(visit=data.identity.visit),     # TODO: add date
            load = lambda identity, filename, dir:
                PfsMerged.read(Identity(identity.visit), dirName=dir),
        ),
        PfsSingle: SimpleNamespace(
            name = 'pfsSingle',
            params = SimpleNamespace(
                catId = IntFilter(name='catId', format='{:05d}'),
                tract = IntFilter(name='tract', format='{:05d}'),
                patch = StringFilter(name='patch'),
                objId = HexFilter(name='objId', format='{:016x}'),
                visit = IntFilter(name='visit', format='{:06d}'),
            ),
            params_regex = [
                re.compile(r'pfsSingle-(?P<catId>\d{5})-(?P<tract>\d{5})-(?P<patch>.*)-(?P<objId>[0-9a-f]{16})-(?P<visit>\d{6})\.(fits|fits\.gz)$'),
            ],
            dir_format = '$datadir/$rerundir/pfsSingle/{catId}/{tract}/{patch}',
            filename_format = 'pfsSingle-{catId}-{tract}-{patch}-{objId}-{visit}.fits',
            identity = lambda data:
                SimpleNamespace(catId=data.target.catId, tract=data.target.tract, patch=data.target.patch, objId=data.target.objId, visit=data.observations.visit[0]),
            load = lambda identity, filename, dir:
                PfsSingle.read(identity.__dict__, dirName=dir),
        ),
        PfsObject: SimpleNamespace(
            name = 'pfsObject',
            params = SimpleNamespace(
                catId = IntFilter(name='catId', format='{:05d}'),
                tract = IntFilter(name='tract', format='{:05d}'),
                patch = StringFilter(name='patch'),
                objId = HexFilter(name='objId', format='{:016x}'),
                nVisit = IntFilter(name='nVisit', format='{:03d}'),
                pfsVisitHash = HexFilter(name='pfsVisitHash', format='{:016x}'),
            ),
            params_regex = [
                re.compile(r'pfsObject-(?P<catId>\d{5})-(?P<tract>\d{5})-(?P<patch>.*)-(?P<objId>[0-9a-f]{16})-(?P<nVisit>\d{3})-(?P<pfsVisitHash>0x[0-9a-f]{16})\.(fits|fits\.gz)$'),
            ],
            dir_format = '$datadir/$rerundir/pfsObject/{catId}/{tract}/{patch}',
            filename_format = 'pfsObject-{catId}-{tract}-{patch}-{objId}-{nVisit}-0x{pfsVisitHash}.fits',
            identity = lambda data:
                SimpleNamespace(catId=data.target.catId, tract=data.target.tract, patch=data.target.patch, objId=data.target.objId, nVisit=data.nVisit, pfsVisitHash=data.pfsVisitHash),
            load = lambda identity, filename, dir:
                PfsObject.read(identity.__dict__, dirName=dir),
        ),
        PfsStar: SimpleNamespace(
            name = 'pfsStar',
            params = SimpleNamespace(
                catId = IntFilter(name='catId', format='{:05d}'),
                tract = IntFilter(name='tract', format='{:05d}'),
                patch = StringFilter(name='patch'),
                objId = HexFilter(name='objId', format='{:016x}'),
                nVisit = IntFilter(name='nVisit', format='{:03d}'),
                pfsVisitHash = HexFilter(name='pfsVisitHash', format='{:016x}'),
            ),
            params_regex = [
                re.compile(r'pfsStar-(?P<catId>\d{5})-(?P<tract>\d{5})-(?P<patch>.*)-(?P<objId>[0-9a-f]{16})-(?P<nVisit>\d{3})-(?P<pfsVisitHash>0x[0-9a-f]{16})\.(fits|fits\.gz)$'),
            ],
            dir_format = '$datadir/$rerundir/pfsStar/{catId}/{tract}/{patch}',
            filename_format = 'pfsStar-{catId}-{tract}-{patch}-{objId}-{nVisit}-0x{pfsVisitHash}.fits',
            identity = lambda data:
                SimpleNamespace(
                    catId = data.target.catId,
                    tract = data.target.tract,
                    patch = data.target.patch,
                    objId = data.target.objId,
                    nVisit = data.nVisit,
                    pfsVisitHash = calculatePfsVisitHash(data.observations.visit)
                ),
            load = lambda identity, filename, dir:
                PfsStar.readFits(os.path.join(dir, filename)),
            save = lambda data, identity, filename, dir:
                PfsStar.writeFits(data, os.path.join(dir, filename))
        ),
    }
)
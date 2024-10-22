import os
import re
from types import SimpleNamespace

from .datamodel import *

from ..repo.intfilter import IntFilter
from ..repo.hexfilter import HexFilter
from ..repo.datefilter import DateFilter
from ..repo.stringfilter import StringFilter

PfsFileSystemConfig = SimpleNamespace(
    root = '$datadir',
    variables = {
        'datadir': '$PFSSPEC_PFS_DATADIR',
        'rerundir': '$PFSSPEC_PFS_RERUNDIR',
    },
    products = {
        PfsDesign: SimpleNamespace(
            params = SimpleNamespace(
                pfsDesignId = HexFilter(name='pfsDesignId', format='{:016x}')
            ),
            params_regex = [
                re.compile(r'pfsDesign-0x(?P<pfsDesignId>[0-9a-fA-F]{16})\.(?:fits|fits\.gz)$'),
            ],
            dir_format = '$datadir/pfsDesign',
            filename_format = 'pfsDesign-0x{pfsDesignId}.fits',
            load = lambda identity, filename, dir:
                PfsDesign.read(pfsDesignId=identity.pfsDesignId, dirName=dir),
        ),
        PfsConfig: SimpleNamespace(
            params = SimpleNamespace(
                pfsDesignId = HexFilter(name='pfsDesignId', format='{:016x}'),
                visit = IntFilter(name='visit', format='{:06d}'),
                date = DateFilter(name='date', format='{:%Y-%m-%d}'),
            ),
            params_regex = [
                re.compile(r'(?P<date>\d{4}-\d{2}-\d{2})/pfsConfig-0x(?P<pfsDesignId>[0-9a-fA-F]{16})-(?P<visit>\d{6})\.(fits|fits\.gz)$'),
                re.compile(r'pfsConfig-0x(?P<pfsDesignId>[0-9a-fA-F]{16})-(?P<visit>\d{6})\.(fits|fits\.gz)$')
            ],
            dir_format = '$datadir/pfsConfig/{date}/',
            filename_format = 'pfsConfig-0x{pfsDesignId}-{visit}.fits',
            load = lambda identity, filename, dir: 
                PfsConfig.read(pfsDesignId=identity.pfsDesignId, visit=identity.visit, dirName=dir),
        ),
        PfsArm: SimpleNamespace(
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
            dir_format = '$datadir/rerun/$rerundir/pfsArm/{date}/v{visit}/',
            filename_format = 'pfsArm-{visit}-{arm}{spectrograph}.fits',
            load = lambda identity, filename, dir:
                PfsArm.read(Identity(identity.visit, arm=identity.arm, spectrograph=identity.spectrograph), dirName=dir),
        ),
        PfsMerged: SimpleNamespace(
            params = SimpleNamespace(
                visit = IntFilter(name='visit', format='{:06d}'),
                date = DateFilter(name='date', format='{:%Y-%m-%d}'),
            ),
            params_regex = [
                re.compile(r'(?P<date>\d{4}-\d{2}-\d{2})/v(\d{6})/pfsMerged-(?P<visit>\d{6})\.(fits|fits\.gz)$'),
                re.compile(r'pfsMerged-(?P<visit>\d{6})\.(fits|fits\.gz)$'),
            ],
            dir_format = '$datadir/rerun/$rerundir/pfsMerged/{date}/v{visit}/',
            filename_format = 'pfsMerged-{visit}.fits',
            load = lambda identity, filename, dir:
                PfsMerged.read(Identity(identity.visit), dirName=dir),
        ),
        PfsSingle: SimpleNamespace(
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
            dir_format = '$datadir/rerun/$rerundir/pfsSingle/{catId}/{tract}/{patch}',
            filename_format = 'pfsSingle-{catId}-{tract}-{patch}-{objId}-{visit}.fits',
            load = lambda identity, filename, dir:
                PfsSingle.read(identity.__dict__, dirName=dir),
        ),
        PfsObject: SimpleNamespace(
            params = SimpleNamespace(
                catId = IntFilter(name='catId', format='{:05d}'),
                tract = IntFilter(name='tract', format='{:05d}'),
                patch = StringFilter(name='patch'),
                objId = HexFilter(name='objId', format='{:016x}'),
                nVisit = IntFilter(name='nVisit', format='{:03d}'),
                pfsVisitHash = HexFilter(name='pfsVisitHash', format='{:016x}'),
            ),
            params_regex = [
                re.compile(r'pfsObject-(?P<catId>\d{5})-(?P<tract>\d{5})-(?P<patch>.*)-(?P<objId>[0-9a-f]{16})-(?P<nVisit>\d{3})-0x(?P<pfsVisitHash>[0-9a-f]{16})\.(fits|fits\.gz)$'),
            ],
            dir_format = '$datadir/rerun/$rerundir/pfsObject/{catId}/{tract}/{patch}',
            filename_format = 'pfsObject-{catId}-{tract}-{patch}-{objId}-{nVisit}-0x{pfsVisitHash}.fits',
            load = lambda identity, filename, dir:
                PfsObject.read(identity.__dict__, dirName=dir),
        ),
        PfsGAObject: SimpleNamespace(
            params = SimpleNamespace(
                catId = IntFilter(name='catId', format='{:05d}'),
                tract = IntFilter(name='tract', format='{:05d}'),
                patch = StringFilter(name='patch'),
                objId = HexFilter(name='objId', format='{:016x}'),
                nVisit = IntFilter(name='nVisit', format='{:03d}'),
                pfsVisitHash = HexFilter(name='pfsVisitHash', format='{:016x}'),
            ),
            params_regex = [
                re.compile(r'pfsGAObject-(?P<catId>\d{5})-(?P<tract>\d{5})-(?P<patch>.*)-(?P<objId>[0-9a-f]{16})-(?P<nVisit>\d{3})-0x(?P<pfsVisitHash>[0-9a-f]{16})\.(fits|fits\.gz)$'),
            ],
            dir_format = '$datadir/rerun/$rerundir/pfsGAObject/{catId}/{tract}/{patch}',
            filename_format = 'pfsGAObject-{catId}-{tract}-{patch}-{objId}-{nVisit}-0x{pfsVisitHash}.fits',
            load = lambda identity, filename, dir:
                PfsGAObject.read(identity.__dict__, dirName=dir),
        ),
    }
)
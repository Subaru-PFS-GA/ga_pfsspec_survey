import os
import re
from types import SimpleNamespace

from .datamodel import *

from ..repo import IntFilter, HexFilter, DateFilter, TimeFilter, StringFilter

PfsGen3FileSystemConfig = SimpleNamespace(
    root = '$datadir',
    variables = {
        'datadir': '$PFSSPEC_PFS_DATADIR',
        'rerundir': '$PFSSPEC_PFS_RERUNDIR',
        'rerun': '$PFSSPEC_PFS_RERUN',
        'pfsdesigndir': '$PFSSPEC_PFS_DESIGNDIR',
        'psfconfigdir': '$PFSSPEC_PFS_CONFIGDIR',
    },
    products = {
        PfsDesign: SimpleNamespace(
            params = SimpleNamespace(
                pfsDesignId = HexFilter(name='pfsDesignId', format='{:016x}')
            ),
            params_regex = [
                re.compile(r'pfsDesign-0x(?P<pfsDesignId>[0-9a-fA-F]{16})\.(?:fits|fits\.gz)$'),
            ],
            dir_format = '$pfsdesigndir/pfsDesign',
            filename_format = 'pfsDesign-0x{pfsDesignId}.fits',
            identity = lambda data:
                SimpleNamespace(pfsDesignId=data.pfsDesignId),
            load = lambda identity, filename, dir:
                PfsDesign.read(pfsDesignId=identity.pfsDesignId, dirName=dir),
        ),
        PfsConfig: SimpleNamespace(
            params = SimpleNamespace(
                visit = IntFilter(name='visit', format='{:06d}'),
                date = DateFilter(name='date', format='{:%Y%m%d}'),
            ),
            params_regex = [
                re.compile(r'(?P<date>\d{4}\d{2}\d{2})/(?P<visit>\d{6})/pfsConfig_PFS_\d{6}_PFS_raw_pfsConfig\.(fits|fits\.gz)$'),
                re.compile(r'pfsConfig-PFS-(?P<visit>\d{6})_PFS_raw_pfsConfig\.(fits|fits\.gz)$'),
            ],
            dir_format = '$psfconfigdir/pfsConfig/{date}/{visit}',
            filename_format = 'pfsConfig_PFS_{visit}_PFS_raw_pfsConfig.fits',
            identity = lambda data:
                SimpleNamespace(pfsDesignId=data.pfsDesignId, visit=data.visit),
            load = lambda identity, filename, dir: 
                PfsConfig.read(pfsDesignId=identity.pfsDesignId, visit=identity.visit, dirName=dir),
        ),
        PfsArm: SimpleNamespace(
            params = SimpleNamespace(
                visit = IntFilter(name='visit', format='{:06d}'),
                arm = StringFilter(name='arm'),
                spectrograph = IntFilter(name='spectrograph', format='{:1d}'),
                date = DateFilter(name='date', format='{:%Y%m%d}'),
                proctime = TimeFilter(name='proctime', format='{:%Y%m%dT%H%M%SZ}'),
            ),
            params_regex = [
                re.compile(r'(\d{8}T\d{6}Z)/pfsArm/(?P<date>\d{4}\d{2}\d{2})/(\d{6})/pfsArm_PFS_(?P<visit>\d{6})_(?P<arm>[brnm])(?P<spectrograph>\d)_(?P<rerun>[^.]+)_(?P<proctime>\d{8}T\d{6}Z)\.(fits|fits\.gz)$'),
                re.compile(r'pfsArm-(?P<visit>\d{6})-(?P<arm>[brnm])(?P<spectrograph>\d)\.(fits|fits\.gz)$')
            ],
            dir_format = '${datadir}/${rerundir}/{proctime}/pfsArm/{date}/{visit}/',
            filename_format = 'pfsArm_PFS_{visit}_{arm}{spectrograph}_${rerun}_{proctime}.fits',
            identity = lambda data:
                SimpleNamespace(visit=data.identity.visit, arm=data.identity.arm, spectrograph=data.identity.spectrograph),
            load = lambda identity, filename, dir:
                PfsArm.read(Identity(identity.visit, arm=identity.arm, spectrograph=identity.spectrograph), dirName=dir),
        ),
        PfsMerged: SimpleNamespace(
            params = SimpleNamespace(
                visit = IntFilter(name='visit', format='{:06d}'),
                date = DateFilter(name='date', format='{:%Y%m%d}'),
                proctime = TimeFilter(name='proctime', format='{:%Y%m%dT%H%M%SZ}'),
            ),
            params_regex = [
                re.compile(r'(\d{8}T\d{6}Z)/pfsMerged/(?P<date>\d{4}\d{2}\d{2})/(\d{6})/pfsMerged_PFS_(?P<visit>\d{6})_(?P<rerun>[^.]+)_(?P<proctime>\d{8}T\d{6}Z)\.(fits|fits\.gz)$'),
                re.compile(r'pfsMerged_PFS_(?P<visit>\d{6})_(?P<rerun>[^.]+)_(?P<proctime>\d{8}T\d{6}Z)\.(fits|fits\.gz)$')
            ],
            dir_format = '${datadir}/${rerundir}/{proctime}/pfsMerged/{date}/{visit}/',
            filename_format = 'pfsMerged_PFS_{visit}_${rerun}_{proctime}.fits',
            identity = lambda data:
                SimpleNamespace(visit=data.identity.visit),     # TODO: add date
            load = lambda identity, filename, dir:
                PfsMerged.read(Identity(identity.visit), dirName=dir),
        ),
        PfsCalibrated: SimpleNamespace(
            params = SimpleNamespace(
                visit = IntFilter(name='visit', format='{:06d}'),
                date = DateFilter(name='date', format='{:%Y%m%d}'),
                proctime = TimeFilter(name='proctime', format='{:%Y%m%dT%H%M%SZ}'),
            ),
            params_regex = [
                re.compile(r'(\d{8}T\d{6}Z)/pfsCalibrated/(?P<date>\d{4}\d{2}\d{2})/(\d{6})/pfsCalibrated_PFS_(?P<visit>\d{6})_(?P<rerun>[^.]+)_(?P<proctime>\d{8}T\d{6}Z)\.(fits|fits\.gz)$'),
                re.compile(r'pfsCalibrated_PFS_(?P<visit>\d{6})_(?P<rerun>[^.]+)_(?P<proctime>\d{8}T\d{6}Z)\.(fits|fits\.gz)$')
            ],
            dir_format = '${datadir}/${rerundir}/{proctime}/pfsCalibrated/{date}/{visit}/',
            filename_format = 'pfsCalibrated_PFS_{visit}_${rerun}_{proctime}.fits',
            identity = lambda data:
                SimpleNamespace(visit=data.identity.visit),     # TODO: add date
            load = lambda identity, filename, dir:
                PfsCalibrated.read(Identity(identity.visit), dirName=dir),
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
            identity = lambda data:
                SimpleNamespace(catId=data.target.catId, tract=data.target.tract, patch=data.target.patch, objId=data.target.objId, visit=data.observations.visit[0]),
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
            identity = lambda data:
                SimpleNamespace(catId=data.target.catId, tract=data.target.tract, patch=data.target.patch, objId=data.target.objId, nVisit=data.nVisit, pfsVisitHash=data.pfsVisitHash),
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
                PfsGAObject.readFits(os.path.join(dir, filename)),
            save = lambda data, identity, filename, dir:
                PfsGAObject.writeFits(data, os.path.join(dir, filename))
        ),
    }
)
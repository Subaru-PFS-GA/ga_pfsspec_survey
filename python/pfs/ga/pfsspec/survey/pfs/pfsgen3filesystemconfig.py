import os
import re
from types import SimpleNamespace

from .datamodel import *

from ..repo import IntFilter, HexFilter, DateFilter, TimeFilter, StringFilter

def load_PfsDesign(identity, filename, dir):
    return PfsDesign.read(pfsDesignId=identity.pfs_design_id, dirName=dir)

def load_PfsConfig(identity, filename, dir):
    if filename is not None:
        return PfsConfig._readImpl(filename, visit=identity.visit)
    else:
        return PfsConfig.read(pfsDesignId=identity.pfs_design_id, visit=identity.visit, dirName=dir)

def load_PfsArm(identity, filename, dir):
    return PfsArm.read(Identity(identity.visit, arm=identity.arm, spectrograph=identity.spectrograph), dirName=dir)

def load_PfsMerged(identity, filename, dir):
    if filename is not None:
        return PfsMerged.readFits(filename)
    else:
        return PfsMerged.read(Identity(identity.visit), dirName=dir)

def load_PfsCalibrated(identity, filename, dir):
    if filename is not None:
        return PfsCalibrated.readFits(filename)
    else:
        return PfsCalibrated.read(Identity(identity.visit), dirName=dir)

def load_PfsSingle(identity, filename, dir):
    return PfsSingle.read(identity.__dict__, dirName=dir)

def save_PfsSingle(data, identity, filename, dir):
    if filename is not None:
        data.writeFits(filename)
    else:
        raise NotImplementedError()

def load_PfsObject(identity, filename, dir):
    return PfsObject.read(identity.__dict__, dirName=dir)

def load_PfsGAObject(identity, filename, dir):
    return PfsGAObject.readFits(os.path.join(dir, filename))

def save_PfsGAObject(data, identity, filename, dir):
    PfsGAObject.writeFits(data, os.path.join(dir, filename))

def load_PfsGACatalog(identity, filename, dir):
    pass

def save_PfsGACatalog(data, identity, filename, dir):
    data.writeFits(filename)

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
            name = 'pfsDesign',
            params = SimpleNamespace(
                pfs_design_id = HexFilter(name='pfs_design_id', format='{:016x}')
            ),
            params_regex = [
                re.compile(r'pfsDesign-0x(?P<pfs_design_id>[0-9a-fA-F]{16})\.(?:fits|fits\.gz)$'),
            ],
            dir_format = '$pfsdesigndir/pfsDesign',
            filename_format = 'pfsDesign-0x{pfs_design_id}.fits',
            identity = lambda data:
                SimpleNamespace(pfs_design_id=data.pfsDesignId),
            load = load_PfsDesign,
        ),
        PfsConfig: SimpleNamespace(
            name = 'pfsConfig',
            params = SimpleNamespace(
                pfs_design_id = HexFilter(name='pfs_design_id', format='{:016x}'),
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
                SimpleNamespace(pfs_design_id=data.pfsDesignId, visit=data.visit),
            load = load_PfsConfig,
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
            load = load_PfsArm,
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
            load = load_PfsMerged,
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
            load = load_PfsCalibrated,
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
            dir_format = '$datadir/$rerundir/pfsSingle/{catId}/{tract}/{patch}',
            filename_format = 'pfsSingle-{catId}-{tract}-{patch}-{objId}-{visit}.fits',
            identity = lambda data:
                SimpleNamespace(catId=data.target.catId, tract=data.target.tract, patch=data.target.patch, objId=data.target.objId, visit=data.observations.visit[0]),
            load = load_PfsSingle,
            save = save_PfsSingle,
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
            dir_format = '$datadir/$rerundir/pfsObject/{catId}/{tract}/{patch}',
            filename_format = 'pfsObject-{catId}-{tract}-{patch}-{objId}-{nVisit}-0x{pfsVisitHash}.fits',
            identity = lambda data:
                SimpleNamespace(catId=data.target.catId, tract=data.target.tract, patch=data.target.patch, objId=data.target.objId, nVisit=data.nVisit, pfsVisitHash=data.pfsVisitHash),
            load = load_PfsObject,
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
            dir_format = '$datadir/$rerundir/pfsGAObject/{catId}/{tract}/{patch}',
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
            load = load_PfsGAObject,
            save = save_PfsGAObject
        ),
        PfsGACatalog: SimpleNamespace(
            params = SimpleNamespace(
                catId = IntFilter(name='catId', format='{:05d}'),
                nVisit = IntFilter(name='nVisit', format='{:03d}'),
                pfsVisitHash = HexFilter(name='pfsVisitHash', format='{:016x}'),
            ),
            params_regex = [
                re.compile(r'pfsGACatalog-(?P<catId>\d{5})-(?P<nVisit>\d{3})-0x(?P<pfsVisitHash>[0-9a-f]{16})\.(fits|fits\.gz)$'),
            ],
            dir_format = '$datadir/$rerundir/pfsGACatalog/{catId}',
            filename_format = 'pfsGACatalog-{catId}-{nVisit}-0x{pfsVisitHash}.fits',
            identity = lambda data:
                SimpleNamespace(
                    catId = data.catId,
                    nVisit = data.nVisit,
                    pfsVisitHash = calculatePfsVisitHash(data.observations.visit)
                ),
            load = load_PfsGACatalog,
            save = save_PfsGACatalog
        )
    }
)

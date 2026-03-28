import os
import re
from types import SimpleNamespace

from .datamodel import *

from ..repo import IntFilter, HexFilter, DateFilter, TimeFilter, StringFilter

def load_PfsStar(identity, filename, dir):
    return PfsStar.readFits(os.path.join(dir, filename))

def save_PfsStar(data, identity, filename, dir):
    PfsStar.writeFits(data, os.path.join(dir, filename))

def load_PfsStarCatalog(identity, filename, dir):
    pass

def save_PfsStarCatalog(data, identity, filename, dir):
    data.writeFits(filename)

PfsGAFileSystemConfig = SimpleNamespace(
    variables = {
        'datadir': '$PFSSPEC_PFS_DATADIR',
        'rundir': '$PFSSPEC_PFS_RUNDIR',
    },
    root = '$datadir',
    products = {
        PfsStar: SimpleNamespace(
            name = 'pfsStar',
            params = SimpleNamespace(
                run = StringFilter(name='run'),
                catId = IntFilter(name='catId', format='{:05d}'),
                objId = HexFilter(name='objId', format='{:016x}'),
                nVisit = IntFilter(name='nVisit', format='{:03d}'),
                pfsVisitHash = HexFilter(name='pfsVisitHash', format='{:016x}'),
            ),
            params_regex = [
                re.compile(r'pfsStar_PFS_(?P<catId>\d{5})-(?P<objId>[0-9a-f]{16})-(?P<nVisit>\d{3})-0x(?P<pfsVisitHash>[0-9a-f]{16})_(?P<run>[^.]+)\.(fits|fits\.gz)$'),
            ],
            dir_format = '$datadir/$rundir/pfsStar/{catId}/{objId}',
            filename_format = 'pfsStar_PFS_{catId}-{objId}-{nVisit}-0x{pfsVisitHash}_{run_}.fits',
            identity = lambda data:
                SimpleNamespace(
                    catId = data.target.catId,
                    tract = data.target.tract,
                    patch = data.target.patch,
                    objId = data.target.objId,
                    nVisit = data.nVisit,
                    pfsVisitHash = calculatePfsVisitHash(data.observations.visit)
                ),
            load = load_PfsStar,
            save = save_PfsStar
        ),
        PfsStarCatalog: SimpleNamespace(
            name = 'pfsStarCatalog',
            params = SimpleNamespace(
                run = StringFilter(name='run'),
                catId = IntFilter(name='catId', format='{:05d}'),
                nVisit = IntFilter(name='nVisit', format='{:03d}'),
                pfsVisitHash = HexFilter(name='pfsVisitHash', format='{:016x}'),
            ),
            params_regex = [
                re.compile(r'pfsStarCatalog_PFS_(?P<catId>\d{5})-(?P<nVisit>\d{3})-0x(?P<pfsVisitHash>[0-9a-f]{16})_(?P<run>[^.]+)\.(fits|fits\.gz)$'),
            ],
            dir_format = '$datadir/$rundir/pfsStarCatalog/{catId}',
            filename_format = 'pfsStarCatalog_PFS_{catId}-{nVisit}-0x{pfsVisitHash}_{run_}.fits',
            identity = lambda data:
                SimpleNamespace(
                    catId = data.catId,
                    nVisit = data.nVisit,
                    pfsVisitHash = calculatePfsVisitHash(data.observations.visit)
                ),
            load = load_PfsStarCatalog,
            save = save_PfsStarCatalog
        )
    }
)

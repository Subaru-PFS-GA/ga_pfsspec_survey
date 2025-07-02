from types import SimpleNamespace
from copy import deepcopy

from .pfsgen3filesystemconfig import PfsGen3FileSystemConfig

PfsGen3ButlerConfig = SimpleNamespace(
    root = '$datadir',
    variables = {
        'butlerconfigdir': '$BUTLER_CONFIGDIR',
        'butlercollections': '$BUTLER_COLLECTIONS',
    },
    products = deepcopy(PfsGen3FileSystemConfig.products),
)

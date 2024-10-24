import os
import re
import urllib.parse

from pfs.ga.pfsspec.core.util import SmartParallel
from pfs.ga.pfsspec.core.util.dict import pivot_array_of_dicts, pivot_dict_of_arrays
from ...io import SurveyDownloader

from ..setup_logger import logger

class PfsSurveyDownloader(SurveyDownloader):
    """
    Implements function to download spectra from a survey.

    Tokens can be requested through the science portal.
    """

    PORTAL_URL = 'https://hscpfs.mtk.nao.ac.jp/portal'
    DOWNLOAD_URL = 'https://hscpfs.mtk.nao.ac.jp/fileaccess'

    def __init__(self, orig=None):
        super().__init__(orig=orig)

        if not isinstance(orig, PfsSurveyDownloader):
            self.base_url = PfsSurveyDownloader.DOWNLOAD_URL
            self.token = None

            self.rerun_dir = None
            self.catId = None
            self.tract = None
            self.patch = None
            self.visit = None
            self.objId = None
        else:
            self.base_url = orig.base_url
            self.token = orig.token

            self.rerun_dir = orig.rerun_dir
            self.catId = orig.catId
            self.tract = orig.tract
            self.patch = orig.patch
            self.visit = orig.visit
            self.objId = orig.objId

    def add_args(self, parser, config):
        super().add_args(parser, config)

        parser.add_argument('--base-url', dest='base_url', type=str, default=None, help='Base URL of the survey')
        parser.add_argument('--token', dest='token', type=str, default=None, help='Token to access the survey')

        parser.add_argument('--rerun-dir', dest='rerun_dir', type=str, default=None, help='Rerun directory')
        parser.add_argument('--catId', dest='catId', type=int, default=None, help='Catalog ID')
        parser.add_argument('--tract', dest='tract', type=int, default=None, help='Tract')
        parser.add_argument('--patch', dest='patch', type=str, default=None, help='Patch')
        parser.add_argument('--visit', dest='visit', type=int, default=None, help='Visit')
        parser.add_argument('--objId', dest='objId', type=str, default=None, help='Object ID')

    def init_from_args(self, script, config, args):
        super().init_from_args(script, config, args)
    
        self.base_url = self.get_arg('base_url', self.base_url, args)
        self.token = self.get_arg('token', self.token, args)
        
        self.rerun_dir = self.get_arg('rerun_dir', self.rerun_dir, args)
        self.catId = self.get_arg('catId', self.catId, args)
        self.tract = self.get_arg('tract', self.tract, args)
        self.patch = self.get_arg('patch', self.patch, args)
        self.visit = self.get_arg('visit', self.visit, args)
        self.objId = self.get_arg('objId', self.objId, args)
        if self.objId is not None and self.objId.startswith('0x'):
            self.objId = int(self.objId, 16)
        elif self.objId is not None:
            self.objId = int(self.objId)

    def run(self):
        # TODO: now this only downloads pfsSingle files,
        #       extend this to process other types of files

        # Grab the list of files based on the catId, tract, and patch
        ids = self.get_pfsSingle_list(self.catId, self.tract, self.patch)

        # Filter the list to a certain objId and visit
        ids = self.filter_pfsSingle_list(ids, self.catId, self.tract, self.patch, self.objId, self.visit)

        self.download_pfsSingle_list(ids)
    
    def get_auth_headers(self):
        return { 'Authorization': f'Bearer {self.token}' }
    
    def get_full_url(self, url):
        # https://hscpfs.mtk.nao.ac.jp/fileaccess/2d/rerun/run15_20240328/pfsSingle/91023/00001/1%2C1/pfsSingle-91023-00001-1%2C1-008cc938174001af-108503.fits

        url = self.base_url + '/' + self.rerun_dir + '/' + url
        return url

    # TODO: these are common with PfsSurveyReader, consider merging them somewhere

    def get_pfsSingle_dir(self, catId, tract, patch):
        return f'pfsSingle/{catId:05d}/{tract:05d}/{patch}/'
    
    def get_pfsSingle_path(self, catId, tract, patch, objId, visit):
        dir = self.get_pfsSingle_dir(catId, tract, patch)
        return f'{dir}pfsSingle-{catId:05d}-{tract:05d}-{patch}-{objId:016x}-{visit:06d}.fits'
    
    def parse_pfsSingle_path(self, path):
        m = re.match(r"^pfsSingle-(\d{5})-(\d{5})-(.*)-([0-9a-f]{16})-(\d{6})\.fits.*$", path)
        if m is None:
            return None
        else:
            return {
                'catId': int(m.group(1)),
                'tract': int(m.group(2)),
                'patch': urllib.parse.unquote(m.group(3)),
                'objId': int(m.group(4), 16),
                'visit': int(m.group(5))
            }
        
    def get_pfsSingle_list(self, catId, tract, patch):
        # Read file list from the science platform server
        url = self.get_full_url(self.get_pfsSingle_dir(catId, tract, patch))
        headers = self.get_auth_headers()
        html = self.http_get(url, headers=headers).text
        urls = self.parse_href(html)
        ids = { k: [] for k in ['catId', 'tract', 'patch', 'objId', 'visit']}
        for url in urls:
            r = self.parse_pfsSingle_path(url)
            if r is not None:
                for k in ids:
                    ids[k].append(r[k])

        return ids
    
    def filter_pfsSingle_list(self, ids, catId, tract, patch, objId, visit):
        # Filter the list to a certain objId and visit)
        filtered_ids = { k: [] for k in ids }
        for i in range(len(ids['catId'])):
            if catId is None or ids['catId'][i] == catId \
                and tract is None or ids['tract'][i] == tract \
                and patch is None or ids['patch'][i] == patch \
                and objId is None or ids['objId'][i] == objId \
                and visit is None or ids['visit'][i] == visit:

                for k in ids:
                    filtered_ids[k].append(ids[k][i])

        return filtered_ids
    
    def download_pfsSingle(self, identity):
        # Download a pfsSingle file and save it

        catId = identity['catId']
        tract = identity['tract']
        patch = identity['patch']
        objId = identity['objId']
        visit = identity['visit']

        # Construct the download URL
        path = self.get_pfsSingle_path(catId, tract, patch, objId, visit)
        url = self.get_full_url(path)

        # Construct the output path
        outfile = os.path.join(self.outdir, path)
        
        headers = self.get_auth_headers()
        self.wget_download(url, outfile, headers=headers, resume=self.resume)

        return True
        

    def download_pfsSingle_error(self, ex, i):
        raise ex

    def download_pfsSingle_list(self, ids):
        ids = pivot_dict_of_arrays(ids)

        with SmartParallel(verbose=self.verbose, parallel=self.parallel, threads=self.threads) as p:
            res = [r for r in p.map(self.download_pfsSingle, self.download_pfsSingle_error, ids)]



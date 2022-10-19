import os, re
from glob import glob
import logging
import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord, Angle
from astropy.io import fits

from ..xslsurvey import XslSurvey
from ...io.surveyreader import SurveyReader
from .xslspectrumreader import XslSpectrumReader

class XslSurveyReader(SurveyReader):
    def __init__(self, orig=None):
        super().__init__(orig=orig)

        if not isinstance(orig, XslSurveyReader):
            self.reader = None
        else:
            self.reader = orig.reader

    def add_args(self, parser):
        super().add_args(parser)

    def init_from_args(self, config, args):
        super().init_from_args(config, args)

    def create_survey(self):
        return XslSurvey()

    def create_spectrum_reader(self):
        reader = XslSpectrumReader()
        reader.path = os.path.join(self.indir, 'fits')
        return reader

    def open_data(self, args, indir, outdir):
        super().open_data(args, indir, outdir)

        self.reader = self.create_spectrum_reader()
        self.reader.path = indir

    def load_file_list(self):
        ff = glob(os.path.join(self.indir, 'fits/*.fits'))
        ff = [ os.path.basename(f) for f in ff ]
        files = []
        for f in ff:
            files.append({ 
                'xsl_id': int(re.search('(\d+)', f).group(0)),
                'file_merged': f
                })

        files = pd.DataFrame(files)
        return files

    def load_fits_headers(self):
        """
        Read all FITS headers
        """

        ff = glob(os.path.join(self.indir, 'fits/*.fits'))
        fitsdata = None

        for f in ff:
            hdus = fits.open(f, memmap=False)
            headers = { k: hdus[0].header[k] for k in hdus[0].header.keys() }
            headers['filename'] = os.path.split(f)[1]
            
            if fitsdata is None:
                fitsdata = pd.DataFrame(headers, index=['XSL_ID'])
            else:
                fitsdata = fitsdata.append(headers, ignore_index=True)

        fitsdata['xsl_id'] = fitsdata['XSL_ID'].map(lambda x: int(re.search('(\d+)', x).group(0)))

        return fitsdata

    def load_params(self):
        # Main XSL data table

        fn = os.path.join(self.indir, 'table.dat')
        cols = {
            'obj_id':       (0, 25,     np.str),
            'uncert':       (25, 26,    np.str),
            'ra':           (27, 40,    np.str),
            'dec':          (40, 51,    np.str),
            'xsl_id':       (53, 58,    np.str),
            'mjd':          (59, 69,    np.float),
            'arm_missing':  (70, 77,    np.str),
            'file_uvb':     (78, 118,   np.str),
            'file_vis':     (119, 159,  np.str),
            'file_nir':     (160, 200,  np.str),
            'comments':     (201, 401,  np.str)}
        table = pd.read_fwf(fn, header=None,
            names=[ k for k in cols.keys() ],
            dtype={ k: cols[k][2] for k in cols.keys() },
            colspecs=[ (cols[k][0], cols[k][1]) for k in cols.keys() ])
        table['xsl_id'] = table['xsl_id'].map(lambda x: int(x[1:]))
        table['ra'] = table['ra'].map(lambda ra: Angle(ra, unit=u.hourangle).deg)
        table['dec'] = table['dec'].map(lambda dec: Angle(dec, unit=u.degree).deg)

        # Stellar parameters from Arentsen+19

        fn = os.path.join(self.indir, 'Arentsen+19/tablea1.dat')
        cols = {
            'HNAME':        (0, 24,    np.str),    
            'xsl_id':       (26, 29,   np.int),     
            'Teffuvb':      (30, 35,   np.float),    
            'logguvb':      (36, 41,   np.float),    
            '[Fe/H]uvb':    (42, 47,   np.float),    
            'Teffvis':      (48, 53,   np.float),    
            'loggvis':      (54, 59,   np.float),    
            '[Fe/H]vis':    (60, 65,   np.float),    
            'Teff':         (66, 71,   np.float),          
            'e_Teff':       (72, 76,   np.float),    
            'logg':         (77, 82,   np.float),    
            'e_logg':       (83, 87,   np.float),    
            '[Fe/H]':       (88, 93,   np.float),    
            'e_[Fe/H]':     (94, 98,   np.float),    
            'f_Teff':       (99, 100,  np.str),    
            'f_logg':       (101, 102, np.str),    
            'f_[Fe/H]':     (103, 104, np.str),    
            'Cflag':        (105, 106, np.str),    
        }
        tablea1 = pd.read_fwf(fn, header=None,
            names=[ k for k in cols.keys() ],
            dtype={ k: cols[k][2] for k in cols.keys() },
            colspecs=[ (cols[k][0], cols[k][1]) for k in cols.keys() ])

        return table, tablea1

    def join_params(self, files, fitsdata, table, tablea1):
        """
        Join tables to get file names and physical parameters
        """

        params = pd.merge(
            pd.merge(table, tablea1, left_on='xsl_id', right_on='xsl_id'),
            pd.merge(files, fitsdata, left_on='file_merged', right_on='filename'),
            left_on='xsl_id', right_on='xsl_id_x')

        params = params[['xsl_id', 'obj_id', 'filename',
            'ra', 'dec', 'mjd',
            '[Fe/H]', 'Teff', 'logg',
            'e_[Fe/H]', 'e_Teff', 'e_logg',
            'SPEC_RES', 'FWHM', 'SNR']]

        params.columns = ['xsl_id', 'obj_id', 'filename',
            'ra', 'dec', 'mjd',
            'Fe_H', 'T_eff', 'log_g',
            'Fe_H_err', 'T_eff_err', 'log_g_err',
            'res', 'pfs_fwhm', 'snr']

        return params

    def load_survey(self, params):
        reader = self.create_spectrum_reader()
        survey = self.create_survey()
        survey.params = params
        survey.spectra = []

        for index, row in survey.params.iterrows():
            spec = reader.load_spectrum(row['filename'])
            spec.ra = row['ra']
            spec.dec = row['dec']
            spec.mjd = row['mjd']

            spec.Fe_H = row['Fe_H']
            spec.Fe_H_err = row['Fe_H_err']
            spec.T_eff = row['T_eff']
            spec.T_eff_err = row['T_eff_err']
            spec.log_g = row['log_g']
            spec.log_g_err = row['log_g_err']

            spec.snr = row['snr']

            survey.spectra.append(spec)

        return survey

    def run(self):
        files = self.load_file_list()
        fitsdata = self.load_fits_headers()
        table, tablea1 = self.load_params()
        params = self.join_params(files, fitsdata, table, tablea1)
        survey = self.load_survey(params)
        return survey

    def execute_notebooks(self, script):
        super().execute_notebooks(script)
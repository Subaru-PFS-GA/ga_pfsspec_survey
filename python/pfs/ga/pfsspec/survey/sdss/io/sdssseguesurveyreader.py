import os

from pfs.ga.pfsspec.surveys.sdssseguesurvey import SdssSegueSurvey
from pfs.ga.pfsspec.surveys.sdsssurveyreader import SdssSurveyReader
from pfs.ga.pfsspec.surveys.sdss1stellarspectrumreader import Sdss1StellarSpectrumReader
from pfs.ga.pfsspec.surveys.sdss4stellarspectrumreader import Sdss4StellarSpectrumReader

class SdssSegueSurveyReader(SdssSurveyReader):
    def __init__(self, orig=None):
        super(SdssSegueSurveyReader, self).__init__(orig=orig)

        if isinstance(orig, SdssSegueSurveyReader):
            self.Fe_H = orig.Fe_H
            self.T_eff = orig.T_eff
            self.log_g = orig.log_g
            self.a_Fe = orig.a_Fe
        else:
            self.Fe_H = None
            self.T_eff = None
            self.log_g = None
            self.a_Fe = None

    def add_args(self, parser):
        super(SdssSegueSurveyReader, self).add_args(parser)

        parser.add_argument('--Fe_H', type=float, nargs=2, default=None, help='Limit [Fe/H]')
        parser.add_argument('--T_eff', type=float, nargs=2, default=None, help='Limit T_eff')
        parser.add_argument('--log_g', type=float, nargs=2, default=None, help='Limit log_g')
        parser.add_argument('--a_Fe', type=float, nargs=2, default=None, help='Limit [a/Fe]')

    def init_from_args(self, config, args):
        super(SdssSegueSurveyReader, self).init_from_args(config, args)

        self.Fe_H = self.get_arg('Fe_H', self.Fe_H, args)
        self.T_eff = self.get_arg('T_eff', self.T_eff, args)
        self.log_g = self.get_arg('log_g', self.log_g, args)
        self.a_Fe = self.get_arg('a_Fe', self.a_Fe, args)

    def create_survey(self):
        return SdssSegueSurvey()

    def create_spectrum_reader(self):
        if self.dr == 'DR7':
            return Sdss1StellarSpectrumReader()
        elif self.dr == 'DR16':
            return Sdss4StellarSpectrumReader()
        else:
            raise NotImplementedError()        

    def find_objects(self):
        if self.dr == 'DR7':
            return self.find_object_SDSS1()
        elif self.dr == 'DR16':
            return self.find_objects_SDSS4()
        else:
            raise NotImplementedError()

    def find_objects_SDSS1(self, context='DR7'):
        where = ''
        if self.mjd is not None:
            where += "AND s.mjd = {:d} \n".format(self.mjd)
        if self.plate is not None:
            where += "AND s.plate = {:d} \n".format(self.plate)
        if self.Fe_H is not None:
            where += "AND spp.feha BETWEEN {:f} AND {:f} \n".format(self.Fe_H[0], self.Fe_H[1])
        if self.T_eff is not None:
            where += "AND spp.teffa BETWEEN {:f} AND {:f} \n".format(self.T_eff[0], self.T_eff[1])
        if self.log_g is not None:
            where += "AND spp.logga BETWEEN {:f} AND {:f} \n".format(self.log_g[0], self.log_g[1])
        if self.a_Fe is not None:
            where += "AND spp.alphafe BETWEEN {:f} AND {:f} \n".format(self.a_Fe[0], self.a_Fe[1])

        sql = \
        """
        SELECT {} 
            s.specObjID AS id, s.mjd, s.plate, s.fiberID AS fiber, s.ra AS ra, s.dec AS dec, 
            s.z AS redshift, s.zErr AS redshift_err, s.sn_1 AS snr,
            spp.feha AS Fe_H, spp.fehaerr AS Fe_H_err, 
            spp.teffa AS T_eff, spp.teffaerr AS T_eff_err,
            spp.logga AS log_g, spp.loggaerr AS log_g_err,
            spp.alphafe AS a_Fe, spp.alphafeerr AS a_Fe_err,
            p.psfMag_r AS mag, p.psfMagErr_r AS mag_err,
            p.psfMag_u AS mag_u, p.psfMagErr_u AS mag_u_err,
            p.psfMag_g AS mag_g, p.psfMagErr_g AS mag_g_err,
            p.psfMag_r AS mag_r, p.psfMagErr_r AS mag_r_err,
            p.psfMag_i AS mag_i, p.psfMagErr_i AS mag_i_err,
            p.psfMag_z AS mag_z, p.psfMagErr_z AS mag_z_err,
            p.extinction_r AS ext
        FROM SpecObj s
            INNER JOIN sppParams spp ON spp.specobjID = s.specObjID
            INNER JOIN PhotoObj p ON p.objID = s.bestObjID
        WHERE specClass = 1 AND zConf > 0.98 
              AND p.psfMag_r > 10               -- exclude unmeasured psf mag 
              {}
        ORDER BY s.mjd, s.plate, s.fiberID
        """.format('' if self.top is None else 'TOP {:d}'.format(self.top), where)

        if self.outdir is not None:
            with open(os.path.join(self.outdir, "sciserver.sql"), "w") as f:
                f.write(sql)

        return self.execute_query(sql, context=context)

    def find_objects_SDSS4(self, context='DR16'):
        where = ''
        if self.mjd is not None:
            where += "AND s.mjd = {:d} \n".format(self.mjd)
        if self.plate is not None:
            where += "AND s.plate = {:d} \n".format(self.plate)
        if self.Fe_H is not None:
            where += "AND spp.FEHADOP BETWEEN {:f} AND {:f} \n".format(self.Fe_H[0], self.Fe_H[1])
        if self.T_eff is not None:
            where += "AND spp.TEFFADOP BETWEEN {:f} AND {:f} \n".format(self.T_eff[0], self.T_eff[1])
        if self.log_g is not None:
            where += "AND spp.LOGGADOP BETWEEN {:f} AND {:f} \n".format(self.log_g[0], self.log_g[1])
        if self.a_Fe is not None:
            raise ValueError("Alpha abundance not measured in {}.".format(context))

        sql = \
        """
        SELECT {}
            s.specObjID AS id, s.mjd, s.plate, s.fiberID AS fiber, s.ra AS ra, s.dec AS dec, 
            s.z AS redshift, s.zErr AS redshift_err, s.snMedian AS snr,
            spp.FEHADOP AS Fe_H, spp.FEHADOPUNC AS Fe_H_err, 
            spp.TEFFADOP AS T_eff, spp.TEFFADOPUNC AS T_eff_err,
            spp.LOGGADOP AS log_g, spp.LOGGADOPUNC AS log_g_err,
            -9999.0 AS a_Fe, -9999.0 AS a_Fe_err,
            p.psfMag_r AS mag, p.psfMagErr_r AS mag_err,
            p.psfMag_u AS mag_u, p.psfMagErr_u AS mag_u_err,
            p.psfMag_g AS mag_g, p.psfMagErr_g AS mag_g_err,
            p.psfMag_r AS mag_r, p.psfMagErr_r AS mag_r_err,
            p.psfMag_i AS mag_i, p.psfMagErr_i AS mag_i_err,
            p.psfMag_z AS mag_z, p.psfMagErr_z AS mag_z_err,
            p.extinction_r AS ext,
            dbo.fGetUrlFitsSpectrum(s.specObjID) AS url
        FROM SpecObjAll s
        INNER JOIN sppParams spp ON spp.specobjID = s.specObjID
        INNER JOIN PhotoObj p ON p.objID = s.bestObjID
        WHERE class = 'STAR' 
            AND instrument = 'SDSS'
            AND p.psfMag_r > 10               -- exclude unmeasured psf mag 
            {}
        ORDER BY s.mjd, s.plate, s.fiberID
        """.format(
            '' if self.top is None else 'TOP {:d}'.format(self.top),
            where)

        if self.outdir is not None:
            with open(os.path.join(self.outdir, "sciserver.sql"), "w") as f:
                f.write(sql)

        return self.execute_query(sql, context=context)
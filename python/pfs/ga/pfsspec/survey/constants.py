class Constants():
    PFSSPEC_SURVEY_LOGNAME = 'pfs.ga.survey'

    # TODO: move these under SDSS
    SDSS_SP_MASK_OK = 0x000
    SDSS_SP_MASK_NOPLUG = 0x001  # Fiber not listed in plugmap file
    SDSS_SP_MASK_BADTRACE = 0x002  # Bad trace from routine TRACE320CRUDE
    SDSS_SP_MASK_BADFLAT = 0x004  # Low counts in fiberflat
    SDSS_SP_MASK_BADARC = 0x008  # Bad arc solution
    SDSS_SP_MASK_MANYBADCOL = 0x010  # More than 10% pixels are bad columns
    SDSS_SP_MASK_MANYREJECT = 0x020  # More than 10% pixels are rejected in extraction
    SDSS_SP_MASK_LARGESHIFT = 0x040  # Large spatial shift between flat and object position
    SDSS_SP_MASK_NEARBADPIX = 0x10000  # Bad pixel within 3 pixels of trace
    SDSS_SP_MASK_LOWFLAT = 0x20000  # Flat field less than 0.5
    SDSS_SP_MASK_FULLREJECT = 0x40000  # Pixel fully rejected in extraction
    SDSS_SP_MASK_PARTIALREJ = 0x80000  # Some pixels rejected in extraction
    SDSS_SP_MASK_SCATLIGHT = 0x100000  # Scattered light significant
    SDSS_SP_MASK_CROSSTALK = 0x200000  # Cross-talk significant
    SDSS_SP_MASK_NOSKY = 0x400000  # Sky level unknown at this wavelength
    SDSS_SP_MASK_BRIGHTSKY = 0x800000  # Sky level > flux + 10*(flux error)
    SDSS_SP_MASK_NODATA = 0x1000000  # No data available in combine B-spline
    SDSS_SP_MASK_COMBINEREJ = 0x2000000  # Rejected in combine B-spline
    SDSS_SP_MASK_BADFLUXFACTOR = 0x4000000  # Low flux-calibration or flux-correction factor
    SDSS_SP_MASK_BADSKYCHI = 0x8000000  # Chi^2 > 4 in sky residuals at this wavelength
    SDSS_SP_MASK_REDMONSTER = 0x10000000  # Contiguous region of bad chi^2 in sky residuals
    SDSS_SP_MASK_EMLINE = 0x40000000  # Emission line detected here
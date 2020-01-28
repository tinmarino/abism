"""
    Fits Header parser

Necessary:
    diameter        (real in m)     The primary diameter
    wavelenght      (real in um)    The wavelength of the detection
    obstruction     (real in %)     The percentage in area of the central
                                    obstruction. This is 14%**2 for VLT i guess,
    pixel_scale     (real in arsec/pixel) The number anguler size of one p
                                    pixel in arcsec

Util for real intensity/position:
    exptime         (real in sec)   The time of one exposure.  This will not
                                    infer the strehl ratio but the potometry
                                    as well as the zero point.
    zpt             (real in log)   The luminosity of 1 intensity Arbitrary
                                    Unit during one second.
                                    The higher the Zero point, the fainter stars
                                    (or noise) you may detect.
                                    It depends on the filter AND the airmass.
    wcs             (wcs object)    This set of matrices can be used to get the
                                    position on sky of your object.

Helper:
    telescope       (string)        Name of your telescope
    date            (string)        Date, maybe of last modification
    date_obs        (string)        Data of observation.
    instrument      (string)        Name of the instrument.
    company         (string)        Name of the company owning the telescope:
                                    ESO, CFHT, Carnergie...

    instrument      (string)        Name of the camera. Can be used to
                                    automatially retrieve informations.
    reduced_type    (string)        RAW or REDUCED

    saturation_level  (real ADU)    The ADU of saturation of the CCD, proper to
                                    the science camera.  non_lineratiry_level
                                    (real ADU) The ADU where non linearity starts,
                                    I wont use this value I guess.
                                    Or just as a quiet warning.
"""

import numpy as np
from astropy import wcs

from abism.util import log



def parse_header(header):
    """ the objects is fits.open(image)[0]"""

    # 0/ DETERMINE the instrument
    if 'INSTRUM' in header:
        instrument = header['INSTRUM']
    elif 'INSTRUME' in header:
        instrument = header['INSTRUME']
    elif 'INSTRUMENT' in header:
        instrument = header['INSTRUMENT']
    else:
        instrument = ""
    log(3, 'Header parsing got instrument:', instrument)

    # 1/ Call header Class According to the instrument
    if ("NAOS" in instrument) and ("CONICA" in instrument):
        return NacoHeader(header)
    if "SINFONI" in instrument:
        return SinfoniHeader(header)

    return Header(header)

class WCSDefault:
    def all_pix2world(self, x, y):
        return np.array([[float('nan'), float('nan')]])


class Header:
    """Container"""
    def __init__(self, header):
        self.header = header

        # Strehl
        self.diameter = float('nan')  # m
        self.wavelength = float('nan')  # um
        self.obstruction = float('nan')  # % area
        self.pixel_scale = float('nan')   # arsec/pixel

        self.exptime = 1.     # sec
        self.zpt = 0.
        self.wcs = WCSDefault()

        # Doc
        self.telescope = 'UNKNOWN telescope'
        self.date = 'UNKNOWN date '
        self.date_obs = 'UNKNOWN obsdate'
        self.instrument = 'UNKNOWN instrument'
        self.company = "UNKNOWN company"  # will be "eso"

        # Info
        self.saturation_level = np.inf  # in ADU
        self.non_linearity_level = np.inf

        # COMPANY
        # because, the HIERARCH disappear when readden by python
        if any("ESO OBS" in s for s in self.header.keys()):
            self.company = "ESO"

        # TELESCOP
        if "TELESCOP" in self.header:
            self.telescope = self.header["TELESCOP"]

        # INSRTU
        if 'INSTRUM' in self.header:
            self.instrument = self.header['INSTRUM']
            if 'INSTRUME' in self.header:
                self.instrument = self.header['INSTRUME']
                if 'INSTRUMENT' in self.header:
                    self.instrument = self.header['INSTRUMENT']

        self.reduced_type = "RAW"
        # REDUCED
        if 'HIERARCH ESO PRO TYPE' in self.header:
            self.reduced_type = self.header['HIERARCH ESO PRO TYPE']

        # WAVELENGHT
        if 'FILTER' in self.header:
            filt = self.header['FILTER']
            if filt == 'H':
                self.wavelength = 1.6
            if ("U" or "u") in filt:
                self.wavelength = 0.365
            if ("B" or "b") in filt:
                self.wavelength = 0.445
            if ("V" or "v") in filt:
                self.wavelength = 0.551
            if ("R" or "r") in filt:
                self.wavelength = 0.658
            if ("I" or "i") in filt:
                self.wavelength = 0.806
            if ("Z" or "z") in filt:
                self.wavelength = 0.9
            if ("Y" or "y") in filt:
                self.wavelength = 1.020
            if ("J" or "j") in filt:
                self.wavelength = 1.220
            if ("K" or "k") in filt:
                self.wavelength = 2.190
            if ("L" or "l") in filt:
                self.wavelength = 3.450
            if ("M" or "m") in filt:
                self.wavelength = 4.750
            if 'LAMBDA' in self.header:
                self.wavelength = self.header['LAMBDA']
                if 'HIERARCH ESO INS CWLEN' in self.header:
                    self.wavelength = self.header['HIERARCH ESO INS CWLEN']

        # ""
        # APERTURE
        if 'VLT'in self.telescope:
            self.diameter = 8.0
            self.obstruction = 14.
        elif 'Baade'in self.telescope:
            self.diameter = 6.0
            self.obstruction = 15
        elif "Keck" in self.telescope:
            self.diameter = 10.
            if 'TELDIAM' in self.header:
                self.diameter = self.header['TELDIAM']
                if 'TELSECD' in self.header:
                    self.obstruction = (
                        self.header['TELSECD'] / self.diameter)**2

        #
        # SCALE
        # baade
        if 'SCALE' in self.header:
            self.pixel_scale = self.header['SCALE']
        if (self.pixel_scale > 1e-6) & (self.pixel_scale < 1e-3):  # in deg
            self.pixel_scale *= 3600

        # ZPT
        self.zpt = 0
        if "ZPT" in self.header:
            self.zpt = float(self.header['ZPT'])

        # VLT
        if 'HIERARCH ESO INS PIXSCALE' in self.header:
            self.pixel_scale = self.header['HIERARCH ESO INS PIXSCALE']
            if 'APPXSCL' in self.header:
                self.pixel_scale = self.header['APPXSCL'] / 1000.
                if 'CD1_1' in self.header:
                    if 'CD2_2' in self.header:
                        self.pixel_scale = (abs(float(self.header['CD1_1'])) + abs(
                            float(self.header['CD2_2']))) / 2. * 3600.
                    else:
                        self.pixel_scale = abs(
                            float(self.header['CD1_1'])) * 3600.

        if self.pixel_scale == 0:
            self.pixel_scale = 99.

        # Useless keys
        if 'DATE' in self.header:
            self.date = self.header['DATE']
            if 'DATE-OBS' in self.header:
                self.date_obs = self.header['DATE-OBS']
                if 'BPM' in self.header:
                    self.bpm_name = self.header['BPM']

        if 'EXPTIME' in self.header:
            self.exptime = self.header['EXPTIME']
            if 'HIERARCH ESO DET DIT' in self.header:
                self.exptime = self.header['HIERARCH ESO DET DIT']

        self.WCSKey()

    def WCSKey(self):  # and zpt for all classes
        """Fill WCS"""
        try:
            def flatten_header(header):
                """
                Attempt to turn an N-dimensional fits header into a 2-dimensional header
                Turns all CRPIX[>2] etc. into new keywords with suffix 'A'

                header must be a fits.Header instance
                """

                # astropy.io.fits != fits -> sadness
                # if not hasattr(header,'copy')
                # raise Exception("flatten_header requires a fits.Header
                # instance")

                newheader = header.copy()

                for key in newheader.keys():
                    try:
                        if int(key[-1]) >= 3 and key[:2] in ['CD', 'CR', 'CT', 'CU', 'NA']:
                            newheader.rename_key(key, 'A' + key, force=True)
                    except ValueError:
                        # if key[-1] is not an int
                        pass
                    except IndexError:
                        # if len(key) < 2
                        pass
                newheader.update(NAXIS=2)

                return newheader

            self.flathead = flatten_header(self.header)
            # If proj type in more than 8 characters, we cut from 3 dec----tan
            # -> dec--tan
            # RA---TAN
            # DEC--TAN
            for field in ('CTYPE1', 'CTYPE2'):
                value = self.flathead.get('CTYPE1', '')
                if len(value) > 8:
                    self.flathead[field] = value[0:3] + value[len(value) - 8 + 3:]

            self.wcs = wcs.WCS(self.flathead)  # for coord transformation

            # Warning, dirty pig, thie depends on the shape of x
            if (self.wcs.all_pix2world([[0, 0]], 0) == [[1, 1]]).all():
                self.wcs.all_pix2world = lambda x, y: np.array([[float('nan'), float('nan')]])

        except:  # includding no wcs module
            import traceback
            log(0, traceback.format_exc(),
                "WARNING I dit not manage to get WCS from wcs\n\n")

        #
        # WCS
        self.CD1_1, self.CD2_2 = 1, 1
        self.CD2_1, self.CD1_2 = 0, 0
        if 'CD1_1' in self.header:
            self.CD1_1 = float(self.header['CD1_1'])
            if 'CD1_2' in self.header:
                self.CD1_2 = float(self.header['CD1_2'])
                if 'CD2_1' in self.header:
                    self.CD2_1 = float(self.header['CD2_1'])
                    if 'CD2_2' in self.header:
                        self.CD2_2 = float(self.header['CD2_2'])

        #
        #  ZPT


class NacoHeader(Header):
    """NaOS + Conica la lleva pero se la llevaron !"""
    def __init__(self, header):
        Header.__init__(self, header)
        self.company = "ESO"
        if "TELESCOP" in self.header:  # NACO will be changed soon
            self.telescope = self.header["TELESCOP"]
        self.instrument = "NaCo"

        # StrehlKey
        self.wavelength = self.header['HIERARCH ESO INS CWLEN']
        self.diameter = 8.0
        self.obstruction = 14
        self.pixel_scale = self.header['HIERARCH ESO INS PIXSCALE']

        self.reduced_type = "RAW"
        if 'HIERARCH ESO PRO TYPE' in self.header:
            self.reduced_type = self.header['HIERARCH ESO PRO TYPE']

        self.Saturation()

    def Saturation(self):
        """Check if non-linear or even staturated"""
        if 'HIERARCH ESO DET NCORRS NAME' in self.header:
            self.ncor = self.header['HIERARCH ESO DET NCORRS NAME']
            if 'HIERARCH ESO DET MODE NAME' in self.header:
                self.read_mode = self.header['HIERARCH ESO DET MODE NAME']
                bias = -np.inf
                fullwell = np.inf  # in case
                if self.ncor == "Double_RdRstRd":
                    bias, fullwell = 0., 15000.
                elif self.ncor == "FowlerNsamp":
                    bias, fullwell = 0., 7500.
                elif self.ncor == "Uncorr":
                    bias = -8000.
                    if self.read_mode == "HighDynamic":
                        fullwell = 15000.
                        if self.read_mode == "HighWellDepth":
                            fullwell = 22000.
                            if self.read_mode == "HighBackground":
                                fullwell = 28000.

        self.saturation_level = fullwell + bias
        self.non_linearity_level = 0.6 * fullwell + bias


class SinfoniHeader(Header):
    """Sinfoni Instrument"""
    def __init__(self, header):
        Header.__init__(self, header)

        self.company = "ESO"
        if "TELESCOP" in self.header:  # NACO will be changed soon
            self.telescope = self.header["TELESCOP"]
        self.instrument = "SINFONI"
        self.reduced_type = "RAW"
        if 'HIERARCH ESO PRO TYPE' in self.header:
            self.reduced_type = self.header['HIERARCH ESO PRO TYPE']

        # StrehlKey
        self.wavelength = float(
            self.header['HIERARCH ESO INS GRAT1 WLEN']) / 1000
        self.diameter = 8.0
        self.obstruction = 14.

        def pixel_scale():
            # PIXEL SCALE FROM CD matrix
            if 'CD1_1' in self.header:
                if 'CD2_2' in self.header:
                    self.pixel_scale = (abs(float(self.header['CD1_1'])) + abs(
                        float(self.header['CD2_2']))) / 2. * 3600.
                else:
                    self.pixel_scale = abs(
                        float(self.header['CD1_1'])) * 3600.

        # PIXEL SCALE FROM HEADER OPT1.NAME
        opt1 = 1.
        if 'HIERARCH ESO INS OPTI1 NAME' in self.header:
            opt1 = float(self.header['HIERARCH ESO INS OPTI1 NAME'])
            self.pixel_scale = np.sqrt(2) / 2 * opt1
            if self.pixel_scale == 0:
                self.pixel_scale = 99.
            self.pixel_scale = opt1

        pixel_scale()

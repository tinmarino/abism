"""
    Warning, I am loaded in util space

    The answer object the backend is sharing
class Answer(metaclass=ABCMeta):
    # Base class for an answser
    # Printable with a value
    def __init__(self, text, obj):
        self.text = text
        self.value = obj

    def __str__(self):
        pass



"""

from abc import ABC, abstractmethod

import numpy as np

from abism.util import get_root


class Answer(ABC):
    """Base class for an answser
    text and value
    """
    def __init__(self, text, value):
        self.text = text
        self.value = value

    @abstractmethod
    def __str__(self):
        return str(self.value)


class AnswerSky(Answer):
    """Different possible representation
    on sky: real univer
    on detector: what you see, (on image is overused)
    """
    @abstractmethod
    def str_sky(self):
        return self.__str__()

    @abstractmethod
    def str_detector(self):
        return self.__str__()


class AnswerNum(Answer):
    """A number"""
    def __init__(self, text, number):
        super().__init__(text, float(number))

    def __str__(self):
        return f'{self.value:,.1f}'.replace(',', ' ')


class AnswerPosition(AnswerSky):
    """A position on image: x, y or ra/dec
    Stored as x, y and a ref to wcs
    """
    def __init__(self, text, xy, converter=None):
        super().__init__(text, xy)
        self.converter = converter

    def __str__(self):
        return self.str_detector()

    def str_sky(self):
        """
        my_wcs = wcs.all_pix2world(
        np.array([[W.strehl["center_y"], W.strehl["center_x"]]]), 0)
            W.strehl["center_ra"], W.strehl["center_dec"] = my_wcs[0][0], my_wcs[0][1]
        """
        if self.converter is None: return self.str_detector()
        ra, dec = self.converter(np.array([self.value]), 0)
        s_ra, s_dec = format_sky(ra, dec)
        return s_ra + ' , ' + s_dec

    def str_detector(self):
        x, y = self.value
        s_x = f'{x:,.3f}'.replace(',', ' ')
        s_y = f'{y:,.3f}'.replace(',', ' ')
        return s_x + ' , ' + s_y


class AnswerLuminosity(AnswerSky):
    """Luminosity stored in adu, convertable to mag
    Require: zero point
             exposure time
    phot_mag = W.strehl["my_photometry"] / get_root().header.exptime
    phot_mag = get_root().header.zpt - 2.5 * np.log10(phot_mag)
    line = AnswerImageSky(
        "Photometry: ",
        W.strehl["my_photometry"],
        MyFormat(W.strehl["my_photometry"], 1, "f") + " [adu]",
        "%.2f" % phot_mag + " [mag]"
        )
    """
    def __str__(self):
        return self.str_detector()

    def str_sky(self):
        # Read header
        exptime = get_root().header.exptime
        zpt = get_root().header.zpt

        # Get Flux / sec
        i_sky = self.value / exptime
        # Get Magnitude
        i_sky = zpt - 2.5 * np.log10(i_sky)

        return f'{i_sky:.2f}'

    def str_detector(self):
        return f'{self.value:.1f}'



# Helpers to transform coordinate


def decimal2hms(RADeg, delimiter):
    # pylint: disable = W, R, C
    """Converts decimal degrees to string in Hours:Minutes:Seconds format with
    user specified delimiter.

    @type RADeg: float
    @param RADeg: coordinate in decimal degrees
    @type delimiter: string
    @param delimiter: delimiter character in returned string
    @rtype: string
    @return: coordinate string in H:M:S format

    """

    hours = (RADeg/360.0)*24
    # if hours < 10 and hours >= 1:
    if 1 <= hours < 10:
        sHours = '0'+str(hours)[0]
    elif hours >= 10:
        sHours = str(hours)[:2]
    elif hours < 1:
        sHours = '00'
    else:
        return 'nan'

    if str(hours).find('.') == -1:
        mins = float(hours)*60.0
    else:
        mins = float(str(hours)[str(hours).index('.'):])*60.0
    # if mins<10 and mins>=1:
    if 1 <= mins < 10:
        sMins = '0'+str(mins)[:1]
    elif mins >= 10:
        sMins = str(mins)[:2]
    elif mins < 1:
        sMins = '00'
    else:
        return 'nan'

    secs = (hours-(float(sHours)+float(sMins)/60.0))*3600.0
    # if secs < 10 and secs>0.001:
    if 0.001 < secs < 10:
        sSecs = '0'+str(secs)[:str(secs).find('.')+4]
    elif secs < 0.0001:
        sSecs = '00.001'
    else:
        sSecs = str(secs)[:str(secs).find('.')+4]
    if len(sSecs) < 5:
        sSecs = sSecs+'00'      # So all to 3dp

    if float(sSecs) == 60.000:
        sSecs = '00.00'
        sMins = str(int(sMins)+1)
    if int(sMins) == 60:
        sMins = '00'
        sDeg = str(int(sDeg)+1)

    return sHours+delimiter+sMins+delimiter+sSecs


def decimal2dms(decDeg, delimiter):
    # pylint: disable = W, R, C
    """Converts decimal degrees to string in Degrees:Minutes:Seconds format
    with user specified delimiter.

    @type decDeg: float
    @param decDeg: coordinate in decimal degrees
    @type delimiter: string
    @param delimiter: delimiter character in returned string
    @rtype: string
    @return: coordinate string in D:M:S format

    """
    # Positive
    if decDeg > 0:
        # if decDeg < 10 and decDeg>=1:
        if 1 <= decDeg < 10:
            sDeg = "0"+str(decDeg)[0]
        elif decDeg >= 10:
            sDeg = str(decDeg)[:2]
        elif decDeg < 1:
            sDeg = "00"
        else:
            return 'nan'

        if str(decDeg).find(".") == -1:
            mins = float(decDeg)*60.0
        else:
            mins = float(str(decDeg)[str(decDeg).index("."):])*60
        # if mins<10 and mins>=1:
        if 1 <= mins < 10:
            sMins = "0"+str(mins)[:1]
        elif mins >= 10:
            sMins = str(mins)[:2]
        elif mins < 1:
            sMins = "00"
        else:
            return 'nan'

        secs = (decDeg-(float(sDeg)+float(sMins)/60.0))*3600.0
        # if secs<10 and secs>0:
        if 0 < secs < 10:
            sSecs = "0"+str(secs)[:str(secs).find(".")+3]
        elif secs < 0.001:
            sSecs = "00.00"
        else:
            sSecs = str(secs)[:str(secs).find(".")+3]
        if len(sSecs) < 5:
            sSecs = sSecs+"0"   # So all to 2dp

        if float(sSecs) == 60.00:
            sSecs = "00.00"
            sMins = str(int(sMins)+1)
        if int(sMins) == 60:
            sMins = "00"
            sDeg = str(int(sDeg)+1)

        return "+"+sDeg+delimiter+sMins+delimiter+sSecs

    else:
        # if decDeg>-10 and decDeg<=-1:
        if -10 < decDeg <= -1:
            sDeg = "-0"+str(decDeg)[1]
        elif decDeg <= -10:
            sDeg = str(decDeg)[:3]
        elif decDeg > -1:
            sDeg = "-00"
        else:
            return 'nan'

        if str(decDeg).find(".") == -1:
            mins = float(decDeg)*-60.0
        else:
            mins = float(str(decDeg)[str(decDeg).index("."):])*60
        # if mins<10 and mins>=1:
        if 1 <= mins < 10:
            sMins = "0"+str(mins)[:1]
        elif mins >= 10:
            sMins = str(mins)[:2]
        elif mins < 1:
            sMins = "00"
        else:
            return 'nan'

        secs = (decDeg-(float(sDeg)-float(sMins)/60.0))*3600.0
        # if secs>-10 and secs<0:
        # so don't get minus sign
        if -10 < secs < 0:
            sSecs = "0"+str(secs)[1:str(secs).find(".")+3]
        elif secs > -0.001:
            sSecs = "00.00"
        else:
            sSecs = str(secs)[1:str(secs).find(".")+3]
        if len(sSecs) < 5:
            sSecs = sSecs+"0"   # So all to 2dp

        if float(sSecs) == 60.00:
            sSecs = "00.00"
            sMins = str(int(sMins)+1)
        if int(sMins) == 60:
            sMins = "00"
            sDeg = str(int(sDeg)-1)

        return sDeg+delimiter+sMins+delimiter+sSecs


def hms2decimal(RAString, delimiter):
    """Converts a delimited string of Hours:Minutes:Seconds format into decimal
    degrees.

    @type RAString: string
    @param RAString: coordinate string in H:M:S format
    @type delimiter: string
    @param delimiter: delimiter character in RAString
    @rtype: float
    @return: coordinate in decimal degrees

    """
    # is it in HH:MM:SS format?
    if delimiter == "":
        RABits = str(RAString).split()
    else:
        RABits = str(RAString).split(delimiter)
    if len(RABits) > 1:
        RAHDecimal = float(RABits[0])
        if len(RABits) > 1:
            RAHDecimal = RAHDecimal+(float(RABits[1])/60.0)
        if len(RABits) > 2:
            RAHDecimal = RAHDecimal+(float(RABits[2])/3600.0)
        RADeg = (RAHDecimal/24.0)*360.0
    else:
        RADeg = float(RAString)

    return RADeg


def dms2decimal(decString, delimiter):
    """Converts a delimited string of Degrees:Minutes:Seconds format into
    decimal degrees.

    @type decString: string
    @param decString: coordinate string in D:M:S format
    @type delimiter: string
    @param delimiter: delimiter character in decString
    @rtype: float
    @return: coordinate in decimal degrees

    """
    # is it in DD:MM:SS format?
    if delimiter == "":
        decBits = str(decString).split()
    else:
        decBits = str(decString).split(delimiter)
    if len(decBits) > 1:
        decDeg = float(decBits[0])
        if decBits[0].find("-") != -1:
            if len(decBits) > 1:
                decDeg = decDeg-(float(decBits[1])/60.0)
            if len(decBits) > 2:
                decDeg = decDeg-(float(decBits[2])/3600.0)
        else:
            if len(decBits) > 1:
                decDeg = decDeg+(float(decBits[1])/60.0)
            if len(decBits) > 2:
                decDeg = decDeg+(float(decBits[2])/3600.0)
    else:
        decDeg = float(decString)

    return decDeg


def format_sky(ra, dec):
    if (ra == 99) or isinstance(ra, str):
        x = "N/A"
    else:
        x = decimal2hms(ra, ":")
    if (dec == 99) or isinstance(dec, str):
        y = "N/A"
    else:
        y = decimal2dms(dec, ":")
    return x, y


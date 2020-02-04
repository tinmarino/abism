"""
    List of AnswerSky
"""

from abc import ABC, abstractmethod

import numpy as np


class AnswerSky(ABC):
    """Abism answer from BackEnd, base class
    Variables:
        text:   textual name of varaible
        value:  object value of the variable
        error:  other AnswerSky (of same class) representing the error
                the error has no error!
    Methods: Different possible representation:
        on sky: real univer
        on detector: what you see, (on image is overused)

    Note: overloaded operator to do some error arithmetic for free

    """
    def __init__(self, text, value, error=None):
        self.text = text
        self.value = value
        # Create an error answer of the same type
        if error is not None:
            self.error = self.__class__(text + ' Error', error)
        else:
            self.error = None
        self.unit = ''

    @abstractmethod
    def str_sky(self): pass

    @abstractmethod
    def str_detector(self): pass

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s_err = str(self.error.value) if self.error else 'nan'
        return self.str_detector() + '±' + s_err + '<- ' + self.text


    def constant(self, cst, op):
        """Constant operation on self"""
        # pylint: disable = eval-used
        txt = self.text + op + str(cst)
        val = eval('self.value' + op + str(cst))
        err = eval('self.error.value' + op + str(cst))
        return self.__class__(txt, val, error=err)


    def addition(self, other, op='+'):
        """Helper addition substraction"""
        if isinstance(other, (int, float)):
            return self.constant(other, op)
        if self.__class__ != other.__class__:
            raise NotImplementedError

        if op == '+':
            val = self.value + other.value
        else:
            val = self.value - other.value
        err1 = 0 if self.error is None else self.error.value
        err2 = 0 if other.error is None else other.error.value
        err = np.sqrt(err1**2 + err2**2)
        txt = self.text + op + other.text
        return self.__class__(txt, val, error=err)


    def multiplication(self, other, op='*'):
        """Helper for multiplication"""
        if isinstance(other, (int, float)):
            return self.constant(other, op)
        txt = self.text + op + other.text

        if op == '*':
            val = self.value * other.value
        else:
            val = self.value / other.value

        err1 = 0 if self.error is None else self.error.value
        err2 = 0 if other.error is None else other.error.value
        err = (err1 / self.value)**2 + (err2 / other.value)**2
        err = np.sqrt(err) * val

        return AnswerNum(txt, val, error=err)


    def __add__(self, other):
        return self.addition(other, op='+')

    def __sub__(self, other):
        return self.addition(other, op='-')

    def __rsub__(self, other):
        return other.__sub__(self)

    def __mul__(self, other):
        return self.multiplication(other, '*')

    def __truediv__(self, other):
        """No right part yet. Lazy coding..."""
        return self.multiplication(other, '/')

    def __abs__(self):
        txt = 'abs(' + self.text + ')'
        val = abs(self.value)
        err = self.error.value
        return self.__class__(txt, val, error=err)

    @staticmethod
    def power(bv, be, ev, ee):
        """xʸ -> log(|x|) * err(y) ⊕ y * err(x) (more or less)
        Where ⊕ is the harmonic sum
        In: base value, base error, exponent value, exponent error
        """
        if bv == 0:
            err = 0
        else:
            err = (np.log(abs(bv)) * ee)**2
            err += (ev * be)**2
            err = np.sqrt(err)
        return err

    def __pow__(self, other):
        # Get error and value (in case not an answer)
        if isinstance(other, (int, float)):
            ov = other
            oe = 0
            ot = str(other)
        else:
            ov = other.value
            oe = other.error.value
            ot = other.text

        txt = '(' + self.text + ')' + '**(' + ot + ')'
        val = self.value**ov
        err = AnswerSky.power(self.value, self.error.value, ov, oe)
        return AnswerNum(txt, val, error=err)

    def __rpow__(self, other):
        if isinstance(other, (int, float)):
            ov = other
            oe = 0
            ot = str(other)
        else:
            ov = other.value
            oe = other.error.value
            ot = other.text

        txt = '(' + ot + ')' + '**(' + self.text + ')'
        val = ov**self.value
        err = AnswerSky.power(self.value, self.error.value, ov, oe)
        return AnswerNum(txt, val, error=err)

    def sqrt(self):
        return self.__pow__(0.5)

    __radd__ = __add__
    __iadd__ = __add__
    __rmul__ = __mul__
    __imul__ = __mul__
    __rtruediv__ = __truediv__
    __itruediv__ = __truediv__


class AnswerObject(AnswerSky):
    """Any object"""
    def str_detector(self):
        return str(self.value)

    def str_sky(self):
        return str(self.value)


class AnswerNum(AnswerSky):
    """A number"""
    def __init__(self, text, number, unit='', error=None):
        super().__init__(text, float(number), error=error)
        self.unit = unit

    def str_detector(self):
        return f'{self.value:,.1f}'.replace(',', ' ')

    def str_sky(self):
        return self.str_detector()


class AnswerPosition(AnswerSky):
    """A position on image: x, y or ra/dec
    Stored as x, y and a ref to wcs
    """
    def __init__(self, text, xy, error=None):
        super().__init__(text, xy, error=error)
        self.unit = [' [pxl]', ' [ra, dec]']

    def str_sky(self):
        from abism.util import get_root
        x, y = self.value
        wcs = get_root().header.wcs
        ra, dec = wcs.all_pix2world(np.array([[x, y]]), 0)[0]
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
    """
    def __init__(self, text, adu, error=None):
        super().__init__(text, adu, error=error)
        self.unit = [' [adu]', ' [mag]']

    def str_sky(self):
        from abism.util import get_root
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


class AnswerFwhm(AnswerSky):
    """FWHM has diffrent values
    Need the pixel scale, separation too
    """
    def __init__(self, text, fwhm, error=None):
        super().__init__(text, fwhm, error=error)
        self.unit = [' [pxl]', ' [mas]']

    def str_sky(self):
        # Get pixel scale
        pxll = get_pixel_scale()

        # Apply pixel scale
        a, b, e = self.value
        a *= pxll * 1000
        b *= pxll * 1000

        return self.__class__.format_value(a, b, e)

    def str_detector(self):
        return self.__class__.format_value(*self.value)

    @staticmethod
    def format_value(a, b, e):
        return  f'{a:.1f}, {b:.1f}, {e:.2f}'


class AnswerDistance(AnswerSky):
    """Number of pixel or angular distance"""
    def __init__(self, text, xy, error=None):
        super().__init__(text, xy, error=error)
        self.unit = [' [pxl]', " ''"]

    def str_sky(self):
        # Get pixel scale
        pxll = get_pixel_scale()
        sky_distance = pxll * self.value
        return f'{sky_distance:.3f}'

    def str_detector(self):
        return f'{self.value:.2f}'


class AnswerAngle(AnswerSky):
    """Get a tuple (vector), returns its angle to the top
    Ex: x=0.02, y =10 => angle = 0
    """
    def __init__(self, text, xy, error=None):
        super().__init__(text, xy, error=error)
        self.unit = u'\xb0'

    def str_detector(self):
        im_angle = np.arccos(self.value[1]) * 57.295779
        sign = np.sign(self.value[0])
        im_angle = im_angle + (sign-1)*(-90)
        return f'{im_angle:.2f}'

    def str_sky(self):
        from abism.util import get_root
        # inverted angle and not north
        sky_angle = np.arccos(
            self.value[1] * get_root().frame_image.north_direction[1]
            + self.value[0] * get_root().frame_image.north_direction[0]) * 57.295779
        sign = np.sign(
            self.value[0] * get_root().frame_image.north_direction[0]
            + self.value[1] * get_root().frame_image.east_direction[1])
        sky_angle = sky_angle + (sign-1)*(-90)
        return f'{sky_angle:.2f}'


# Helpers to transform coordinate

def get_pixel_scale():
    """Return: arcsec / pixel, something like 0.02 (NaCo)"""
    from abism.util import get_root
    try:  # Sinfoni
        pxll = get_root().header.sinf_pixel_scale
    except:
        pxll = get_root().header.pixel_scale
    return pxll


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

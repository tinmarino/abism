"""
    Strehl meter
    TODO prettify, the function division is nto judicious:
        Error goes along with mesure (always)
"""
import numpy as np

from abism.back import ImageFunction as IF
from abism.back import StrehlImage as SI

from abism.util import log, get_root, get_state, get_aa, set_aa, \
    EA, EPhot


def StrehlMeter(rectangle):
    """ Note : this should just be a caller
        this is the first written, strehlMeter for pick one,
        I putted more for ellipse and binary
    """

    # Find center && fwhm
    rectangle = IF.Order4(rectangle, grid=get_state().image.im0)
    # IF.FindBadPixel(get_state().image.im0,(rx1,rx2,ry1,ry2))
    # TODO really work twice ?
    star_center = IF.DecreasingGravityCenter(get_state().image.im0, r=rectangle)
    star_center = IF.FindMaxWithBin(get_state().image.im0, rectangle)
    tmp = IF.LocalMax(get_state().image.im0, center=star_center, size=3)
    star_max, star_center = tmp[2], (tmp[0], tmp[1])
    IF.FWHM(get_state().image.im0, star_center)

    # Delegate fit && Save
    o_psf = SI.PsfFit(
        get_state().image.im0, rectangle,
        center=star_center, my_max=star_max)
    psf_fit = o_psf.do_fit().get_result()
    get_state().d_fit_param.update(psf_fit[0])
    get_state().d_fit_error.update(psf_fit[1])

    # Save what it take
    center = psf_fit[0]['center_x'], psf_fit[0]['center_y']
    set_aa(EA.CENTER, center)

    intensity = psf_fit[0]['intensity']
    set_aa(EA.INTENSITY, intensity)

    # Get Background && Save
    background, rms = SI.Background(get_state().image.im0, r=rectangle)
    set_aa(EA.BACKGROUND, background)
    set_aa(EA.NOISE, rms)

    # Get photometry && Save
    photometry, _, number_count = \
        SI.Photometry(get_state().image.im0, background, rectangle=rectangle)
    err_photometry = rms * np.sqrt(number_count)
    set_aa(EA.PHOTOMETRY, photometry)
    set_aa(EA.ERR_PHOTOMETRY, err_photometry)

    # Get Signal on noise && Save
    signal_on_noise = photometry / background / np.sqrt(number_count)
    set_aa(EA.SN, signal_on_noise)

    # Save:  Side effect of course
    save_fwhm()

    # Math
    StrehlRatio()
    StrehlError()


def StrehlRatio():
    # Read from global
    bessel_integer = get_bessel_integer()
    photometry = get_aa(EA.PHOTOMETRY)
    intensity = get_aa(EA.INTENSITY)
    wavelength = get_root().header.wavelength
    log(5, 'Calculating Strehl with', "\n"
        'intensity =', intensity, "\n"
        'photometry =', photometry, "\n"
        'bessel_integer =', bessel_integer, "\n"
        'wavelength =', wavelength, "\n")

    # Get theoretical intensity && Save
    Ith = photometry / bessel_integer
    set_aa(EA.INTENSITY_THEORY, Ith)

    # Save strehl (finally)
    strehl = intensity / Ith
    set_aa(EA.STREHL, 100 * strehl, unit=' %')

    # Save equivalent Strehl ratio
    strehl_eq = get_equivalent_strehl_ratio(strehl, wavelength)
    set_aa(EA.STREHL_EQ, 100 * strehl_eq, unit=' %')

    # Saven for error just after
    set_aa(EA.INTENSITY_THEORY, Ith)
    set_aa(EA.BESSEL_INTEGER, bessel_integer)


def get_bessel_integer():
    """Read wavelenght, pixel_scale, diameter, obstruction"""
    bessel_integer = get_root().header.wavelength * \
        10**(-6.) / np.pi / (get_root().header.pixel_scale/206265) / get_root().header.diameter
    bessel_integer = bessel_integer**2 * 4 * \
        np.pi / (1-(get_root().header.obstruction/100)**2)
    return bessel_integer


def StrehlError():
    """after strehl , number count , background, center_x, and center_y
    """
    dics = get_state().d_fit_error

    # Get in <- side
    Sr = get_state().get_answer(EA.STREHL)
    Ith = get_aa(EA.INTENSITY_THEORY)
    bessel_integer = get_aa(EA.BESSEL_INTEGER)
    dBack = get_aa(EA.NOISE)
    dPhot = get_aa(EA.PHOTOMETRY)

    # if get_state().picka_type != "ellipse": the ellipse was doing the aperture
    get_state().e_phot_type = EPhot.FIT
    log(3, "\n\n WARNING: StrehlError changed the aperture type "
           "to fit because not ellipse pick it shouldn't matter ")

    # INTENSITY
    if get_state().e_phot_type and get_state().s_fit_type != "None":
        dI = get_state().d_fit_error["intensity"]
    else:
        x0, y0 = int(get_state().d_fit_param["center_x"]), int(get_state().d_fit_param["center_y"])
        mean = np.mean(get_state().image.im0[x0-1:x0+2, y0-1:y0+2])
        dI = (get_state().d_fit_param["intensity"] - mean)
        dI /= 2

    dIpsf = np.sqrt(dI**2 + dBack**2)  # error from peak
    dIth = dPhot / bessel_integer           # error from phot
    dSr = np.sqrt(dIpsf**2 + (Sr/100 * abs(dIth))**2)
    dSr /= Ith
    dSr *= 100

    # Save
    # TODO move me in caller
    res = dSr * 3  # because I calculated the best error
    get_state().add_answer(EA.ERR_STREHL, res)

    # Save Equivelent err = err * eq/real (unreadable, sorry)
    strehl_eq_err = get_state().get_answer(EA.ERR_STREHL)
    strehl_eq_err *= get_state().get_answer(EA.STREHL_EQ)
    strehl_eq_err /= get_state().get_answer(EA.STREHL)
    get_state().add_answer(EA.ERR_STREHL_EQ, strehl_eq_err, unit=' %')




def save_fwhm():
    """Save (Long, Short axe, Excentricity)"""
    fwhm_a = max(get_state().d_fit_param["fwhm_x"], get_state().d_fit_param["fwhm_y"])
    fwhm_b = min(get_state().d_fit_param["fwhm_x"], get_state().d_fit_param["fwhm_y"])
    fwhm_e = np.sqrt(fwhm_a**2 - fwhm_b**2) / fwhm_a
    get_state().add_answer(EA.FWHM_ABE, (fwhm_a, fwhm_b, fwhm_e))


def BinaryStrehl(star1, star2):
    binary_psf = SI.BinaryPsf(get_state().image.im0, star1, star2)
    psf_fit = binary_psf.do_fit().get_result()
    get_state().d_fit_param = psf_fit[0]
    get_state().d_fit_error = psf_fit[1]
    append_binary_info()


def TightBinaryStrehl(star1, star2):
    tight_psf = SI.TightBinaryPsf(get_state().image.im0, star1, star2)
    psf_fit = tight_psf.do_fit().get_result()
    get_state().d_fit_param = psf_fit[0]
    get_state().d_fit_error = psf_fit[1]
    append_binary_info()


def append_binary_info():
    """Read
    Write: Separatation"""
    # Fit type
    fit_dic, err_dic = get_state().d_fit_param, get_state().d_fit_error
    # TODO : Isn't that ugly
    set_aa(EA.BINARY, get_state().s_fit_type)

    # Some lookup due to move
    x0, x1, y0, y1 = fit_dic["x0"], fit_dic["x1"], fit_dic["y0"], fit_dic["y1"]
    dx0, dx1 = err_dic["x0"], err_dic["x1"]
    dy0, dy1 = err_dic["y0"], err_dic["y1"]

    set_aa(EA.STAR1, (y0, x0))
    set_aa(EA.STAR2, (y1, x1))

    # Get separation
    separation_dic = get_separation(point=((x0, x1), (y0, y1)), err=((dx0, dx1), (dy0, dy1)))
    separation = separation_dic["dist"]
    sep_err = separation_dic["dist_err"]
    xy_angle = separation_dic["xy_angle"]
    set_aa(EA.ORIENTATION, xy_angle)
    set_aa(EA.SEPARATION, separation)
    set_aa(EA.ERR_SEPARATION, sep_err)

    phot0, phot1 = fit_dic["my_photometry0"], fit_dic["my_photometry1"]
    set_aa(EA.PHOTOMETRY1, phot0)
    set_aa(EA.PHOTOMETRY2, phot1)
    set_aa(EA.FLUX_RATIO, phot0 / phot1)

    # Strehl
    bessel_integer = get_bessel_integer()
    Ith0, Ith1 = phot0/bessel_integer, phot1/bessel_integer
    strehl0 = fit_dic["intensity0"] / Ith0
    strehl1 = fit_dic["intensity1"] / Ith1
    set_aa(EA.STREHL1, 100 * strehl0, unit=' %')
    set_aa(EA.STREHL2, 100 * strehl1, unit=' %')


def EllipseEventStrehl(ellipse):
    """Main ellipse worker,
    Param: ellipse artist with ru, rv, position
    """
    if get_state().e_phot_type == EPhot.FIT:
        log(0, "Warning: Ellipse Mesurement ignoring fit photometric type")

    # Background
    back_stat = SI.EllipseEventBack(ellipse)
    background = back_stat.mean
    get_state().add_answer(EA.BACKGROUND, background)

    # Photometry
    photometry, _, _ = SI.EllipseEventPhot(ellipse, background)
    get_state().add_answer(EA.PHOTOMETRY, photometry)

    # Get maximum (side effect)
    SI.EllipseEventMax(ellipse)

    # Math
    StrehlRatio()
    # TODO refactor StrehlErrorn not working here
    #StrehlError()


def get_equivalent_strehl_ratio(strehl, wavelength):
    """Get equivalent Strehl ration at 2.17"""
    if strehl < 0:
        factor = 0
    else:
        factor = wavelength / 2 / np.pi * np.sqrt(-np.log(strehl))

    factor = - (factor * 2 * np.pi / 2.17)**2

    return np.exp(factor)


def get_separation(point=((0, 0), (0, 0)), err=((0, 0), (0, 0))):
    """point1i  (and 2) : list of 2 float = (x,y)= row, column
    err_point1 = 2 float = x,y )
    read north position in W
    """
    point1, point2 = point[0], point[1]
    err_point1, err_point2 = err[0], err[1]
    x0, x1, y0, y1 = point1[0], point1[1], point2[0], point2[1]
    dx0, dx1, dy0, dy1 = err_point1[0], err_point1[1], err_point2[0], err_point2[1]

    # Get separation distance <- Pythagora
    dist = np.sqrt((y1-y0)**2 + (x1-x0)**2)

    # Get error
    dist_err = np.sqrt(dx0**2 + dx1**2)
    dx0 = np.sqrt(err_point1[0]**2 + err_point1[1]**2)
    dx1 = np.sqrt(err_point2[0]**2 + err_point2[1]**2)

    # Get angle
    angle = np.array([(y1-y0),   (x1-x0)])
    angle /= np.sqrt((y0-y1)**2 + (x0-x1)**2)

    res = {"xy_angle": angle,
           "dist": dist, "dist_err": dist_err,
           }
    return res

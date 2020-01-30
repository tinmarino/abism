"""
    Strehl meter
"""
import numpy as np

from abism.back import ImageFunction as IF
from abism.back import StrehlImage as SI

from abism.util import log, get_root, get_state, EA

import abism.back.util_back as W


def StrehlMeter(rectangle):
    """ Note : this should just be a caller
        this is the first written, strehlMeter for pick one,
        I putted more for ellipse and binary
    """

    W.strehl = {"theta": 99}
    ##########################
    # FIND   THE   CENTER  AND FWHM
    rectangle = IF.Order4(rectangle)
    # IF.FindBadPixel(get_state().image.im0,(rx1,rx2,ry1,ry2))
    star_center = IF.DecreasingGravityCenter(get_state().image.im0, r=rectangle)  # GravityCenter
    star_center = IF.FindMaxWithBin(get_state().image.im0, rectangle)  # GravityCenter
    tmp = IF.LocalMax(get_state().image.im0, center=star_center, size=3)
    star_max, star_center = tmp[2], (tmp[0], tmp[1])
    W.FWHM = IF.FWHM(get_state().image.im0, star_center)
    W.background = 0


    # Delegate fit
    ############################################################
    import time
    start_time = time.time()

    o_psf = SI.PsfFit(
        get_state().image.im0, rectangle,
        center=star_center, my_max=star_max)

    W.psf_fit = psf_fit = o_psf.do_fit().get_result()

    log(0, "Fit efectuated in %f seconds" % (time.time() - start_time))
    W.strehl.update(W.psf_fit[0])

    # Save what it take
    center = psf_fit[0]['center_x'], psf_fit[0]['center_y']
    get_state().add_answer(EA.CENTER, center)


    intensity = psf_fit[0]['intensity']
    get_state().add_answer(EA.INTENSITY, intensity)

    # Get Background && SAve
    back_dic = SI.Background(get_state().image.im0, rectangle)
    background = back_dic['my_background']
    rms = back_dic['rms']
    get_state().add_answer(EA.BACKGROUND, background)
    get_state().add_answer(EA.NOISE, rms)

    # Get photometry && Save
    photometry, _, number_count = \
        SI.Photometry(get_state().image.im0, background, rectangle=rectangle)
    get_state().add_answer(EA.PHOTOMETRY, photometry)

    # Get Signal on noise && Save
    signal_on_noise = photometry / background / np.sqrt(number_count)
    get_state().add_answer(EA.SN, signal_on_noise)

    # Save:  Side effect of course
    save_fwhm()

    # Math
    StrehlRatio()
    StrehlError()


def StrehlRatio():
    # Read from global
    bessel_integer = get_bessel_integer()
    photometry = get_state().get_answer(EA.PHOTOMETRY)
    intensity = get_state().get_answer(EA.INTENSITY)
    wavelength = get_root().header.wavelength

    # Get theoretical intensity && Save
    Ith = photometry / bessel_integer
    get_state().add_answer(EA.INTENSITY_THEORY, Ith)

    # Save strehl (finally)
    strehl = intensity / Ith
    get_state().add_answer(EA.STREHL, 100 * strehl, unit=' %')

    # Save equivalent Strehl ratio
    strehl_eq = get_equivalent_strehl_ratio(strehl, wavelength)
    get_state().add_answer(EA.STREHL_EQ, 100 * strehl_eq, unit=' %')

    # Save
    W.strehl["Ith"] = Ith  # used for error
    W.strehl["bessel_integer"] = bessel_integer   # used for error


def get_bessel_integer():
    """Read wavelenght, pixel_scale, diameter, obstruction"""
    bessel_integer = get_root().header.wavelength * \
        10**(-6.) / np.pi / (get_root().header.pixel_scale/206265) / get_root().header.diameter
    bessel_integer = bessel_integer**2 * 4 * \
        np.pi / (1-(get_root().header.obstruction/100)**2)
    return bessel_integer


def StrehlError():
    """after strehl , number count , background, center_x, and center_y"""
    dics = W.strehl
    # Get in
    # TODO refactor
    Sr = get_state().get_answer(EA.STREHL)
    Ith, bessel_integer = dics["Ith"], dics['bessel_integer']

    # Background
    dBack = W.strehl["rms"]

    # PHOTOMETRY
    dPhot = dBack * np.sqrt(W.strehl["number_count"])

    # if get_state().picka_type != "ellipse": the ellipse was doing the aperture
    get_state().phot_type = "fit"
    log(3, "\n\n WARNING: StrehlError changed the aperture type "
           "to fit because not ellipse pick it shouldn't matter ")

    # INTENSITY
    if get_state().phot_type and get_state().fit_type != "None":
        dI = W.psf_fit[1]["intensity"]
    else:
        x0, y0 = int(W.strehl["center_x"]), int(W.strehl["center_y"])
        mean = np.mean(get_state().image.im0[x0-1:x0+2, y0-1:y0+2])
        dI = (W.strehl["intensity"] - mean)
        dI /= 2

    dIpsf = np.sqrt(dI**2 + dBack**2)  # error from peak
    dIth = dPhot/bessel_integer           # error from phot
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
    fwhm_a = max(W.strehl["fwhm_x"], W.strehl["fwhm_y"])
    fwhm_b = min(W.strehl["fwhm_x"], W.strehl["fwhm_y"])
    fwhm_e = np.sqrt(fwhm_a**2 - fwhm_b**2) / fwhm_a
    get_state().add_answer(EA.FWHM_ABE, (fwhm_a, fwhm_b, fwhm_e))


def BinaryStrehl(star1, star2):
    binary_psf = SI.BinaryPsf(get_state().image.im0, star1, star2)
    W.psf_fit = binary_psf.do_fit().get_result()
    W.strehl = W.psf_fit[0]


def TightBinaryStrehl(star1, star2):
    tight_psf = SI.TightBinaryPsf(get_state().image.im0, star1, star2)
    W.psf_fit = tight_psf.do_fit().get_result()
    W.strehl = W.psf_fit[0]


def EllipseEventStrehl(ellipse):
    """Main ellipse worker,
    Param: ellipse artist with ru, rv, position
    """
    W.strehl = {}
    if get_state().phot_type == "fit":
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
    # TODO refactor StrehlError lying on W.strehl
    #StrehlError()


def get_equivalent_strehl_ratio(strehl, wavelength):
    """Get equivalent Strehl ration at 2.17"""
    if strehl < 0:
        factor = 0
    else:
        factor = wavelength / 2 / np.pi * np.sqrt(-np.log(strehl))

    factor = - (factor * 2 * np.pi / 2.17)**2

    return np.exp(factor)

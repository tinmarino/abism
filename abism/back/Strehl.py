"""
    Strehl meter
"""
import numpy as np

from abism.back import ImageFunction as IF
from abism.back import StrehlImage as SI

from abism.util import log, get_root, get_state, EA

import abism.back.util_back as W


def StrehlMeter():  # receive W.r, means a cut of the image
    """ Note : this should just be a caller
        this is the first written, strehlMeter for pick one,
        I putted more for ellipse and binary
    """

    W.strehl = {"theta": 99}
    ##########################
    # FIND   THE   CENTER  AND FWHM
    W.r = IF.Order4(W.r)
    # IF.FindBadPixel(get_state().image.im0,(rx1,rx2,ry1,ry2))
    star_center = IF.DecreasingGravityCenter(get_state().image.im0, r=W.r)  # GravityCenter
    star_center = IF.FindMaxWithBin(get_state().image.im0, W.r)  # GravityCenter
    tmp = IF.LocalMax(get_state().image.im0, center=star_center, size=3)
    star_max, star_center = tmp[2], (tmp[0], tmp[1])
    W.FWHM = IF.FWHM(get_state().image.im0, star_center)
    W.background = 0

    # Delegate fit
    import time
    start_time = time.time()

    W.psf_fit = psf_fit = SI.PsfFit(
        get_state().image.im0, center=star_center,
        max=star_max)

    log(0, "Fit efectuated in %f seconds" % (time.time() - start_time))
    W.strehl.update(W.psf_fit[0])

    # Save what it take
    intensity = psf_fit[0]['intensity']
    get_state().add_answer(EA.INTENSITY, intensity)

    # Get Background && SAve
    back_dic = SI.Background(get_state().image.im0)
    background = back_dic['my_background']
    rms = back_dic['rms']
    get_state().add_answer(EA.BACKGROUND, background)
    get_state().add_answer(EA.NOISE, rms)

    # Get photometry && Save
    photometry, _, number_count = \
        SI.Photometry(get_state().image.im0, background)
    get_state().add_answer(EA.PHOTOMETRY, photometry)

    # Get Signal on noise && Save
    signal_on_noise = photometry / background / np.sqrt(number_count)
    get_state().add_answer(EA.SN, signal_on_noise)

    # Save:  Side effect of course
    save_fwhm()

    bessel_integer = get_bessel_integer()

    # Get theoretical intensity && Save
    Ith = photometry / bessel_integer
    get_state().add_answer(EA.INTENSITY_THEORY, Ith)

    # Get strehl (finally)
    strehl = intensity / Ith * 100

    # Save
    get_state().add_answer(EA.STREHL, strehl, unit=' %')
    W.strehl["Ith"] = Ith  # used for error
    W.strehl["bessel_integer"] = bessel_integer   # used for error

    StrehlError()


def get_bessel_integer():
    """From image statistics"""
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

    if get_state().pick_type != "ellipse":
        get_state().aperture_type = "fit"
        log(3, "\n\n WARNING: StrehlError changed the aperture type "
               "to fit because not ellipse pick it shouldn't matter ")
    # INTENSITY
    if get_state().aperture_type and get_state().fit_type != "None":
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



def save_fwhm():
    """Save (Long, Short axe, Excentricity)"""
    fwhm_a = max(W.strehl["fwhm_x"], W.strehl["fwhm_y"])
    fwhm_b = min(W.strehl["fwhm_x"], W.strehl["fwhm_y"])
    fwhm_e = np.sqrt(fwhm_a**2 - fwhm_b**2) / fwhm_a
    get_state().add_answer(EA.FWHM_ABE, (fwhm_a, fwhm_b, fwhm_e))


def BinaryStrehl(star1, star2):
    binary_psf = SI.BinaryPsf(get_state().image.im0, star1, star2)
    W.psf_fit = binary_psf.get_result()
    W.strehl = W.psf_fit[0]


def TightBinaryStrehl(star1, star2):
    W.psf_fit = SI.TightBinaryPsf(get_state().image.im0, star1, star2)
    W.strehl = W.psf_fit[0]


def EllipseEventStrehl():
    W.strehl = {}
    if get_state().aperture_type == "fit":
        return

    else:  # including aperture = ellipse you've drawn
        SI.EllipseEventBack()  # Update
        # TODO bass background instead of global
        # TODO brefore:  check if used
        SI.EllipseEventPhot()  # Update  with ellipse, number count needed
        SI.EllipseEventMax()  # Update
        StrehlRatio()
        StrehlError()
        return


def get_equivalent_strehl_ratio(strehl, wavelength):
    """Get equivalent Strehl ration at 2.17"""
    if strehl < 0:
        factor = 0
    else:
        factor = wavelength / 2 / np.pi * np.sqrt(-np.log(strehl))

    factor = - (factor * 2 * np.pi / 2.17)**2

    return 100 * np.exp(factor)

import numpy as np
import multiprocessing
from threading import Thread

#from timeout import timeout
import ImageFunction as IF
import AnswerReturn as AR
import StrehlImage as SI
import scipy.ndimage

import GuyVariables as G
import WorkVariables as W


def StrehlRatio():  # read W.strehl ["my_photometry"], ["intensity"]
    """ and wavelgnth , pixel_scale, obstruciton, diameter """
    bessel_integer = W.head.wavelength * \
        10**(-6.) / np.pi / (W.head.pixel_scale/206265) / W.head.diameter
    bessel_integer = bessel_integer**2 * 4 * \
        np.pi / (1-(W.head.obstruction/100)**2)
    Ith = W.strehl["my_photometry"] / bessel_integer  # for I theory
    strehl = W.strehl["intensity"] / Ith * 100

    # SAve
    W.strehl["strehl"] = strehl
    W.strehl["Ith"] = Ith  # used for error
    W.strehl["bessel_integer"] = bessel_integer   # used for error


def StrehlError():  # after strehl , number count , background, center_x, and center_y
    dics = W.strehl
    Ith, Sr, bessel_integer = dics["Ith"],  dics['strehl'], dics['bessel_integer']

    # BACKGROUND
    dBack = W.strehl["rms"]

    # PHOTOMETRY
    dPhot = dBack * np.sqrt(W.strehl["number_count"])

    if W.type["pick"] != "ellipse":
        W.type["aperture"] = "fit"
        W.log(3, "\n\n WARNING: StrehlError changed the aperture type "
              "to fit because not ellipse pick it shouldn't matter ")
    # INTENSITY
    if W.type["aperture"] and W.type["fit"] != "None":
        dI = W.psf_fit[1]["intensity"]
    else:
        x0, y0 = int(W.strehl["center_x"]), int(W.strehl["center_y"])
        mean = np.mean(W.Im0[x0-1:x0+2, y0-1:y0+2])
        dI = (W.strehl["intensity"] - mean)
        dI /= 2

    dIpsf = np.sqrt(dI**2 + dBack**2)  # error from peak
    dIth = dPhot/bessel_integer           # error from phot
    dSr = np.sqrt(dIpsf**2 + (Sr/100 * abs(dIth))**2)
    dSr /= Ith
    dSr *= 100

    W.strehl["err_strehl"] = dSr * 3  # because I calculated the best error
    # "for  i in locals() :
    return


def StrehlMeter():  # receive W.r, means a cut of the image
    """ Note : this should just be a caller
       this is the first written, strehlMeter for pick one,
        I putted more for ellipse and binary
    """
    W.strehl = {"theta": 99}
    ##########################
    # FIND   THE   CENTER  AND FWHM
    W.r = IF.Order4(W.r)
    # IF.FindBadPixel(W.Im0,(rx1,rx2,ry1,ry2))
    star_center = IF.DecreasingGravityCenter(W.Im0, r=W.r)  # GravityCenter
    star_center = IF.FindMaxWithBin(W.Im0, W.r)  # GravityCenter
    tmp = IF.LocalMax(W.Im0, center=star_center, size=3)
    star_max, star_center = tmp[2], (tmp[0], tmp[1])
    W.FWHM = IF.FWHM(W.Im0, star_center)
    W.background = 0

    ######################
    #  FIT   the PSF            (the most important of the software)
    import time
    start_time = time.time()
    dictionary = {'NoiseType': W.type["noise"], 'PhotType': W.type["phot"],
                  'FitType': W.type["fit"], "bpm": W.Im_bpm}

    # @timeout(15)
    def FIT():
        W.psf_fit = SI.PsfFit(W.Im0, center=star_center,
                              max=star_max, dictionary=dictionary)
    FIT()
    W.log(0, "Fit efectuated in %f seconds" % (time.time() - start_time))

    W.strehl.update(W.psf_fit[0])

    ### phot and noise
    W.strehl.update(SI.Background(W.Im0))
    W.strehl.update(SI.Photometry(W.Im0))

    StrehlRatio()
    StrehlError()

    return


def BinaryStrehl():
    W.psf_fit = SI.BinaryPsf(W.Im0)
    W.strehl = W.psf_fit[0]


def TightBinaryStrehl():
    W.psf_fit = SI.TightBinaryPsf(W.Im0)
    W.strehl = W.psf_fit[0]


def EllipseEventStrehl():
    W.strehl = {}
    if W.type["aperture"] == "fit":
        return

    else:  # including aperture = ellipse you've drawn
        SI.EllipseEventBack()  # Update
        SI.EllipseEventPhot()  # Update  with ellipse, number count needed
        SI.EllipseEventMax()  # Update
        StrehlRatio()
        StrehlError()
        return

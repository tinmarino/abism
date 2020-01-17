import numpy as np
from matplotlib import pyplot as plt
from scipy.special import jn

from util import log

##########################
##   BINARY   STARS      #
##########################


def Gaussian2pt(points, params, dic={"aniso": 1, "same_psf": 1}):
    x, y = points
    x0, y0 = params['x0'], params['y0']
    x1, y1 = params['x1'], params['y1']
    I0, I1 = params['intensity0'], params['intensity1']
    bck = params['background']

    if dic["aniso"] == 0:
        a0, a1 = params['spread_x0'], params['spread_x1']
        if dic["same_psf"] == 1:
            res = I0*np.exp(- ((x-x0)**2+(y-y0)**2)/a0**2) + \
                I1*np.exp(- ((x-x1)**2+(y-y1)**2)/a0**2) + bck
        else:  # including same_fit =0
            res = I0*np.exp(- ((x-x0)**2+(y-y0)**2)/a0**2) + \
                I1*np.exp(- ((x-x1)**2+(y-y1)**2)/a1**2) + bck

    else:  # including aniso =1
        a0x, a1x = params['spread_x0'], params['spread_x1']
        a0y, a1y = params['spread_y0'], params['spread_y1']

        x0p = (x-x0)*np.cos(params['theta'])-(y-y0)*np.sin(params['theta'])
        y0p = (x-x0)*np.sin(params['theta'])+(y-y0)*np.cos(params['theta'])

        x1p = (x-x1)*np.cos(params['theta'])-(y-y1)*np.sin(params['theta'])
        y1p = (x-x1)*np.sin(params['theta'])+(y-y1)*np.cos(params['theta'])

        if dic["same_psf"] == 1:
          #           xp(-(xp**2/params['spread_x']**2+yp**2/params['spread_y']**2))
            res = I0*np.exp(- (x0p/a0x)**2 - (y0p/a0y)**2) + \
                I1*np.exp(- (x1p/a0x)**2 - (y1p/a0y)**2) + bck
        else:  # including same_fit =0
            res = I0*np.exp(- (x0p/a0x)**2 - (y0p/a0y)**2) + \
                I1*np.exp(- (x1p/a1x)**2 - (y1p/a1y)**2) + bck
    return res


def Moffat2pt(points, params, dic={"aniso": 1, "same_psf": 1}):
    x, y = points
    x0, y0 = params['x0'], params['y0']
    x1, y1 = params['x1'], params['y1']
    I0, I1 = params['intensity0'], params['intensity1']
    try:
        bck = params['background']
    except:
        bck = 0

    if not dic["aniso"]:        # Circular psf
        a0, a1 = params['spread_x0'], params['spread_x1']
        b0, b1 = params['b0'], params['b1']
        if dic["same_psf"] == 1:  # here we don't fit a1 nor b1
            res = I0 * (1 + ((x-x0)**2+(y-y0)**2)/a0**2)**(-b0)
            res += I1 * (1 + ((x-x1)**2+(y-y1)**2)/a0**2)**(-b0)+bck
        else:                     # including different psf
            res = I0 * (1 + ((x-x0)**2+(y-y0)**2)/a0**2)**(-b0)
            res += I1 * (1 + ((x-x1)**2+(y-y1)**2)/a1**2)**(-b1) + bck

    else:  # including anisoplanetism
        a0x, a1x = params['spread_x0'], params['spread_x1']
        a0y, a1y = params['spread_y0'], params['spread_y1']
        b0, b1 = params['b0'], params['b1']

        x0p = (x-x0)*np.cos(params['theta'])-(y-y0)*np.sin(params['theta'])
        y0p = (x-x0)*np.sin(params['theta'])+(y-y0)*np.cos(params['theta'])

        x1p = (x-x1)*np.cos(params['theta'])-(y-y1)*np.sin(params['theta'])
        y1p = (x-x1)*np.sin(params['theta'])+(y-y1)*np.cos(params['theta'])

        if dic["same_psf"] == 1:
            res = I0 * (1 + (x0p**2/a0x**2 + y0p**2/a0y**2))**(-b0)
            res += I1 * (1 + (x1p**2/a0x**2 + y1p**2/a0y**2))**(-b0) + bck
        else:      # including same_fit =0
            res = I0 * (1 + (x0p**2/a0x**2 + y0p**2/a0y**2))**(-b0)
            res += I1 * (1 + (x1p**2/a1x**2 + y1p**2/a1y**2))**(-b1)+bck
    return res

    ####################
    ## PSF SINGLE STAR #
    # "

##########
# GAUSSIAN


def Gaussian(points, params):  # param contains   center, spread, amplitude, background
    ""
# max = I(+cst) ; integral = pi I alpha**2  (sure)
# R99 = 2.14 * alpha
    x, y = points
    x0 = params['center_x']
    y0 = params['center_y']
    a = params['spread_x']
    I = params['intensity']
    cst = params['background']
    res = I * np.exp(- ((x-x0)**2+(y-y0)**2)/a**2) + cst
    return res


def Gaussian2D(xy, params):
    """params: center_x,center_y,theta,backgroudn,intensity,spread_x,spread_y """

    # prevent theta from rotating crazy return cst fct
    # if (params["theta"]<-0.1) :
    #   return xy*10 * (1+ np.log10(-params["theta"]) )
    # if (params["theta"]>3.24) :
    #   return xy*params["theta"] # *(1+ np.log10(params["theta"])  )
    #theta= params["theta"]%3.1415926

    xt = xy[0]
    yt = xy[1]
    # tested the next thing
    xp = (xt-params['center_x'])*np.cos(params['theta']) - \
        (yt-params['center_y'])*np.sin(params['theta'])
    yp = (xt-params['center_x'])*np.sin(params['theta']) + \
        (yt-params['center_y'])*np.cos(params['theta'])
    res = params['background']+params['intensity'] * \
        np.exp(-(xp**2/params['spread_x']**2+yp**2/params['spread_y']**2))
    return res


def Gaussian_hole(points, params):    # If there is a negative gaussian in the center, a hole
    xt, yt = points
    x0, y0, t = params['center_x'], params['center_y'], params['theta']
    if params["same_center"] == 1:
        x0h, y0h, th = x0, y0, t
    else:
        x0h, y0h, th = params['center_x_hole'], params['center_y_hole'], params['theta_hole']
    if params["2D"] == 0:
        params['spread_y'], params['spread_y_hole'] = params['spread_x'], params['spread_x_hole']

    xp = (xt-x0)*np.cos(t)-(yt-y0)*np.sin(t)
    yp = (xt-x0)*np.sin(t)+(yt-y0)*np.cos(t)
    xh = (xt-x0)*np.cos(th)-(yt-y0h)*np.sin(t)
    yh = (xt-x0)*np.sin(th)+(yt-y0h)*np.cos(t)
    res = params['background']+params['intensity'] * \
        np.exp(-(xp**2/params['spread_x']**2+yp**2/params['spread_y']**2))
    res -= params["intensity_hole"] * \
        np.exp(-(xh**2/params['spread_x_hole'] **
                 2+yp**2/params['spread_y_hole']**2))
    return res


###########
# MOFFAT
def Moffat(points, params):
    (x, y) = points
    x0 = params['center_x']
    y0 = params['center_y']
    a = params['spread_x']
    b = params['exponent']
    I = params['intensity']
    cst = params['background']

    res = I * (1 + ((x-x0)**2+(y-y0)**2)/a**2)**(-b) + cst
    return res


def Moffat2D(xy, params):
    """ center_x y theta , spread x , y ,
        exponent intensity, background
    """
    x0, y0 = params['center_x'], params['center_y']
    xt = xy[0]
    yt = xy[1]
    theta = params['theta']
    xp = (xt-x0)*np.cos(theta)-(yt-y0)*np.sin(theta)
    yp = (xt-x0)*np.sin(theta)+(yt-y0)*np.cos(theta)
    res = params['background']
    res += params['intensity']*(1 + xp**2/params['spread_x']
                                ** 2 + yp**2/params['spread_y']**2)**(-params['exponent'])
    return res


############
# BESSEL
def Bessel1(points, params):
    # the max is I the integer of [J1(x)/x] **2 is   pi  (sure)
    (x, y) = points
    x0 = params['center_x']
    y0 = params['center_y']
    a = params['spread_x']
    I = params['intensity']
    cst = params['background']
    # nb : r is directly divided by a
    r = np.sqrt(((x-x0)**2 + (y-y0)**2)/a**2)
    res = np.nan_to_num(2*jn(1, r)/r)**2 + np.float_(np.array(r) == 0)
    res = I*res
    return res


def Bessel12D(xy, params):
    xt = xy[0]
    yt = xy[1]
    xp = (xt-params['center_x'])*np.cos(params['theta']) - \
        (yt-params['center_y'])*np.sin(params['theta'])
    yp = (xt-params['center_x'])*np.sin(params['theta']) + \
        (yt-params['center_y'])*np.cos(params['theta'])
    # nb : r is directly divided by a
    r = np.sqrt(xp**2/params['spread_x']**2 + yp**2/params['spread_y']**2)
    res = np.nan_to_num((2*jn(1, r)/r)**2)
    res *= params['intensity']
    res += params['background']
    return res


def DiffractionPatern(points, params):
    from scipy.special import jn
    x0 = params['center_x']
    y0 = params['center_y']
    l = params['lambda']*10**(-6)  # wavelength
    p = params['phot']
    D = params['diameter']  # telescope diameter
    pxl = params['pixelscale']/206265
    e = params['obstruction']  # centralobstruction
    I = p * (1-e**2)/4/np.pi / (l/pxl/np.pi/D)**2
    theta = (points[0]-x0) * pxl
    u = np.pi/l * D * theta
    if not e == 0:  # otherwise division by 0
        # + np.float_(np.array(r)==0)
        res = np.nan_to_num((2*jn(1, u)/u - e**2 * 2*jn(1, e*u)/e/u)**2)
    else:
        res = np.nan_to_num((2*jn(1, u)/u)**2)
    res *= I/(1-e**2)**2
    return res

    ##########
    # USELESS STAFF
    ###########


##########
#
def LogScale(min, max, bin):
    res = np.zeros(())
    for i in range(1, bin+1):
        res[i] = min + 10**(i/bin)*(max-min)
    return res
# def moffat(


def AnnulusSize(ins, out):
    return (3.14*(out**2-ins**2))


def MultiAnnulusSize(x):  # take a 1d array  /RETURN: annulus entre i-1 y i
    lenght = len(x)
    tmp = np.zeros(lenght)
    res = np.zeros(lenght)
    for i in range(lenght):
        tmp[i] = np.pi*x[i]**2
        res[i] = tmp[i]
        if tmp[i-1]:
            res[i] -= tmp[i-1]
    return res

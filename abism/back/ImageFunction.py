"""
    ImageFunction works on array to separe matematics and graphics
"""
# pylint: disable = too-many-locals

import numpy as np
from scipy.ndimage import median_filter
import scipy.interpolate  # for LocalMax

from abism.back.image_info import get_array_stat
from abism.back.fit_template_function import Moffat2D

from abism.util import log, get_state, DotDic



def DoNotPassBorder(grid, point2d):
    """Ensure point is in image
    Arg: grid <- image
         pinrt2d <- x,y
    Returns: new point
    """
    x = point2d[0]
    y = point2d[1]
    if x < 0:
        x = 0
    elif x > grid.shape[0]:
        x = len(grid)
    if y < 0:
        y = 0
    elif y > grid.shape[1]:
        y = len(grid)
    return x, y


def Order4(r, grid=None, intify=False):
    """Returns (rxmin, rxmax, rymin, rymax)
    Arg: r      <- 4-tuple
         grid   <- to check bounds
         intify <- result items are integers
    """
    rx1, rx2, ry1, ry2 = r[0], r[1], r[2], r[3]
    if rx1 > rx2:
        rx1, rx2 = rx2, rx1
    if ry1 > ry2:
        ry1, ry2 = ry2, ry1
    rx1 = max(rx1, 0)
    ry1 = max(ry1, 0)
    if grid is not None:
        rx2 = min(rx2, len(grid)-1)
        ry2 = min(ry2, len(grid[0])-1)
    if intify:
        rx1, rx2, ry1, ry2 = list(map(int, [rx1, rx2, ry1, ry2]))
    return (rx1, rx2, ry1, ry2)


def LocalMax(grid, center=None, size=10, r=None, type="interpolation"):
    """Returns: maximum in a circle of `size` around `center` in `grid`
    type = "gravity"       # gravity center of the 3*3 box
           "interpolation" # interpolation of the 5*5
    With bad pixel filter
    """
    # INIT R
    if r is None:
        r = (center[0]-size, center[0]+size+1,
             center[1]-size, center[1]+size+1)

    # CUT
    bound_int = list(map(int, r))
    cut1 = grid[bound_int[0]:bound_int[1], bound_int[2]:bound_int[3]]

    # FILT BAd PIXELS
    mIX = scipy.ndimage.uniform_filter(cut1, size=(3, 3))
    bol1 = np.abs(cut1-mIX) > mIX
    cut1[bol1] = mIX[bol1]

    # 1st MAX
    coord1 = np.unravel_index(cut1.argmax(), cut1.shape)
    coord1 = (coord1[0] + r[0], coord1[1] + r[2])
    log(3, "LocalMax coord", coord1, r)

    # INTERPOLATE
    if type == "interpolation":
        xmin = int(max(0, coord1[0]-2))
        xmax = int(min(coord1[0]+3, len(grid)))
        ymin = int(max(0, coord1[1]-2))
        ymax = int(min(coord1[1]+3, len(grid[0])))
        x = np.arange(xmin, xmax)
        y = np.arange(ymin, ymax)
        cut2 = grid[xmin: xmax, ymin: ymax]
        log(3, "LocalMax shapes:", x.shape, y.shape,
            cut2.shape, xmin, xmax, ymin, ymax)
        interp = scipy.interpolate.interp2d(x, y, cut2, kind="cubic")

        xx = np.arange(xmin, xmax, 0.1)
        yy = np.arange(ymin, ymax, 0.1)
        zz = interp(xx, yy)

        # 2nd Max
        coord2 = np.unravel_index(zz.argmax(), zz.shape)
        log(3, "coord, cut ", coord2, cut2)
        res = xx[coord2[0]],  yy[coord2[1]], zz[coord2[0], coord2[1]]

    # GRAVITY CENTER
    else:  # including type == gravity
        xmin = max(0, coord1[0]-1)
        xmax = min(coord1[0]+2, len(cut1))
        ymin = max(0, coord1[1]-1)
        ymax = min(coord1[1]+2, len(cut1[0]))
        x = np.arange(xmin, xmax)
        y = np.arange(ymin, ymax)
        cut2 = cut1[xmin: xmax, ymin: ymax]
        X, Y = np.meshgrid(x, y)
        norm = np.sum(cut2)
        coord2 = np.sum(X*cut1) / norm, np.sum(Y * cut1) / norm
        log(3, "coord1, cut ", coord2, cut2)
        res = coord2[0]+r[0],  coord2[1]+r[2],  cut2[coord2[0], coord2[1]]

    log(3, " LocalMax@ImageFunction.py : ", res)
    return res


def FindMaxWithBin(grid, rectangle):
    """arg =  grid and r : 3*3 median filter
    """
    r = rectangle
    cutted = grid[r[0]:r[1], r[2]:r[3]]
    # Median file 3 x 3 (fuzz)
    cutted = median_filter(cutted, size=(3, 3))
    # Get peak
    coord = np.unravel_index(cutted.argmax(), cutted.shape)

    # return x,y
    return coord[0]+r[0], coord[1]+r[2]


# Find one of the half Maximum without precision  in direction (x,-x,y,-y)
def FWHM(grid, centermax, direction='average'):
    (x, y) = centermax  # center should be the max pixel.
    i, j = int(x), int(y)       # RETURN  float
    max2 = grid[i, j]/2
    if direction == 'average':
        res = FWHM(grid, centermax, direction='x')
        res += FWHM(grid, centermax, direction='-x')
        res += FWHM(grid, centermax, direction='y')
        res += FWHM(grid, centermax, direction='-y')
        res /= 4
        return res + 0.5
    else:
        while (grid[i][j] > max2):
            log(3, 'FWHM :i,j,I=', i, j, grid[i][j], direction)
            if direction == 'x':
                i += 1
            if direction == '-x':
                i -= 1
            if direction == 'y':
                j += 1
            if direction == 'z':
                j -= 1
            if grid[i][j] > grid[int(x)][int(y)]/2:
                break
        fwhm = np.sqrt((j-y)**2+(i-x)**2)*2
        log(3, "FWHM2:", fwhm)
        return fwhm


def PixelMax(grid, r=None):
    """array.float , 2 float , 1 float     RETURN center, max (=2+1floats)
    TODO merge with find_max
    """
    if r is None:
        r = 0, len(grid), 0, len(grid[0])
    cut1 = grid[r[0]: r[1], r[2]: r[3]]
    x, y = np.unravel_index(cut1.argmax(), cut1.shape)
    return (r[0]+x, r[2] + y), cut1[x, y]


def EnergyRadius(grid, dic={}):
    """We first define r99u and v following the spread direction
    x and y respectively, but these are arbitrary due to the fit
    we then transfroms it to r99x and R99y
    Returns: (r99uv), (r99xy)
    """
    params = dic  # because no update
    s_fit_type = get_state().s_fit_type
    aniso = get_state().b_aniso

    ############
    # GAUSSIAN
    if s_fit_type == 'Gaussian':
        # 2.14 for 99% energy, we ll use pi
        r99u = np.pi * params['spread_x']
        if aniso:
            r99v = np.pi * params['spread_y']
        else:
            r99v = np.pi * params['spread_x']

    ###############
    # MOFFAT
    if 'Moffat' in s_fit_type:
        # r99 = r90
        # r99u= params['spread_x'] * np.sqrt( (1-%)**(1/(1-params['exponent'])) -1 )
        ap = 5  # 5 times the spread, for aperture,
        if params["exponent"] < 1:
            ap = 10
        elif params["exponent"] > 3:
            if params["exponent"] > 4:
                if params["exponent"] > 10:
                    ap = 1.
                else:
                    ap = 3.
            else:
                ap = 4.
        if aniso:
            # r99 = r90
            r99u, r99v = params['spread_x'] * ap, params['spread_y'] * ap
        else:
            r99v, r99u = params['spread_x'] * ap,  params['spread_x'] * ap

    ############
    # BESSEL and None
    if s_fit_type == 'Bessel1':
        # take cara r99 = R90
        r99u = 5.8 * params['spread_x']
        r99v = 5.8 * params['spread_x']
    if (s_fit_type == 'Bessel12D'):
        # take cara r99 = R90
        r99u = 5.8 * params['spread_x']
        r99v = 5.8 * params['spread_y']
    if (s_fit_type == 'None'):
        r99u, r99v = params["r99x"],  params["r99y"]

    ###########
    # r99x and r99y  ROTATE
    if 'theta' in params:
        r99x = r99u * abs(np.cos(params["theta"])) + \
            r99v * abs(np.sin(params["theta"]))
        r99y = r99u * abs(np.sin(params["theta"])) + \
            r99v * abs(np.cos(params["theta"]))
    else:
        r99x, r99y = r99u, r99v

    log(3, "------>EnergyRadius(ImageFunction.py)->", (r99x, r99y))
    return (r99x, r99y), (r99u, r99v)


def FwhmFromFit(fit_dic, err_dic):
    """And phot  all explicit
    Return a_phot, a_fwhm_x, a_fwhm_y type answer lum and distance
    Note: could be rename integral:
    Gauss: ∫e^(-x²/a²)  = πa²
    Moffat: ∫(1+x²)^-b  = πa² / (b-1)
    """
    from abism.answer import AnswerLuminosity, AnswerDistance, AnswerNum
    s_fit_type = get_state().s_fit_type

    a_phot = AnswerLuminosity('Helper', 1, error=0)
    a_fwhm_x = AnswerDistance('Helper', 1, error=0)
    a_fwhm_y = AnswerDistance('Helper', 1, error=0)

    a_spread_x = AnswerDistance('Helper', fit_dic['spread_x'], error=err_dic['spread_x'])
    a_spread_y = AnswerDistance('Helper', fit_dic['spread_y'], error=err_dic['spread_y'])
    a_intensity = AnswerNum('Helper', fit_dic['intensity'], error=err_dic['intensity'])

    # Gaussian
    if 'Gaussian' in s_fit_type:
        """2 * sqrt( log(2) ) = 1.6651092223153954"""
        a_phot *= a_intensity * np.pi * a_spread_x * a_spread_y
        a_fwhm_x = 1.66510922 * a_spread_x
        a_fwhm_y = 1.66510922 * a_spread_y

    # Moffat
    elif "Moffat" in s_fit_type:
        a_exponent = AnswerNum('Helper', fit_dic['exponent'], error=err_dic['exponent'])
        if fit_dic['exponent'] > 1:
            a_phot *= a_intensity * np.pi * a_spread_x * a_spread_y
            a_phot /= a_exponent - 1
        else:
            # TODO cleaner with error
            x = np.arange(int(fit_dic["center_x"] - 50),
                          int(fit_dic["center_x"] + 50+1))
            y = np.arange(int(fit_dic["center_y"] - 50),
                          int(fit_dic["center_y"] + 50+1))
            Y, X = np.meshgrid(x, y)
            cut = Moffat2D((X, Y), fit_dic)
            a_phot *= np.sum(cut)

        a_fwhm_x = 2 * abs(a_spread_x) * np.sqrt((0.5)**(-1 / a_exponent) - 1)
        a_fwhm_y = 2 * abs(a_spread_y) * np.sqrt((0.5)**(-1 / a_exponent) - 1)

    # Bessel
    elif 'Bessel1' in s_fit_type:
        a_phot *= 4 * np.pi * a_intensity * a_spread_x * a_spread_y
        a_fwhm_x = 2 * a_spread_x * 1.61
        a_fwhm_y = 2 * a_spread_y * 1.61

    # None
    else:
        a_phot *= 0
        a_fwhm_x = 2 * a_spread_x * 1.61
        a_fwhm_y = 2 * a_spread_y * 1.61


    log(3, 'Fit: photometry, estimated from', s_fit_type, 'is', a_phot)
    return a_phot, a_fwhm_x, a_fwhm_y


def EightRectangleNoise(grid, r, return_rectangle=0, dictionary={'size': 4, 'distance': 1}):
    """Derive the noise from eight rectangle (of R/2 ) around the 99% Energy
    size =4 means that we devide by  4 the size of the rectangle
    distance = 2 means we go father by a factor 2 for star center (r center)
    we suppose order in r
    """
    rx1, rx2, ry1, ry2 = r
    distance, size = dictionary['distance'], dictionary['size']
    rx1, rx2 = rx1 - distance*(rx2-rx1)/2, rx2 + distance*(rx2-rx1)/2
    ry1, ry2 = ry1 - distance*(ry2-ry1)/2, ry2 + distance*(ry2-ry1)/2
    p = []
    rx, ry, background, rms = (
        rx2-rx1)/2/distance/size, (ry2-ry1)/2/distance/size, [], []  # we search the noise
    for i in ['NW', 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W']:
        if i == 'NW':
            # we define 8 boxes of noise
            (ax1, ax2, ay1, ay2) = (rx1-rx, rx1, ry2, ry2+ry)
        if i == 'N':
            (ax1, ax2, ay1, ay2) = ((rx1+rx2)/2 -
                                    rx/2, (rx1+rx2)/2+rx/2, ry2, ry2+ry)
        if i == 'NE':
            (ax1, ax2, ay1, ay2) = (rx2, rx2+rx, ry2, ry2+ry)
        if i == 'E':
            (ax1, ax2, ay1, ay2) = (rx2, rx2+rx,
                                    (ry1+ry2)/2-ry/2, (ry1+ry2)/2+ry/2)
        if i == 'SE':
            (ax1, ax2, ay1, ay2) = (rx2, rx2+rx, ry1-ry, ry1)
        if i == 'S':
            (ax1, ax2, ay1, ay2) = ((rx1+rx2)/2 -
                                    rx/2, (rx1+rx2)/2+rx/2, ry1-ry, ry1)
        if i == 'SW':
            (ax1, ax2, ay1, ay2) = (rx1-rx, rx1, ry1-ry, ry1)
        if i == 'W':
            (ax1, ax2, ay1, ay2) = (rx1-rx, rx1,
                                    (ry1+ry2)/2-ry/2, (ry1+ry2)/2+ry/2)
        image_cut = grid[int(ax1): int(ax2+1), int(ay1): int(ay2+1)]
        background.append(np.mean(image_cut))
        rms.append(np.std(image_cut))
        log(3, "8rects: Background, rms :", background[-1], rms[-1])
        if return_rectangle:  # we draw the rectangles
            center, width, height = (
                ((ax1+ax2)/2, (ay1+ay2)/2), (ax2-ax1), (ay2-ay1))
            p.append((center, width, height))
    background.sort()
    background = np.mean(background[2:6])
    rms = np.median(rms)
    log(3, '----->8rectsbackground', background)
    if return_rectangle:
        return background, 'uselesse', p
    return {'background': background, 'rms': rms}


def find_bad_pixel(grid, r=None):
    """Compare with the median filter
    Verbose: In the method we define in arg1 the number of pixel to include in the median
    and in arg2, the max differnce between true image and median
    the bad pixels can be noise or warm pixel
    :param r: ordered rectangle bounds to cut grid
    """
    # Parse in: Cut grid if requested
    if r is None:
        IX = grid
    else:
        rx1, rx2, ry1, ry2 = r
        IX = grid[rx1:rx2, ry1:ry2]
    res, mIX = IX, IX

    # Filter infs and nan
    nan = np.isnan(res)
    inf = np.isinf(res)
    res[nan] = 0
    mIX[nan] = 0
    res[inf] = 0
    mIX[inf] = 0

    # Median filter bad pixels
    mIX = median_filter(IX, size=(3, 3))
    b_bad = np.abs(IX - mIX) > np.abs(mIX)
    res[b_bad] = mIX[b_bad]  # Almost useless becaused masked

    # Finally error
    eIX = (IX-mIX).std() * np.ones(IX.shape)
    b_ignore = np.logical_or(nan, inf)
    b_ignore = np.logical_or(b_ignore, b_bad)
    eIX[b_ignore] = float('inf')

    return res, mIX, eIX


def project_on_radial_line(point1_n_point2, point):
    """Return sbscisse of point projected on line between point1_n_point2"""
    # Tuple unpack in
    (x1, y1), (x2, y2) = point1_n_point2
    x, y = point

    # get line lenght
    length = (x2 - x1)**2 + (y2 - y1)**2
    length = np.sqrt(length)

    # Project
    res = (x - x1) * (x2 - x1) + (y - y1) * (y2 -y1)
    res /= length
    return res


def get_radial_line(grid, point1_and_point2, return_point=0):
    """Returns profile one a line: 2 vectors x and y
    Param: return_point, boolean if callr want point (usually yes)
    """
    # Parse in
    (x1, y1), (x2, y2) = point1_and_point2

    # Calculate line lenght
    vect_r = ((x2-x1), (y2-y1))
    lenght = np.sqrt(vect_r[1]**2+vect_r[0]**2)

    # Get the extreme points of the line on grid
    xmin, xmax, ymin, ymax = Order4((x1, x2, y1, y2), grid=grid)
    xmin, xmax, ymin, ymax = int(xmin), int(xmax), int(ymin), int(ymax)

    x, y = np.arange(xmin, xmax), np.arange(ymin, ymax)
    Y, X = np.meshgrid(y, x)
    array = grid[xmin:xmax, ymin:ymax]

    # Radial array, cos of scalar product
    R = ((X-x1)*(x2-x1) + (Y-y1)*(y2-y1)) / lenght
    # Sin of scalar product
    # the distance of (X,Y) to x1,y1 projected on the line
    d = (R*(x2-x1)/lenght-(X-x1))**2 + (R*(y2-y1)/lenght-(Y-y1))**2

    # Flaten all
    # the square distance of the point from the line
    R, d, array = R.flatten(), d.flatten(), array.flatten()
    X, Y = X.flatten(), Y.flatten()
    ab, od = np.zeros(len(array)), np.zeros(len(array))

    ab[d < 0.25] = R[d < 0.25]   # ab like abscisse
    od[d < 0.25] = array[d < 0.25]
    X, Y = X[d < 0.25], Y[d < 0.25]

    # good idea also :  od = [od for (Y,od) in sorted(zip(Y,od))]
    # Remove zeros
    ab = ab[od.nonzero()]  # why do we have so many zero ?
    od = od[od.nonzero()]  # think, but it works
    res = sorted(zip(ab, od))
    res = np.array(res)
    #res[np.abs(IX-mIX)>(method[2]-1)*mIX] = mIX[np.abs(IX-mIX)>(method[2]-1)*mIX]

    if return_point:
        X, Y = X[od.nonzero()], Y[od.nonzero()]
        res2 = sorted(zip(ab, X, Y))
        res2.sort()
        res2 = np.array(res2)
        # abscice ordonate, points in array
        return res[:, 0], res[:, 1], (res2[:, 1].astype("int"), res2[:, 2].astype("int"))

    return res[:, 0], res[:, 1]  # abscice ordonate


def get_profile_x(grid, center):
    """Get profile along X
    Note: only used onces in AnswerReturn
    """
    r = (0, len(grid)-1, 0, len(grid[0]) - 1)
    r = Order4(r)
    x = np.arange(int(r[0]), int(r[1])+1)
    y = grid[int(r[0]):int(r[1])+1, int(center[1])]
    return x, y


def correct_bad_pixel(grid):
    """Smooth bad pixel <- Filter median"""
    median = median_filter(grid, size=(3, 3))
    bol = np.abs(grid - median) > 3 * np.abs(median)
    grid[bol] = median[bol]
    return grid


def get_elliptical_aperture(grid, center=None, uv=None, theta=None):
    """Returns a bol : grid[bol] <- you are in aperture"""
    # Check in
    if None in (center, uv, theta):
        log(-1, 'Error: get_elliptical_aperture wrong parameters')
        return DotDic()

    # Unpack in
    x0, y0 = center
    ru, rv = uv
    cos = np.cos(theta)
    sin = np.sin(theta)

    a = ((cos/ru)**2 + (sin/rv)**2)
    b = ((sin/ru)**2 + (cos/rv)**2)
    c = (np.sin(2 * theta) * (1./rv**2 - 1. / ru**2))

    x = np.arange(-x0, len(grid)-x0)  # invert IDK why
    y = np.arange(-y0, len(grid[0])-y0)

    # need to be in this order , tested with event ellipser!
    Y, X = np.meshgrid(y, x)

    bol = a*X**2 + b*Y**2 + c*X*Y < 1

    return bol

"""
    ImageFunction works on array to separe matematics and graphics
"""

import numpy as np
import scipy.ndimage  # for the median filter
import scipy.interpolate  # for LocalMax

from abism.back.image_info import get_array_stat
from abism.back.fit_template_function import Moffat2D

from abism.util import log, get_state



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


def Order2(a, b):
    """Returns (min, max)"""
    if a >= b: return (b, a)
    return (a, b)


def Order4(r, grid=None):
    """Returns (rxmin, rxmax, rymin, rymax)
    Arg: r <- 4-tuple
         grid <- to check bounds
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
    cut1 = grid[bound_int[0]:bound_int[1],  bound_int[2]:bound_int[3]]

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
        res = xx[coord2[0]],  yy[coord2[1]],  zz[coord2[0], coord2[1]]

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

    #res =  grid[coord[0],coord[1]],( float(coord[0])/100 +reindex[0], float(coord[1])/100 +reindex[1])

    log(3, " LocalMax@ImageFunction.py : ", res)
    return res


def GravityCenter(grid, center=None, rad=None, r=None, bol=None):
    # radius of a square    /RETURN: center , means (x,y)
    # bol is the bollean of teh selected pixels

    # 1/ Create Constants
    if r is None:
        (x0, y0) = int(center[0]), int(center[1])
        my_r = int(rad)
        rx1, rx2, ry1, ry2 = x0-my_r, x0+my_r, y0-myr, y0+my_r
        x = np.arange(-my_r, my_r+1)
        y = np.arange(-my_r, my_r+1)
    else:
        tmp = Order4(r)
        rx1, rx2, ry1, ry2 = int(tmp[0]),  int(
            tmp[1]), int(tmp[2]), int(tmp[3])
        x = np.arange(rx1, rx2+1)
        y = np.arange(ry1, ry2+1)

        # Create R, distance from x0,y0
    Y, X = np.meshgrid(y, x)
    #R =  np.sqrt( Y**2+ X**2 )

    # 2/ cut grid)
    cutted = grid[rx1:rx2+1, ry1:ry2+1]
    my_sum = np.sum(cutted)

    # 3/ get the gravity center
    x1 = np.sum(cutted*X) / my_sum
    y1 = np.sum(cutted*Y) / my_sum

    return (x1, y1)


def FindMaxWithBin(*arg):
    """arg =  grid and r : 3*3 median filter"""
    # Parse in
    grid = arg[0]
    if len(arg) == 1:
        r = 0, len(grid), 0, len(grid[0])
    else:
        r = arg[1]
    # Cut
    cutted = grid[int(r[0]):int(r[1]), int(r[2]):int(r[3])]
    # Median file 3 x 3 (fuzz)
    cutted = scipy.ndimage.median_filter(cutted, size=(3, 3))
    # Get peak
    coord = np.unravel_index(cutted.argmax(), cutted.shape)

    # return x,y
    return coord[0]+r[0], coord[1]+r[2]


def FindMaxWithIncreasingSquares(grid, center):  # center is th ecenter click
    size_max = 20
    return


# call with radius each time samller
def DecreasingGravityCenter(grid, r=None, binfact=2, radiusmin=4):
    """ Get the ce nter of gravity with decreasing squares around the previous gravity center """

    gravity_center = GravityCenter(grid, r=r)
    # need to do that to avoid error mess 'tuple' object do not support item assignment
    rx1, rx2, ry1, ry2 = r
    if r[1]-r[0] > radiusmin:
        dist = float((r[1]-r[0]))/2/binfact
        log(2, "DecreasingGravityCenter", "r", r)
        rx1 = int(gravity_center[0] - dist)
        rx2 = int(gravity_center[0] + dist)
    if r[3]-r[2] > radiusmin:
        dist = float((r[3]-r[2]))/2/binfact
        ry1 = int(gravity_center[1] - dist)
        ry2 = int(gravity_center[1] + dist)
    elif r[1]-r[0] <= radiusmin:  # now we can leave the function
        return gravity_center

    return DecreasingGravityCenter(grid, r=(rx1, rx2, ry1, ry2))


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


# point is the coord of the exact point you need to assess intensity from linear assuption of nearest pixels,  seems to be slow tooo
def PointIntensity(grid, point):
    res, M = 0, 0
    (x, y) = point
    (i, j) = (int(x), int(y))
    if ((i, j) == (x, y)):
        return grid[i][j]
    else:
        try:
            tmp = 1 / (np.sqrt((x-i)**2+(y-j)**2))
            res += grid[i][j] / (np.sqrt((x-i)**2+(y-j)**2))
            M += 1 / (np.sqrt((x-i)**2+(y-j)**2))
        except:
            pass
        try:
            tmp = 1 / (np.sqrt((x-(i+1))**2+(y-j)**2))
            res += grid[i+1][j]*tmp
            M += tmp
        except:
            pass
        try:
            tmp = 1 / (np.sqrt((x-i)**2+(y-(j+1))**2))
            res += grid[i][j+1]
            M += tmp
        except:
            pass
        try:
            tmp = 1 / (np.sqrt((x-(i+1))**2+(y-(j+1))**2))
            res += grid[i+1][j+1]
            M += tmp
        except:
            pass
    return res/M


def PixelMax(grid, r=None):   # array.float , 2 float , 1 float     RETURN center, max (=2+1floats)
    if r is None:
        r = 0, len(grid), 0, len(grid[0])
    cut1 = grid[r[0]: r[1], r[2]: r[3]]
    x, y = np.unravel_index(cut1.argmax(), cut1.shape)
    return (r[0]+x, r[2] + y), cut1[x, y]


def GoodPixelMax(grid, r=(10, 10, 10, 10)):   # array.float , 2 float , 1 float
    m, bad = 0, []  # m will be the maximum value of a pixel,bad are the BadPixels coord
    (rx1, rx2, ry1, ry2) = r
    for i in range(int(rx1), int(rx2+1)):
        for j in range(int(ry1), int(ry2+1)):
            if (i, j) in bad:
                pass
            else:
                try:  # in case we are out of the grid
                    if grid[i][j] > m:
                        m = grid[i][j]
                        (x, y) = (i, j)
                except:
                    pass
    if (grid[x-1][y] < grid[x][y]/10
        and grid[x][y-1] < grid[x][y]/10
        and grid[x+1][y] < grid[x][y]/10
            and grid[x][y+1] < grid[x][y]/10):
        bad.append((x, y))
    return (x, y), m

    # This is background in not only  Our rectangle " should change name


def EnergyRadius(grid, dic={}):
    """We first define r99u and v following the spread direction
    x and y respectively, but these are arbitrary due to the fit
    we then transfroms it to r99x and R99y
    Returns: (r99uv), (r99xy)
    """
    params = dic  # because no update
    fit_type = get_state().fit_type
    aniso = get_state().b_aniso

    ############
    # GAUSSIAN
    if fit_type == 'Gaussian':
        # 2.14 for 99% energy, we ll use 3.14
        r99u = 3.14 * params['spread_x']
        if aniso:
            r99v = 3.14 * params['spread_y']
        else:
            r99v = 3.14 * params['spread_x']

    # if ('Gaussian_hole' in fit_type):  # 2.14 for 99% energy, we ll use 3.14
    #     if 'pread_y' in params.has_key:
    #         r99u = 3.14 * params['spread_x']
    #         r99v = 3.14 * params['spread_y']
    #     else:
    #         r99u = 3.14 * params['spread_x']
    #         r99v = 3.14 * params['spread_x']

    ###############
    # MOFFAT
    if 'Moffat' in fit_type:
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
    if fit_type == 'Bessel1':
        # take cara r99 = R90
        r99u = 5.8 * params['spread_x']
        r99v = 5.8 * params['spread_x']
    if (fit_type == 'Bessel12D'):
        # take cara r99 = R90
        r99u = 5.8 * params['spread_x']
        r99v = 5.8 * params['spread_y']
    if (fit_type == 'None'):
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


def FwhmFromFit(param):
    """and phot  all explicit  return fwhm_x, fwhm_y (0 or 1)
    from spread and exponent and fit_type, that is explicit"""
    fit_type = get_state().fit_type
    aniso = get_state().b_aniso

    # "
    # GAUSSIAN
    if 'Gaussian' in fit_type:
        if not aniso:
            try:
                param["spread_y_hole"] = param["spread_x_hole"]
            except:
                pass
        photometry = np.pi*param['intensity'] * \
            param['spread_x']*param['spread_y']
        # if "hole" in fit_type:
        #     photometry -= np.pi*param['intensity_hole'] * \
        #         param['spread_x_hole']*param['spread_y_hole']
        fwhm_x = 1.66510922*param['spread_x']  # 2 * sqrt( log(2) )
        fwhm_y = 1.66510922*param['spread_y']

    ###########
    # MOFFAT
    elif "Moffat" in fit_type:
        if not aniso:
            param["spread_y"] = param["spread_x"]
            param["theta"] = 99
        if param['exponent'] > 1:
            photometry = np.pi * \
                param['intensity']*param['spread_x'] * \
                param["spread_y"] / (param['exponent']-1)
        else:  # fit diverges
            x = np.arange(int(param["center_x"]-50),
                          int(param["center_x"]+50+1))
            y = np.arange(int(param["center_y"]-50),
                          int(param["center_y"]+50+1))
            Y, X = np.meshgrid(x, y)
            cut = Moffat2D((X, Y), param)
            photometry = np.sum(cut)

        fwhm_x = 2 * abs(param['spread_x']) * \
            np.sqrt((0.5)**(-1/param['exponent'])-1)
        fwhm_y = 2 * abs(param['spread_y']) * \
            np.sqrt((0.5)**(-1/param['exponent'])-1)

    ##########
    # BESSEL
    elif 'Bessel1' in fit_type:
        if not aniso:
            param["spread_y"] = param["spread_x"]

        photometry = 4 * np.pi * param['intensity'] * \
            param['spread_x']*param["spread_y"]
        fwhm_x = 2 * param['spread_x'] * 1.61
        fwhm_y = 2 * param['spread_y'] * 1.61

    elif fit_type == 'None':
        photometry = 99
        fwhm_x, fwhm_y = 99, 99

    log(3, 'Fit: photometry, estimated from', fit_type, 'is', photometry)
    return {"fwhm_x": fwhm_x, "fwhm_y": fwhm_y, "photometry_fit": photometry}


def EightRectangleNoise(grid, r, return_rectangle=0, dictionary={'size': 4, 'distance': 1}):
    # We Derive the noise from eight rectangle (of R/2 ) around the 99% Energy
    # size =4 means that we devide by  4 the size of the rectangle
    # distance = 2 means we go father by a factor 2 for star center (r center)
    # we suppose order in r
    rx1, rx2, ry1, ry2 = r
    distance, size = dictionary['distance'], dictionary['size']
    rx1, rx2 = rx1 - distance*(rx2-rx1)/2,  rx2 + distance*(rx2-rx1)/2
    ry1, ry2 = ry1 - distance*(ry2-ry1)/2,  ry2 + distance*(ry2-ry1)/2
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
        # tmp=Stat.RectanglePhot(grid,(ax1,ax2,ay1,ay2),dic={"get":["number_count","sum","rms"]})  # bad pixels
        # background.append((tmp["sum"]/tmp["number_count"]))   #rectangle phot return the sum and the number_count # bite bad pixel

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


# We compare with the median filter.
def FindBadPixel(grid, r=None, method=('median', 3, 2), ordered=False):
    # In the method we define in arg1 the number of pixel to include in the median
    # and in arg2, the max differnce between true image and median
    # the bad pixels can be noise or warm pixel
    if r is None:
        IX = grid
    else:
        if ordered == False:
            rx1, rx2, ry1, ry2 = Order4(r)
        else:
            (rx1, rx2, ry1, ry2) = r
        IX = grid[rx1:rx2+1, ry1:ry2+1]
    res, mIX = IX, IX

    # Filter infs and nan
    nan = np.isnan(res)
    inf = np.isinf(res)
    res[nan] = 0
    mIX[nan] = 1
    res[inf] = 0
    mIX[inf] = 1

    if method[0] == 'median':
        mIX = scipy.ndimage.median_filter(IX, size=(method[1], method[1]))
        res[np.abs(IX-mIX) > (method[2]-1) * mIX] = mIX[np.abs(IX-mIX) > (method[2]-1)*mIX]
        # that you Antoine for showing how to get the median value when we differ to much from it.

    return res, mIX


def InBorder(grid, r):  # to check if r is in the grid
    rx1, rx2, ry1, ry2 = Order4(r)
    if rx1 < 0:
        rx1 = 0
    if rx1 > len(grid)-1:
        rx1 = len(grid)-1
    if ry1 < 0:
        ry1 = 0
    if ry1 > len(grid[rx1])-1:
        rx1 = len(grid[rx1]-1)
    return (rx1, rx2, ry1, ry2)

    #################
    # PROFILE OF A LINE (Cuting )
    #########################


def RadialLine(grid, point1_and_point2, return_point=0):
    """Returns profile one a line: 2 vectors x and y"""
    (x1, y1), (x2, y2) = point1_and_point2
    vect_r = ((x2-x1), (y2-y1))
    lenght = np.sqrt(vect_r[1]**2+vect_r[0]**2)  # of the line
    # the extreme points of the line
    xmin, xmax, ymin, ymax = Order4((x1, x2, y1, y2), grid=grid)
    xmin, xmax, ymin, ymax = int(xmin), int(xmax), int(ymin), int(ymax)

    # should put int otherwise mismatch with array
    x, y = np.arange(xmin-1, xmax+1), np.arange(ymin-1, ymax+1)
    Y, X = np.meshgrid(y, x)
    array = grid[xmin-1:xmax+1, ymin-1:ymax+1]

    R = ((X-x1)*(x2-x1)+(Y-y1)*(y2-y1))/lenght
    # the distance of (X,Y) to x1,y1 projected on the line
    d = (R*(x2-x1)/lenght-(X-x1))**2 + (R*(y2-y1)/lenght-(Y-y1))**2

    # the square distance of the point from the line
    R, d, array = R.flatten(), d.flatten(), array.flatten()
    X, Y = X.flatten(), Y.flatten()
    ab, od = np.zeros(len(array)), np.zeros(len(array))

    ab[d < 0.25] = R[d < 0.25]   # ab like abscisse
    od[d < 0.25] = array[d < 0.25]
    X, Y = X[d < 0.25], Y[d < 0.25]
    # good idea also :  od = [od for (Y,od) in sorted(zip(Y,od))]
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
    else:
        return res[:, 0], res[:, 1]  # abscice ordonate


# we supose that r is ordere for the display og the strahl funciton
def XProfile(grid, center, r=None, direction='X'):
    if r is None:
        r = (0, len(grid)-1,   0, len(grid[0]) - 1)
    Order4(r)
    if direction == 'X':
        x = np.arange(int(r[0]), int(r[1])+1)
        y = grid[int(r[0]):int(r[1])+1, int(center[1])]
    return x, y


def RadialCloud(grid, center, radius, direction='None'):
    x0, y0 = center
    rx1, rx2, ry1, ry2 = int(
        x0-radius), int(x0+radius+1), int(y0-radius), int(y0+radius+1)
    x, y = [], []
    for i in range(rx1, rx2):
        for j in range(ry1, ry2):
            x.append, y.append = np.sqrt((x0-i)**2+(y0-i)**2), grid[i][j]
    return x, y


# take care it will take the image and its end
# N number of stars. BINFACT, the size (diameter) of the "psf"
def FindNStars(grid, N, binfact=3, separation=30):
                                                # SEPARATION, the minimum separation betwenn two stars.
    # we just bin the image and give the N maximums, there can be an error (order of binfact pixels
    #        => yo1Gu need to use PixelMax and SeeingFit then.
    fattable = Bin(grid, binfact)
    res = np.zeros((N, 3))
    for i in range(len(fattable)):
        for j in range(len(fattable[i])):
            tmp = 0
            IsFar = True
            for k in range(N):
                IsFar &= ((i-res[k][0])**2 + (j-res[k][1])**2 <
                          separation)  # here you see the separation
            while((fattable[i][j] > res[N-tmp-1][2]) & (tmp < N)):
                tmp += 1
            try:
                res[N-tmp-1][0] = res[N-tmp][0]
                res[N-tmp-1][1] = res[N-tmp][1]
                res[N-tmp-1][2] = res[N-tmp][2]
            except:
                ()
            try:
                res[N-tmp][0] = i*binfact
                res[N-tmp][1] = j*binfact
                res[N-tmp][2] = fattable[i][j]
            except:
                ()
    return res


##################
# DIRECT INTERACT WITH EVENT
##################


# photomtery, return bol or dic
def EllipticalAperture(grid, dic={}, interp=False, full_answer=True, xy_answer=True):
    """ rdic = ru rv theta x0 y0
    Returns a dic,
        dic[bol] = are you in aperture
        dic[coord_x] = X[bol]
        dic[coord_y] = are you in aperture
          SO you can fit grid[bol]  = Basicfct((x,y),params see in StrehlFunciton folder how I use it (written october 30 2013)

    or if we interpolate, return directly some values (phot, rms, number_count, fractional
    interp is dividing each pixel by 10*10 pixelsn seems enought to me
       dic : center_x, center_y , ru,rv, theta
            ru , rv in pixels
           centers in pixels from the begining of the array x = row, y = column
    if full answer return dic : number_count, sum, bol,bol2, interp_grid,
    # REturn X and y index of bol
    """
    # Check in
    if dic == {}:
        return 0*grid
    res = {}

    # Unpack in
    x0, y0 = dic["center_x"], dic["center_y"]
    ru, rv, theta = dic["ru"], dic["rv"], dic["theta"],
    cos = np.cos(theta)
    sin = np.sin(theta)

    a = ((cos/ru)**2 + (sin/rv)**2)
    b = ((sin/ru)**2 + (cos/rv)**2)
    c = (np.sin(2 * theta) * (1./rv**2 - 1. / ru**2))

    x = np.arange(-x0, len(grid)-x0)  # invert IDK why
    y = np.arange(-y0, len(grid[0])-y0)

    if not interp:
        # need to be in this order , tested with event ellipser!
        Y, X = np.meshgrid(y, x)

        bol = a*X**2 + b*Y**2 + c*X*Y < 1
        if full_answer:
            # just need: "sum", "number_count", "rms"
            grid_cut = grid[bol]
            res.update(get_array_stat(grid_cut))
            res["bol"] = bol
            return res
        else:  # no full_answer
            res["bol"] = bol
        if xy_answer:
            res["coord_x"] = X[bol]
            res["coord_y"] = Y[bol]

    else:  # including interpolate
        binn = 0.1
        xx = np.arange(-x0, len(grid)-x0, binn)
        yy = np.arange(-y0, len(grid[0])-y0, binn)
        XX, YY = np.meshgrid(xx, yy)  # need to be in this order , tested

        interp_fct = scipy.interpolate.interp2d(x, y, grid, kind="cubic")
        interp_grid = interp_fct(xx, yy)
        bol2 = a*XX**2 + b*YY**2 + c*XX*YY < 1

        # stats = Stat.Stat(interp_grid[bol], get=["sum", "number_count"])
        stats = get_array_stat(interp_grid[bol])
        res = {"interp_grid": interp_grid, "bol2": bol2, "bol": bol}
        res["sum"] = stats["sum"]*binn**2
        res["number_count"] = stats["number_count"] * binn**2

        if xy_answer:
            res["coord_x"] = X[bol]
            res["coord_y"] = Y[bol]

    return res

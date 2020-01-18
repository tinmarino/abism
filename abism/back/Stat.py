import numpy as np
import scipy  # for median filter


def Stat(grid, dic={}, get=None):  # hist for the histogram
    """
        @brief Make scalar stat on an image
values string in get.
        @param grid, a matrix of the full image, with true ADU
        @param dic, seems useless
        @param get List of the parameters I can get
can be mean, median, rms, min, max, number_count, sum
        @return a dictionnary, witch keys  are the values in get
    """
    res = {}

    # CHECK INPUT grid
    if len(grid) == 0:
        return res    # what can I do with a zero len grid ?

    # CHECK INPUT get
    if get is not None:
        pass   # keep the get from input
    else:
        get = ["mean", "median", "rms", "min", "max", "number_count", "sum"]

    for i in get:
        # RMS
        if i == "rms":
            res[i] = np.std(grid)

        # NUMBER_COUNT = number of pixels
        elif i == "number_count":
            res["number_count"] = len(grid.flatten())

        # SUM of all pixels
        elif i == "sum":  # to go faster
            if "mean" in res and "number_count" in res:
                res["sum"] = res["mean"] * res["number_count"]
            else:
                res["sum"] = np.sum(grid)

        # Np function
        else:  # do np.i[grid]
            method = getattr(np, i)
            res[i] = method(grid)

        """number_count done by rectangle phot"""

    return res


def Sky(grid, dic={}):  # recursive sigmaclipping to estimate the sky bg
    """
        @param grid: the image np.array
        @param dic contains mean,rms, sigma(clipping),
median, it is the input and output
        @return  dic: same as stat, median, or mean id the sky
    """

    # if first loop, no rejection yet
    if "mean" not in dic:

        # MAKE A DEFAULT input of dic the error is a fraction of the rms
        dic_default = {"rec": 0, "max_rec": 10,
                       "error": 0.1, "sigma": 2.5}
        dic_default.update(dic)
        dic = dic_default

        dic.update(Stat(grid))
        dic["rec"] += 1

        return Sky(grid, dic)  # now mean is in dic

    # Second call,
    else:  # including we have a mean, we can do sigma (clipping)
        if dic["rec"] > dic["max_rec"]:  # maximum recursion
            return dic
        else:
            # SIGMA clip
            rms_old = dic["rms"]
            bol1 = abs(grid - dic["mean"]) < abs(dic["sigma"] * dic["rms"])
            grid1 = grid[bol1]
            dic.update(Stat(grid1))

            # Check if finished
            bolt = (dic["rms"] > (1.-dic["error"]) * rms_old)  # t like tmp
            bolt = bolt & (dic["rms"] < (1.+dic["error"])
                           * rms_old)  # but it is error test

            if bolt:    # Finished
                return dic
            else:       # Recurse
                dic["rec"] += 1
                return Sky(grid, dic)


def BadPixelCleaner(lst, dic={}):  # notfinished not working
    """
      lst can be LIST  or ARRAY , return object of the same type
    """
    # DIC default
    default_dic = {'median_filter': (3, 5), "exact": 0}
    default_dic.update(dic)
    dic = default_dic

    # MEDIAN
    med_size = dic["median_filter"]
    if med_size[0] != 0:
        median = scipy.ndimage.median_filter(
            cutted, size=(med_size[0], med_size[0])
        )
        cutted[np.abs(cutted-median) > (med_size[1]-1) *
               median] = median[np.abs(cutted-median) > (med_size[1]-1)*median]
    return


def RectanglePhot(grid, r, dic={}, get=[]):
    """
        @param r: (rx1,rx2,ry1,ry2), it should be ordered
and defining a rectangle
       # exact is for the taking the percentage of the cutted pixel or not
       # median is a median filter of 3 pixel square and 2 sigma clipping
       # in_border is examining if r is in the grid, otherwise, cannot calculate.
    """

    # INPUT DIC default
    default_dic = {'median_filter': (3, 4), "exact": 0, "get": ["sum"]}
    default_dic.update(dic)
    dic = default_dic

    # INPUT get default
    if get == []:
        get = dic["get"]

    # INPUT r  DEFAULT
    if r is None:
        rx1, rx2, ry1, ry2 = 0, len(grid)-1, 0, len(grid[0])-1

    else:
        rx1, rx2, ry1, ry2 = r[0], r[1], r[2], r[3]

    # Take in pixels, no division of a pixel
    if not dic["exact"]:
        cutted = grid[int(rx1):int(rx2+1), int(ry1):int(ry2+1)]

        # MEDIAN FILETRING
        med_size = dic["median_filter"]
        if med_size[0] != 0:
            median = scipy.ndimage.median_filter(
                cutted, size=(med_size[0], med_size[0]))
            cutted[np.abs(cutted-median) > (med_size[1]-1) *
                   median] = median[np.abs(cutted-median) > (med_size[1]-1)*median]

    res = Stat(cutted, get=get)
    res["number_count"] = (ry2 - ry1) * (rx2 - rx1)
    return res


def ObjectDetection(grid, dic={}):
    """
        -sigma is the clip
        -background_box is the side of the background box

        we first detect all objects higher than (local ?) sigma
    """
    default_dic = {"sigma": 2.5, "background_box": 10, "back_type": "global"}
    default_dic.update(dic)
    dic = default_dic
    res = grid

    # MEDIAN FILTER
    median = scipy.ndimage.median_filter(res, size=(3, 3))
    bol1 = (np.abs(res-median) > 2 * median)
    res[bol1] = median[bol1]

    # SKY call
    sky = Sky(res, dic={"sigma": dic["sigma"]})
    bpm = 0 * grid + 1  # bpm = 0 where mask

    # SIGMA CLIP
    bol1 = np.abs(res-sky["median"]) > (dic["sigma"] * sky["rms"])
    bpm[bol1] = 0

    # BOX FROM FELIPE BARRIENTOS
    median = scipy.ndimage.median_filter(bpm, size=(10, 10))
    bpm2 = 0 * bpm + 1
    bpm2[median > 0.08] = 0

    # BOX
    kernel = np.zeros((10, 10)) + 1
    conv = scipy.ndimage.convolve2d(bpm, kernel)

    return bpm2, median, bpm, sky, conv

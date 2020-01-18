"""
    Array scale helpers
"""
import numpy as np

from abism.back import Stat
import abism.back.util_back as W  # to know the stats


def MinMaxCut(grid, dic={}):  # From a true value renge give min_cut and max_cut
    """Define the min and max cut for the viewable image.
    @param  grid: the image (to be viewed) as a np.array
    @param  dic:  the scale_dic,  defining the clipping style and size,
                  for example style: sygma size: 3 means 3 sigma clipping
    @return the min and max cut in ADU
    """

    # CONFIGURE DEFAULT DIC And get input
    default_dic = {"scale_cut_type": "sigma_clip",
                   "sigma_min": 1, "sigma_max": 5}
    default_dic.update(dic)
    dic = default_dic

    # No Clipping
    if dic["scale_cut_type"] == "None":
        min_cut, max_cut = np.min(grid), np.max(grid)

    # PERCENT in (like keep 80% of pixel in the remaining segment
    elif dic["scale_cut_type"] == "percent":
        percent = dic["percent"]
        if "whole_image" in dic:
            sort = W.sort
        else:
            sort = grid.flatten()      # Sorted Flatten Image
            sort.sort()
        percent = (100. - percent) / 100.   # get a little percentage
        min_cut = sort[int(percent / 2 * len(sort))]
        max_cut = sort[int((1-percent/2)*len(sort))]

    # SIGMA clipping
    elif dic["scale_cut_type"] == "sigma_clip":
        if "sigma_min" not in dic:
            dic["sigma_min"] = dic["sigma"]
            dic["sigma_max"] = dic["sigma"]
        if "median" not in dic:   # The stats isn't done yet
            if "whole_image" in dic:
                dic.update(vars(W.imstat))
            else:
                dic.update(Stat.Stat(grid, dic=dic))

        mean, rms = dic["mean"], dic["rms"]
        s_min, s_max = dic["sigma_min"], dic["sigma_max"]

        min_cut, max_cut = mean - s_min*rms, mean + s_max*rms

    res = {"min_cut": min_cut, "max_cut": max_cut}
    return res


def Rescale(grid, dic={}):  # transform 0-1 to 0-1 with a certain function,
    """ TODO give me a lambda
        above linear or under linear. like log or x**2
    """
    default_dic = {"fct": "x"}
    default_dic.update(dic)
    dic = default_dic

    if "min_cut" not in dic:
        dic["min_cut"], dic["max_cut"] = np.min(grid), np.max(grid)

    # Rescale, put everything between 0 and 1
    minc, maxc = dic["min_cut"], dic["max_cut"]
    grid = (grid - minc) / (maxc - minc)

    # Transoform
    def fct(x):
        return x  # to avoid warnings from pep8
    exec("fct = lambda x: " + dic["fct"])  # read the true scale fct
    grid = fct(grid)

    # Scale back, to its "true" value, for min to stay min and max to remains
    # max
    grid = grid * (maxc - minc) + minc

    return grid

"""
    The class you alwas dreamt of

TODO sort function
"""

import numpy as np
from astropy.io import fits
from scipy.ndimage import median_filter
from scipy.signal import convolve2d


from abism.plugin.ReadHeader import parse_header  # What a name !

# TODO root for MinMaxCut, should be here
from abism.util import log, get_root, get_state


class ImageStat():
    """Container mean, median, rms, min, max, number_count, sum"""
    # pylint: disable=attribute-defined-outside-init
    def __init__(self, image):
        self.image = image

    def init_all(self):
        """
        Returns self
        TODO better perf lazy loading ?
        TODO  give sorted sort
        """

        self.mean = np.mean(self.image.im0)

        self.median = np.median(self.image.im0)

        self.rms = np.std(self.image.im0)

        self.min = np.min(self.image.im0)

        self.max = np.max(self.image.im0)

        self.number_count = len(self.image.im0.flatten())

        self.sum = self.mean * self.number_count  # or np.sum(self.image.im0)

        return self


class ImageInfo():
    """Image and its info
    Instance it at root.image. Is is unique as user can open only 1 image.
        - Maybe I should put it in AbismState but ...
        - that does not change anything anyway
    """
    def __init__(self):
        """
        image_name
        image_click = (0., 0.)
        image_release = (0., 0.)
        """
        # Current image filepath
        self.name = ''  # Filename
        self.is_cube = False  # Cube it is not
        self.cube_num = -1
        self.click = (0., 0.)  # Mouse click position
        self.release = (0., 0.)  # You guess ?

        self.bpm = None  # Bad Pixel mask array
        self.bpm_name = None  # Bad Pixel Mask filepath

        # Now we speak
        self.hdulist = None  # From fits.open
        self.header = None  # shortcut
        self.im0 = None  # np.array the image !!
        self.sort = None  # Sorted image for cut and histograms
        self.stat = ImageStat(self)


    @staticmethod
    def from_array(grid):
        """Builder"""
        image = ImageInfo()

        # Remove nan -> they cause errors
        # TODO pretty mask
        grid[np.isnan(grid)] = 0

        # Save im0
        image.im0 = grid


        return image


    @staticmethod
    def from_file(filename):
        """Builder"""
        """Open image from path
        new_fits if a new file, and not cube scrolling
        I know this is not front but so central ...
        """
        # Create
        image = ImageInfo()

        # Check in
        if not filename:
            return image

        # Check open
        try:
            hdulist = fits.open(filename)
        except FileNotFoundError:
            return image

        # Get <- Io
        image.name = filename
        image.hdulist = hdulist

        image.im0 = image.hdulist[0].data

        # Parse header
        image.header = parse_header(image.hdulist[0].header)

        image.set_science_variable()

        return image


    def get_stat_as_dic(self):
        """Helper: readability counts
        Used for Sky, Background, Photometry, Object detection
        """
        return vars(self.stat.init_all())

    def set_science_variable(self):
        """ Get variable, stat from image
        TODO refactor full with ImageInfo lib
        """
        # BPM
        if self.bpm_name is not None:
            hdu = fits.open(self.bpm_name)
            self.bpm = hdu[0].data
        else:
            self.bpm = 0 * self.im0 + 1

        # Statistics
        self.sort = self.im0.flatten()
        self.sort.sort()
        self.stat.init_all()


    def substract_sky(self, fp_sky):
        """Returns True if no problem"""
        # Open
        bg_hdulist = fits.open(fp_sky)

        # Check shape
        bg0 = bg_hdulist[0].data
        if not bg0.shape == self.im0.shape:
            log(0, 'ERROR : Science image and Background image should have the same shape')
            return False

        # Substract arrays
        self.im0 -= bg0
        return True


    def ObjectDetection(self, dic={}):
        """
            -sigma is the clip
            -background_box is the side of the background box

            we first detect all objects higher than (local ?) sigma
        """
        grid = self.im0
        default_dic = {"sigma": 2.5, "background_box": 10, "back_type": "global"}
        default_dic.update(dic)
        dic = default_dic
        res = grid

        # MEDIAN FILTER
        median = median_filter(res, size=(3, 3))
        bol1 = (np.abs(res-median) > 2 * median)
        res[bol1] = median[bol1]

        # SKY call
        sky = self.sky(res, dic={"sigma": dic["sigma"]})
        bpm = 0 * grid + 1  # bpm = 0 where mask

        # SIGMA CLIP
        bol1 = np.abs(res-sky["median"]) > (dic["sigma"] * sky["rms"])
        bpm[bol1] = 0

        # BOX FROM FELIPE BARRIENTOS
        median = median_filter(bpm, size=(10, 10))
        bpm2 = 0 * bpm + 1
        bpm2[median > 0.08] = 0

        # BOX
        kernel = np.zeros((10, 10)) + 1
        conv = convolve2d(bpm, kernel)

        return bpm2, median, bpm, sky, conv


    def MinMaxCut(self):  # From a true value renge give min_cut and max_cut
        """Returns: (min, max) cut in ADU for the viewable image"""
        # Get in <- GUI state
        cut_type = get_state().s_image_cut
        cut_value = get_state().i_image_cut
        log(5, 'Get MinMaxCut for', cut_type, ':', cut_value)

        # No Clipping
        if cut_type == 'None':
            min_cut, max_cut = self.stat.min, self.stat.max

        # Percent
        elif cut_type == 'percent':
            percent = (100. - cut_value) / 100.   # get a little percentage
            min_cut = self.sort[int(percent / 2 * self.stat.number_count)]
            max_cut = self.sort[int((1 - percent) / 2 * self.stat.number_count)]

        # Sigma clipping
        elif cut_type == 'sigma_clip':
            sigma_min = cut_value - 2
            sigma_max = cut_value + 2

            min_cut = self.stat.median - sigma_min * self.stat.rms
            max_cut = self.stat.median + sigma_max * self.stat.rms

        return min_cut, max_cut


    def Rescale(grid, dic={}):  # transform 0-1 to 0-1 with a certain function,
        """ TODO give me a lambda
            above linear or under linear. like log or x**2
        """
        grid = self.im0
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


    def CubeRefactorMe(self):
        if len(self.hdulist[0].data.shape) == 3:
            if new_fits:
                # we start with the last index
                self.cube_num = self.hdulist[0].data.shape[0] - 1
            if abs(self.cube_num) < len(self.hdulist[0].data[:, 0, 0]):
                if self.is_cube == 0:  # to load cube frame
                    self.is_cube = 1
                    selfFrame.Cube()
                self.from_array(self.hdulist[0].data[self.cube_num])

            else:
                self.cube_num = self.hdulist[0].data.shape[0] - 1
                log(1, '\nERROR InitImage@WindowRoot.py :' + self.name
                    + ' has no index ' + str(self.cube_num)
                    + 'Go back to the last cube index :'
                    + str(self.cube_num) + "\n")
            G.cube_var.set(int(self.cube_num + 1))

        else:  # including image not a cube, we try to destroy cube frame
            self.is_cube = False
            get_root().ImageFrame.Cube()


    def sky(self, dic=None):
        """Recursive sigmaclipping to estimate the sky bg
            @param grid: the image np.array
            @param dic contains mean,rms, sigma(clipping),
            median, it is the input and output
            @return  dic: same as stat, median, or mean id the sky
        """
        # First call: no rejection yet
        if dic is None or 'rec' not in dic:

            # MAKE A DEFAULT input of dic the error is a fraction of the rms
            dic = {'rec': 0, 'max_rec': 10, 'error': 0.1, 'sigma': 2.5}
            dic.update(vars(self.stat))

            return self.sky(dic)

        # Check recursion
        if dic.get('rec', 0) > dic.get('max_rec', 100):
            return dic

        # Second call,
        # Sigma clip
        rms_old = dic["rms"]
        bol1 = abs(self.im0 - dic["mean"]) < abs(dic["sigma"] * dic["rms"])
        stat = get_array_stat(self.im0[bol1])
        dic.update(stat)
        log(5, 'Sky cut: ', dic)


        # Check if finished
        bolt = dic["rms"] > (1. - dic["error"]) * rms_old
        bolt = bolt & (dic["rms"] < (1. + dic["error"]) * rms_old)

        # Recurse
        if not bolt:
            dic['rec'] += 1
            return self.sky(dic)

        # Finished
        return dic


    def RectanglePhot(self, r, dic={}, get=[]):
        """
            @param r: (rx1,rx2,ry1,ry2), it should be ordered
            kand defining a rectangle
        # exact is for the taking the percentage of the cutted pixel or not
        # median is a median filter of 3 pixel square and 2 sigma clipping
        # in_border is examining if r is in the grid, otherwise, cannot calculate.

        Take in pixels, no division of a pixel
        """
        log(5, 'Rectangle phot on:', r)

        # INPUT DIC default
        default_dic = {'median_filter': (3, 4), "exact": 0, "get": ["sum"]}
        default_dic.update(dic)
        dic = default_dic

        # INPUT get default
        if get == []:
            get = dic["get"]

        # INPUT r  DEFAULT
        if r is None:
            rx1, rx2, ry1, ry2 = 0, len(self.im0)-1, 0, len(self.im0[0])-1
        else:
            rx1, rx2, ry1, ry2 = list(map(int, r))

        if not dic["exact"]:
            cutted = self.im0[int(rx1):int(rx2+1), int(ry1):int(ry2+1)]

            # MEDIAN FILETRING
            med_size = dic["median_filter"]
            if med_size[0] != 0:
                median = median_filter(
                    cutted, size=(med_size[0], med_size[0]))
                cutted[np.abs(cutted-median) > (med_size[1]-1) * median] = \
                    median[np.abs(cutted-median) > (med_size[1]-1)*median]

        # Just need get
        res = get_array_stat(cutted)
        res["number_count"] = (ry2 - ry1) * (rx2 - rx1)
        return res


def get_array_stat(grid):
    """Helper for readability
    Get statistic dicitonary from a grid
    """
    return ImageInfo.from_array(grid).get_stat_as_dic()

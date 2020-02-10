"""
    The class you always dreamt of ... is in your dreams
"""
import re
import numpy as np
from astropy.io import fits
from scipy.ndimage import median_filter

from abism.back.read_header import parse_header

from abism.util import log, get_state, DotDic


class ImageStat(DotDic):
    """Container mean, median, rms, min, max, number_count, sum"""
    def __init__(self, image):
        # pylint: disable = super-init-not-called
        # Sort
        if image.sort is None:
            image.make_sort()
        sort = image.sort

        self.mean = np.mean(image.im0)

        self.rms = np.std(image.im0)

        self.number_count = len(image.im0.flatten())

        # Check len
        if len(sort) == 0:
            self.median = self.min = self.max = self.sum = float('nan')
            return

        # Median
        middle = (self.number_count-1) // 2
        if self.number_count % 2:
            self.median = sort[middle]
        else:
            self.median = (sort[middle] + sort[middle + 1]) / 2

        self.min = sort[0]

        self.max = sort[-1]

        self.sum = self.mean * self.number_count


class ImageInfo():
    """Image and its info
    Instance it at root.image. Is is unique as user can open only 1 image.
        - Maybe I should put it in AbismState but ...
        - that does not change anything anyway
    """
    def __init__(self, array):
        """np.array of the image
        Warning, it NaN values are zeroed
        """
        self.set_array(array)

        # Metadata
        self.hdulist = None  # From fits.open
        self.header = None  # shortcut

        # Current image filepath
        self.name = ''  # Filename
        self.is_cube = False  # Cube it is not
        self.cube_num = -1  # 0 based
        self.i_cube_len = -1  # 1 based

        self.bpm = None  # Bad Pixel mask array
        self.bpm_name = None  # Bad Pixel Mask filepath

        # TODO remove (has been classified)
        self.click = (0., 0.)  # Mouse click position
        self.release = (0., 0.)  # You guess ?

    def set_array(self, array):
        """Array info called from init and cube chage"""
        self.im0 = array  # np.array the image !!

        # Sorted image for cut and histograms
        self.sort = self.im0.flatten()
        self.sort.sort()

        # Get statistics
        self.stat = ImageStat(self)

        # Remove nan -> they cause errors
        # TODO pretty mask ... takes time
        self.im0[np.isnan(self.im0)] = 0


    @staticmethod
    def from_file(filename):
        """Builder"""
        """Open image from path
        new_fits if a new file, and not cube scrolling
        I know this is not front but so central ...
        """
        # Check in
        if not filename:
            return None

        # Check open
        try:
            hdulist = fits.open(filename)
        except FileNotFoundError:
            return None

        if len(hdulist[0].data.shape) >= 3:
            image = ImageInfo.from_cube(hdulist)
        else:  # including image not a cube, we try to destroy cube frame
            image = ImageInfo.from_2D(hdulist)

        # Get <- Io
        image.name = filename
        image.hdulist = hdulist

        # Parse header
        image.header = parse_header(image.hdulist[0].header)

        # BPM TODO nothing to be here
        if image.bpm_name is not None:
            hdu = fits.open(image.bpm_name)
            image.bpm = hdu[0].data

        return image


    @staticmethod
    def from_2D(hdulist):
        image = ImageInfo(hdulist[0].data)
        image.is_cube = False
        return image


    @staticmethod
    def from_cube(hdulist):
        """ TODO call image_frame.Cube(), to create or destroy
        Here i got deleted 1bb47dccf2
        """
        # Dirty cut first dim for nasa sample
        if len(hdulist[0].data.shape) > 3:
            hdulist[0].data = hdulist[0].data[0]

        # we start with the last index
        cube_num = hdulist[0].data.shape[0]
        image = ImageInfo(hdulist[0].data[cube_num - 1])
        image.is_cube = True
        image.cube_num = cube_num
        image.i_cube_len = cube_num
        return image


    def update_cube(self):
        im0 = self.hdulist[0].data[self.cube_num - 1]
        self.set_array(im0)


    def get_stat(self):
        """Helper: readability counts
        Used for Sky, Background, Photometry, Object detection
        """
        return self.stat


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


    def create_bad_pixel_mask(self):
        """Create bad pixel mask from image grid"""
        self.bpm = False * self.im0
        ground = median_filter(self.im0, size=(4, 4)) + self.stat.rms
        bol1 = np.abs(self.im0) > np.abs(3 * ground)
        self.bpm[bol1] = True


    def get_cut_minmax(self):
        """Returns: (min, max) cut in ADU for the viewable image"""
        # Get in <- GUI state
        cut_type = get_state().s_image_cut
        if cut_type not in ('None', 'Manual'):
            re_float = re.compile(r"""(?x)
                [+-]?\ *         # first, match an optional sign *and space*
                (                # then match integers or f.p. mantissas:
                    \d+          # start out with a ...
                    (
                        \.\d*    # mantissa of the form a.b or a.
                    )?           # ? takes care of integers of the form a
                    |\.\d+       # mantissa of the form .b
                )
                ([eE][+-]?\d+)?  # finally, optionally match an exponent
            """)
            cut_value = float(re.search(re_float, get_state().s_image_cut).group(0))
            log(5, 'Get MinMaxCut for', cut_type, ':', cut_value)

        # No Clipping
        if cut_type == 'None':
            min_cut, max_cut = self.stat.min, self.stat.max

        # Overkill but
        elif cut_type == 'Manual':
            min_cut = get_state().i_image_min_cut
            max_cut = get_state().i_image_max_cut

        # Percent
        elif '%' in cut_type:
            log(9, 'cutting percentage')
            # Get a little percentage (like 0.1 for 99.9)
            percent = (100. - cut_value) / 100.
            min_cut = self.sort[int(percent * self.stat.number_count)]
            max_cut = self.sort[int((1 - percent) * self.stat.number_count)]

        # Sigma clipping
        elif 's' in cut_type or 'S' in cut_type or 'σ' in cut_type:
            sigma_min = cut_value - 2
            sigma_max = cut_value + 2

            min_cut = self.stat.median - sigma_min * self.stat.rms
            max_cut = self.stat.median + sigma_max * self.stat.rms

        return min_cut, max_cut


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
            dic.update(self.stat)

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


    def RectanglePhot(self, r):
        """
        :param r: (rx1,rx2,ry1,ry2), it should be ordered
            kand defining a rectangle
        # exact is for the taking the percentage of the cutted pixel or not
        # median is a median filter of 3 pixel square and 2 sigma clipping
        # in_border is examining if r is in the grid, otherwise, cannot calculate.

        None: Considering pixels, no division of a pixel
        """
        log(5, 'Rectangle phot on:', r)

        rx1, rx2, ry1, ry2 = list(map(int, r))

        # Cut image
        cutted = self.im0[int(rx1):int(rx2+1), int(ry1):int(ry2+1)]

        # Smooth bad pixel <- Filter median
        median = median_filter(cutted, size=(3, 3))
        bol = np.abs(cutted - median) > 3 * median
        cutted[bol] = median[bol]

        # Get stats
        stat = get_array_stat(cutted)
        stat.number_count = (ry2 - ry1) * (rx2 - rx1)
        return stat


def get_array_stat(grid):
    """Helper for readability
    Get statistic dicitonary from a grid
    """
    return ImageInfo(grid).get_stat()

"""
    Fit classes oriented for Strehl retrieval (i.e photometry and intensity)
Build fitted parameters from user variables
"""
from abc import ABC, abstractmethod

import time
import numpy as np

from abism.back import ImageFunction as IF
from abism.back.fit_helper import leastsqFit
import abism.back.fit_template_function as BF


from abism.util import log, get_state, set_aa, \
    EA, ESky


class Fit(ABC):
    """Base class to perform a Fit"""
    def __init__(self, grid):
        self.grid = grid

        # Retrieve fit function
        self.s_fit_type = get_state().s_fit_type
        self.fit_fct = BF.get_fit_function()
        self.b_aniso = get_state().b_aniso
        self.b_saturated = get_state().b_saturated

        # Retrieve verbose
        self.verbose = get_state().verbose > 0

        self.result = []

    def do_fit(self):
        start_time = time.time()

        (x, y), IX, eIX = self.get_xy_IX_eIX()

        # Fit
        self.result = leastsqFit(
            self.get_function(), (x, y), self.get_supposed_parameters(), IX,
            err=eIX,
            doNotFit=self.get_not_fitted(),
            bounds=self.get_bounds(),
            verbose=self.verbose
        )
        set_aa(EA.CHI2, self.result[2])

        # Log
        log(0, "Fit efectuated in %f seconds" % (time.time() - start_time),
            "with function:\n", self.fit_fct, '(if lambda, look above fit log)',
            "\n\n\n\n"
            )

        log(9, 'Fit, result error', self.result[1])
        return self

    @abstractmethod
    def get_xy_IX_eIX(self): pass

    def get_function(self):
        return self.fit_fct

    @abstractmethod
    def get_supposed_parameters(self):
        """Warning, each parameter here will be fitted
        Detect uselesss parameters <- error returned is -1
        """
        supposed_param = {
            'theta': 0.1,
        }
        # Background
        if get_state().e_sky_type in (ESky.MANUAL, ESky.NONE):
            supposed_param['background'] = get_state().i_background
        else:
            supposed_param['background'] = 0

        # Saturation stair top: supposing 30.000 <- 007 is not enought
        if self.b_saturated:
            supposed_param['saturation'] = 5000
        else:
            supposed_param['saturation'] = float('inf')

        return supposed_param


    @abstractmethod
    def get_not_fitted(self):
        """Saturation and background
        Children ! Do your job ! (i.e. check aniso and same psf)
        """
        doNotFit = []
        if get_state().e_sky_type in (ESky.NONE, ESky.MANUAL):
            doNotFit.append('background')
        if not self.b_saturated:
            doNotFit.append('saturation')
        return doNotFit


    @abstractmethod
    def get_bounds(self):
        """Universal bounds, if not used nevermind"""
        bounds = {
            # Theta not rotating (avoid useless time lost)
            'theta': (-0.1, 3.24),
            # Undegenerate Moffat (a little, I could be stricter) (should I ?)
            'exponent': (1.1, 10),
            'b0': (1.1, 10),
            'b1': (1.1, 10),
            # Positive Saturation
            'saturation': (-0.1, None),
            # Positive spread
            'spread_x': (-0.1, None),
            'spread_y': (-0.1, None),
            'spread_x0': (-0.1, None),
            'spread_x1': (-0.1, None),
            'spread_y0': (-0.1, None),
            'spread_y1': (-0.1, None),
            # Positive Intensity
            'intensity': (-0.1, None),
            'intensity0': (-0.1, None),
            'intensity1': (-0.1, None),
        }
        return bounds

    @abstractmethod
    def get_result(self): pass


class OnePsf(Fit):
    """Fit Point Spread Function of a single source"""
    def __init__(self, grid, rectangle, center=(0, 0), my_max=1):
        super().__init__(grid)

        self.rectangle = rectangle
        self.center = center
        self.my_max = my_max

        self.fwhm = IF.FWHM(self.grid, self.center)

        # Change call if no fit
        if self.fit_fct is None:
            self.do_fit = self.no_fit


    def no_fit(self):
        fit_dic = {
            'center_x': self.center[0], 'center_y': self.center[1],
            'intensity': self.my_max,
            "r99x": 5 * self.fwhm, "r99y": 5 * self.fwhm,
            "spread_x": self.fwhm, "spread_y": self.fwhm,
            'theta': 0,
        }
        err_dic = {
            'center_x': 1, 'center_y': 1,
            'intensity': np.sqrt(self.my_max),
            "r99x": 5, "r99y": 5,
            "spread_x": 1, "spread_y": 1,
            'theta': 2 * np.pi,
        }
        set_aa(EA.CHI2, float('nan'))
        log(0, "No fit effectuated <- fit type None selected")
        self.result = (fit_dic, err_dic, 0, None, 0)
        return self


    def get_xy_IX_eIX(self):
        # In center and bound
        rx1, rx2, ry1, ry2 = self.rectangle
        log(3, "OnePsf: ", rx1, rx2, ry1, ry2, 'center :', self.center)

        # Get working grid
        X, Y = np.arange(int(rx1), int(rx2)), np.arange(int(ry1), int(ry2))
        y, x = np.meshgrid(Y, X)        # We have to inverse because of matrix way
        IX = self.grid[rx1:rx2, ry1:ry2]  # the cutted image

        # Mask bad pixel
        IX, _, eIX = IF.find_bad_pixel(IX)

        return (x, y), IX, eIX


    def get_supposed_parameters(self):
        supposed_param = super().get_supposed_parameters()
        supposed_param.update({
            'center_x': self.center[0],
            'center_y': self.center[1],
            'spread_x': 0.83 * (self.fwhm),
            'intensity': self.my_max,
        })
        if self.fit_fct is BF.Gaussian2D:
            tmp = {"spread_y": supposed_param["spread_x"]}
            supposed_param.update(tmp)

        elif self.fit_fct is BF.Gaussian:
            pass

        elif self.fit_fct is BF.Moffat:
            # 1.5 = /np.sqrt(1/2**(-1/b)-1)
            supposed_param.update({'spread_x': 1.5 * self.fwhm, 'exponent': 2})

        elif self.fit_fct is BF.Moffat2D:
            # 0.83 = sqrt(ln(2))
            tmp = {
                "spread_y": supposed_param["spread_x"], "exponent": 2}
            supposed_param.update(tmp)

        elif self.fit_fct is BF.Bessel1:
            pass

        elif self.fit_fct is BF.Bessel12D:
            # 0.83 = sqrt(ln(2))
            tmp = {"spread_y": supposed_param["spread_x"]}
            supposed_param.update(tmp)

        return supposed_param


    def get_not_fitted(self):
        doNotFit = super().get_not_fitted()
        if not get_state().b_aniso:
            doNotFit.append("theta")
            doNotFit.append("spread_y")
        return doNotFit


    def get_bounds(self):

        x0, y0 = self.center
        local_median = np.median(
            self.grid[int(x0)-1:int(x0)+2, int(y0)-1: int(y0+2)])
        bounds = super().get_bounds()

        bounds.update({
            "center_x": [x0 - 10, x0 + 10],
            "center_y": [y0 - 10, y0 + 10],
            "background": [None, self.my_max],
            "instensity": [local_median, 2.3 * self.my_max - local_median]
        })

        return bounds


    def get_result(self):
        # Care if not aniso stuff to full x and y
        is_aniso = not get_state().b_aniso and self.fit_fct is not None
        if is_aniso:
            try:
                self.result[0]["spread_y"], self.result[0]["spread_x"] = \
                    self.result[0]["spread"], self.result[0]["spread"]
                self.result[1]["spread_y"], self.result[1]["spread_x"] = \
                    self.result[1]["spread"], self.result[1]["spread"]
            except:
                self.result[0]["spread_y"], self.result[0]["spread_x"] = \
                    self.result[0]["spread_x"], self.result[0]["spread_x"]
                self.result[1]["spread_y"], self.result[1]["spread_x"] = \
                    self.result[1]["spread_x"], self.result[1]["spread_x"]

        # Update R99
        (r99x, r99y), (r99u, r99v) = IF.EnergyRadius(
            self.grid, dic=self.result[0])
        self.result[0]["number_count"] = r99x * r99y
        self.result[0]["r99x"], self.result[0]["r99y"] = r99x, r99y
        self.result[0]["r99u"], self.result[0]["r99v"] = r99u, r99v

        # Save && Ret
        get_state().d_fit_param = self.result[0]
        get_state().d_fit_error = self.result[1]
        log(9, 'OnePsf, result error', self.result[1])
        return self.result


class BinaryPsf(Fit):
    """Fit two star function together
    TODO log in base class
    """
    def __init__(self, grid, star1, star2):
        super().__init__(grid)
        self.star1 = star1
        self.star2 = star2

        # Calculate distance between two pooints
        (x1, y1), (x2, y2) = self.star1, self.star2
        self.star_distance = np.sqrt((x1-x2)**2 + (y1-y2)**2)
        self.dist1 = min(IF.FWHM(self.grid, self.star1), self.star_distance / 2)
        self.dist2 = min(IF.FWHM(self.grid, self.star2), self.star_distance / 2)


    def get_xy_IX_eIX(self):
        # pylint: disable = too-many-locals
        (x1, y1), (x2, y2) = self.star1, self.star2
        center = [(x1+x2)/2, (y1+y2)/2]

        # Define fitting space
        fit_range = self.star_distance + 5 * max(self.dist1, self.dist2)
        rx1 = int(center[0] - fit_range / 2)
        rx2 = int(center[0] + fit_range / 2)
        ry1 = int(center[1] - fit_range / 2)
        ry2 = int(center[1] + fit_range / 2)

        rx1, rx2, ry1, ry2 = IF.Order4(
            (rx1, rx2, ry1, ry2),
            grid=self.grid)

        log(3, "----->IF.BinaryPSF :", "The fit is done between points ",
            (rx1, ry1), " and ", (rx2, ry2), "with fit", self.s_fit_type)

        X, Y = np.arange(int(rx1), int(rx2)+1), np.arange(int(ry1), int(ry2)+1)
        y, x = np.meshgrid(Y, X)
        IX = self.grid[int(rx1):int(rx2+1), int(ry1):int(ry2+1)]
        IX, _, eIX = IF.find_bad_pixel(IX)

        log(3, "Binary shapes :", X.shape, Y.shape, IX.shape, eIX.shape)
        return (x, y), IX, eIX


    def get_supposed_parameters(self):
        (x1, y1), (x2, y2) = self.star1, self.star2
        supposed_param = super().get_supposed_parameters()
        supposed_param.update({
            'x0': x1, 'y0': y1,
            'x1': x2, 'y1': y2,
            'spread_x0': 0.83 * self.dist1, 'spread_x1': 0.83 * self.dist2,
            'spread_y0': 0.83 * self.dist1, 'spread_y1': 0.83 * self.dist2,
            'intensity0': self.grid[int(x1)][int(y1)],
            'intensity1': self.grid[int(x2)][int(y2)],
            "theta": 1,
        })

        if "Moffat" in self.s_fit_type:
            supposed_param['b0'], supposed_param['b1'] = 1.8, 1.8

        log(3, "Binary FiT, supposed parameters : ", supposed_param)
        return supposed_param


    def get_not_fitted(self):
        doNotFit = super().get_not_fitted()
        if get_state().b_same_psf:
            doNotFit.append("spread_x1")
            doNotFit.append("spread_y1")
            if not self.b_aniso:
                doNotFit.append("spread_y0")
                doNotFit.append("theta")
            if "Moffat" in self.s_fit_type:
                doNotFit.append("b1")
        else:  # not same psf
            if not self.b_aniso:
                doNotFit.append("spread_y0")
                doNotFit.append("spread_y1")
                doNotFit.append("theta")

        return doNotFit


    def get_bounds(self):
        # bd_x0 = (x1 - star_distance/2, x1 + star_distance/2)
        # bd_y0 = (y1 - star_distance/2, y1 + star_distance/2)

        # bd_x1 = (x2 - star_distance/2, x2 + star_distance/2)
        # bd_y1 = (y2 - star_distance/2, y2 + star_distance/2)

        bounds = super().get_bounds()
        bounds.update({
            # 'x0':bd_x0,
            # 'x1':bd_x1,
            # 'y0':bd_y0,
            # 'y1':bd_y1,
        })

        return bounds


    def get_result(self):
        # Declare: Restore not fitted variables
        def restore(lst, to_change, reference):
            lst[0][to_change] = lst[0][reference]
            lst[1][to_change] = lst[1][reference]
            return lst

        if get_state().b_same_psf:
            self.result = restore(self.result, "spread_x1", "spread_x0")
            self.result = restore(self.result, "spread_y1", "spread_y0")
            if not self.b_aniso:
                self.result = restore(self.result, "spread_y0", "spread_x0")
            if "Moffat" in self.s_fit_type:
                self.result = restore(self.result, "b1", "b0")
        else:  # not same psf
            if not self.b_aniso:
                self.result = restore(self.result, "spread_y0", "spread_x0")
                self.result = restore(self.result, "spread_y1", "spread_x1")

        get_state().d_fit_param = self.result[0]
        get_state().d_fit_error = self.result[1]
        return self.result


class TightBinaryPsf(BinaryPsf):
    """Just better bounds"""
    def get_bounds(self):
        (x1, y1), (x2, y2) = self.star1, self.star2

        cut1 = get_state().image.im0[
            int(x1-2): int(x1+2), int(y1-2): int(y1+2)]
        min1 = np.median(cut1)
        max1 = np.max(cut1)
        max1 = 2*max1 - min1

        cut2 = get_state().image.im0[
            int(x2-2): int(x2+2), int(y2-2): int(y2+2)]
        min2 = np.median(cut2)
        max2 = np.max(cut2)
        max2 = 2*max2 - min2

        bounds = super().get_bounds()
        # we put the intensity positive because in a binary fit situation
        # ... you know.... who knows
        bounds.update({
            'x0': (x1-2, x1+2),
            'x1': (x2-2, x2+2),
            'y0': (y1-2, y1+2),
            'y1': (y2-2, y2+2),
            'intensity0': (min1, None),
            'intensity1': (min2, None)
        })

        # Stricter moffat
        if "Moffat" in self.s_fit_type:
            bounds['b0'] = (1, 3)
            bounds['b1'] = (1, 3)

        return bounds

from abc import ABC, abstractmethod

import numpy as np

from abism.back import ImageFunction as IF
from abism.back.fit_helper import leastsqFit
import abism.back.fit_template_function as BF
from abism.back.image_info import ImageInfo, get_array_stat


from abism.util import log, get_root, get_state, EA
import abism.back.util_back as W



class Fit(ABC):
    """Base class to perform a Fit"""
    def __init__(self, grid):
        self.grid = grid

        # Retrieve fit_type
        self.fit_type = get_state().fit_type
        self.fit_type = enhance_fit_type(self.fit_type)

        # Retrieve verbose
        self.verbose = get_state().verbose > 0

        self.result = []

    def do_fit(self):
        (x, y), IX, eIX = self.get_xy_IX_eIX()
        log(3, "fit type is : ", self.fit_type)
        self.result = leastsqFit(
            self.get_function(), (x, y), self.get_supposed_parameters(), IX,
            err=eIX,
            doNotFit=self.get_not_fitted(),
            bounds=self.get_bounds(),
            verbose=self.verbose
        )
        return self

    @abstractmethod
    def get_xy_IX_eIX(self): pass

    @abstractmethod
    def get_function(self): pass

    @abstractmethod
    def get_supposed_parameters(self): pass

    @abstractmethod
    def get_not_fitted(self): pass

    @abstractmethod
    def get_bounds(self): pass

    @abstractmethod
    def get_result(self): pass


class PsfFit(Fit):
    """Fit Point Spread Function of a single source"""
    def __init__(self, grid, rectangle, center=(0, 0), my_max=1):
        super().__init__(grid)

        self.rectangle = rectangle
        self.center = center
        self.my_max = my_max

        self.fwhm = IF.FWHM(self.grid, self.center)

        # Change call if no fit
        if self.fit_type == "None":
            self.do_fit = self.no_fit


    def no_fit(self):
        restmp = {
            'center_x': self.center[0], 'center_y': self.center[0],
            'intensity': self.my_max,
            "r99x": 5 * self.fwhm, "r99y": 5 * self.fwhm}
        self.result = (restmp, 0, 0, None, 0)
        return self


    def get_xy_IX_eIX(self):
        # In center and bound
        (rx1, rx2, ry1, ry2) = list(map(int, self.rectangle))
        log(3, "PsfFit: ", rx1, rx2, ry1, ry2, 'center :', self.center)

        # Get working grid
        X, Y = np.arange(int(rx1), int(rx2)+1), np.arange(int(ry1), int(ry2)+1)
        y, x = np.meshgrid(Y, X)        # We have to inverse because of matrix way
        IX = self.grid[rx1:rx2+1, ry1:ry2+1]  # the cutted image

        # Mask bad pixel (TODO look at that)
        IX, mIX = IF.FindBadPixel(IX)
        eIX = (IX-mIX).std() * np.ones(IX.shape)

        return (x, y), IX, eIX


    def get_function(self):
        return vars(BF)[self.fit_type]

    def get_supposed_parameters(self):
        x0, y0 = self.center
        suposed_param = {
            'center_x': self.center[0],
            'center_y': self.center[1],
            'spread_x': 0.83 * (self.fwhm),
            'intensity': self.my_max,
            'background': 0
        }

        if self.fit_type == "Gaussian2D":
            tmp = {"spread_y": suposed_param["spread_x"], "theta": 0.1}
            suposed_param.update(tmp)

        elif self.fit_type == 'Gaussian':
            pass

        elif self.fit_type == 'Moffat':  # 1.5 = /np.sqrt(1/2**(-1/b)-1)
            suposed_param.update({'spread_x': 1.5 * self.fwhm, 'exponent': 2})

        elif self.fit_type == "Moffat2D":    # 0.83 = sqrt(ln(2))
            tmp = {
                "spread_y": suposed_param["spread_x"], "theta": 0.1, "exponent": 2}
            suposed_param.update(tmp)

        elif self.fit_type == 'Bessel1':
            pass

        elif self.fit_type == "Bessel12D":    # 0.83 = sqrt(ln(2))
            tmp = {"spread_y": suposed_param["spread_x"], "theta": 0.1}
            suposed_param.update(tmp)

        # we consider 2D or not, same_center or not
        elif "Gaussian_hole" in self.fit_type:
            suposed_param.update({
                'center_x_hole': x0, 'center_y_hole': y0,
                'spread_x_hole': 0.83*(self.fwhm)/2,
                'spread_y_hole': 0.83*self.fwhm/2,
                'intensity_hole': 0, 'theta': 0.1, 'theta_hole': 0.1})
            if not "2D" in self.fit_type:
                suposed_param["2D"] = 0
            else:
                suposed_param["2D"] = 1
            if "same_center" in self.fit_type:
                suposed_param["same_center"] = 1

        return suposed_param


    def get_not_fitted(self):
        doNotFit = []
        if get_state().noise_type == 'None' or get_state().noise_type == 'manual':
            doNotFit.append('background')
        elif ("Gaussian_hole" in self.fit_type):
            if not ("2D" in self.fit_type):
                doNotFit.append("theta")
                doNotFit.append("theta_hole")
                doNotFit.append("spread_y")
                doNotFit.append("spread_y_hole")
                doNotFit.append("center_x_hole")
                doNotFit.append("center_y_hole")
            doNotFit.append("2D")
            doNotFit.append("same_center")
        return doNotFit

    def get_bounds(self):
        x0, y0 = self.center
        local_median = np.median(
            self.grid[int(x0)-1:int(x0)+2, int(y0)-1: int(y0+2)])

        fit_bounds = {
            "center_x": [x0 - 10, x0 + 10],
            "center_y": [y0 - 10, y0 + 10],
            "spread_x": [-0.1, None],
            "spread_y": [-0.1, None],
            # "exponent" :[1.2, 6 ],
            "background": [None, self.my_max],
            "instensity": [local_median, 2.3 * self.my_max - local_median]}

        return fit_bounds


    def get_result(self):
        # Update stuff ToRead

        ######
        # DICTIONARY , backup and star improving
        do_improve = not get_state().b_aniso and not self.fit_type == 'None'
        if do_improve:
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

        #############
        # FWHM, and PHOT < from fit
        self.result[0].update(IF.FwhmFromFit(self.result[0], self.fit_type))

        # UPDATE R99X
        (r99x, r99y), (r99u, r99v) = IF.EnergyRadius(
            self.grid, self.fit_type, dic=self.result[0])
        self.result[0]["number_count"] = r99x * r99y
        self.result[0]["r99x"], self.result[0]["r99y"] = r99x, r99y
        self.result[0]["r99u"], self.result[0]["r99v"] = r99u, r99v

        return self.result


class BinaryPsf(Fit):
    """Fit two star function together
    TODO log in base class
    """
    def __init__(self, grid, star1, star2):
        super().__init__(grid)
        self.star1 = star1
        self.star2 = star2

        # Check not Bessel
        if (not "Gaussian" in self.fit_type) and (not "Moffat" in self.fit_type):
            log(0, "WARNING : There is no bessel, None, and Gaussian hole fit "
                "type for binary fi, fit type is set to gaussian")
            self.fit_type = "Gaussian"

        # Calculate distance between two pooints
        (x1, y1), (x2, y2) = self.star1, self.star2
        self.star_distance = np.sqrt((x1-x2)**2 + (y1-y2)**2)
        self.dist1 = min(IF.FWHM(self.grid, self.star1), self.star_distance / 2)
        self.dist2 = min(IF.FWHM(self.grid, self.star2), self.star_distance / 2)


    def get_xy_IX_eIX(self):
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
            (rx1, ry1), " and ", (rx2, ry2), "with fit", self.fit_type)

        X, Y = np.arange(int(rx1), int(rx2)+1), np.arange(int(ry1), int(ry2)+1)
        y, x = np.meshgrid(Y, X)
        IX = self.grid[int(rx1):int(rx2+1), int(ry1):int(ry2+1)]
        IX, mIX = IF.FindBadPixel(IX)  # ,r=r)

        # the error
        eIX = (IX-mIX).std()
        eIX *= np.ones(IX.shape)
        log(3, "Binary shapes :", X.shape, Y.shape, IX.shape, eIX.shape)
        return (x, y), IX, eIX


    def get_function(self):
        dic_for_fit = {
            "same_psf": get_state().b_same_psf,
            "aniso": get_state().b_aniso,
        }
        log(3, "anisoplanetism=" + str(bool(dic_for_fit["aniso"])),
            "same_psf="+str(bool(dic_for_fit["same_psf"])))
        return lambda x, y: \
            vars(BF)[self.fit_type.replace("2D", "")+"2pt"](x, y, dic=dic_for_fit)


    def get_supposed_parameters(self):
        (x1, y1), (x2, y2) = self.star1, self.star2
        suposed_param = {
            'x0': x1, 'y0': y1,
            'x1': x2, 'y1': y2,
            'spread_x0': 0.83 * self.dist1, 'spread_x1': 0.83 * self.dist2,
            'spread_y0': 0.83 * self.dist1, 'spread_y1': 0.83 * self.dist2,
            'intensity0': self.grid[int(x1)][int(y1)],
            'intensity1': self.grid[int(x2)][int(y2)],
            'background': 0, "theta": 1}

        if "Moffat" in self.fit_type:
            suposed_param['b0'], suposed_param['b1'] = 1.8, 1.8

        log(3, "Binary FiT, supposed parameters : ", suposed_param)
        return suposed_param


    def get_not_fitted(self):
        doNotFit = []
        if get_state().b_same_psf:
            doNotFit.append("spread_x1")
            doNotFit.append("spread_y1")
            if not "2D" in self.fit_type:
                doNotFit.append("spread_y0")
                doNotFit.append("theta")
            if "Moffat" in self.fit_type:
                doNotFit.append("b1")
        else:  # not same psf
            if not "2D" in self.fit_type:
                doNotFit.append("spread_y0")
                doNotFit.append("spread_y1")
                doNotFit.append("theta")

        return doNotFit


    def get_bounds(self):
        # ###########
        # # make the bounds
        # bd_x0 = (x1 - star_distance/2, x1 + star_distance/2)
        # bd_y0 = (y1 - star_distance/2, y1 + star_distance/2)

        # bd_x1 = (x2 - star_distance/2, x2 + star_distance/2)
        # bd_y1 = (y2 - star_distance/2, y2 + star_distance/2)

        bounds = {
            # 'x0':bd_x0,
            # 'x1':bd_x1,
            # 'y0':bd_y0,
            # 'y1':bd_y1,
            'spread_x0': (-0.1, None),
            'spread_x1': (-0.1, None),
            'spread_y0': (-0.1, None),
            'spread_y1': (-0.1, None),
            'intensity0': (-0.1, None),
            'intensity1': (-0.1, None),
            'background': (0, None),
            "theta": (-0.1, 3.24)}

        if "Moffat" in self.fit_type:
            bounds['b0'] = (1, 10)
            bounds['b1'] = (1, 10)

        return bounds


    def get_result(self):
        ##############
        # restore not fitted variables
        def restore(lst, to_change, reference):
            lst[0][to_change] = lst[0][reference]
            lst[1][to_change] = lst[1][reference]
            return lst

        if get_state().b_same_psf:
            self.result = restore(self.result, "spread_x1", "spread_x0")
            self.result = restore(self.result, "spread_y1", "spread_y0")
            if not "2D" in self.fit_type:
                self.result = restore(self.result, "spread_y0", "spread_x0")
            if "Moffat" in self.fit_type:
                self.result = restore(self.result, "b1", "b0")
        else:  # not same psf
            if not "2D" in self.fit_type:
                self.result = restore(self.result, "spread_y0", "spread_x0")
                self.result = restore(self.result, "spread_y1", "spread_x1")

        # BACKKUP DIC
        tmp = {}
        tmp.update(self.result[0])
        self.result[0]["fit_dic"] = tmp

        # FWHM , Photo < from fit
        dic_copy0 = self.result[0].copy()
        dic_copy1 = self.result[0].copy()
        for key in self.result[0].keys():
            if "0" in key:
                dic_copy0[key.replace("0", "")] = dic_copy0[key]
            elif "1" in key:
                dic_copy1[key.replace("1", "")] = dic_copy1[key]
            # nevermind the center x0 and x1
        try:
            dic_copy0["exponent"] = dic_copy0["b0"]
        except:
            pass
        try:
            dic_copy1["exponent"] = dic_copy1["b1"]
        except:
            pass

        tmp = IF.FwhmFromFit(dic_copy0, self.fit_type)
        self.result[0].update({
            "fwhm_x0": tmp["fwhm_x"],
            "fwhm_y0": tmp["fwhm_y"],
            "photometry_fit0": tmp["photometry_fit"],})

        tmp = IF.FwhmFromFit(dic_copy1, self.fit_type)
        self.result[0].update({
            "fwhm_x1": tmp["fwhm_x"],
            "fwhm_y1": tmp["fwhm_y"],
            "photometry_fit1": tmp["photometry_fit"]})


        self.result[0]["my_photometry0"], self.result[0]["my_photometry1"] = self.result[0]["photometry_fit0"], self.result[0]["photometry_fit1"]

        return self.result


class TightBinaryPsf(BinaryPsf):
    """Just better bounds"""
    def __init__(self, grid, star1, star2):
        super().__init__(grid, star1, star2)


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

        if "Moffat" in self.fit_type:
            bounds['b0'] = (1, 3)
            bounds['b1'] = (1, 3)

        return bounds



# Not used
######################################################################


def EllipseEventBack(obj):
    """Return: background from ellipse <int(adu)>"""
    rui, rvi = obj.ru, obj.rv     # inner annulus
    ruo, rvo = 2*obj.ru, 2 * obj.rv  # outer annulus

    ell_i = IF.EllipticalAperture(
        get_state().image.im0,
        dic={"center_x": obj.x0, "center_y": obj.y0, "ru": rui,
             "rv": rvi, "theta": obj.theta})  # inner

    ell_o = IF.EllipticalAperture(
        get_state().image.im0,
        dic={"center_x": obj.x0, "center_y": obj.y0, "ru": ruo,
             "rv": rvo, "theta": obj.theta})  # outter

    # annulus  inside out but not inside in
    bol_a = ell_o["bol"] ^ ell_i["bol"]

    image_cut = get_root().im0[bol_a]
    stat = get_array_stat(image_cut)

    stat["mean"]


def EllipseEventPhot(obj):
    """Elliptical phot
    Returns: photometry, total, number_count
    """

    ###########
    # CAlculate Ellipse stats (phot) update phot
    dic = {"center_x": obj.x0, "center_y": obj.y0,
           "ru": obj.ru, "rv": obj.rv, "theta": obj.theta}
    ellipse_stat = IF.EllipticalAperture(
        obj.array, dic=dic, full_answer=True)

    number_count, total = ellipse_stat['sum'], ellipse_stat['number_count']
    photometry = total - get_state().get_answer(EA.BACKGROUND)

    # SAve photo
    get_state().add_answer(EA.PHOTOMETRY, photometry)
    return photometry, total, number_count


def EllipseEventMax(obj):  # receive EllipseEvent

    rad = max(obj.ru, obj.rv)
    r = (obj.x0-rad, obj.x0+rad+1, obj.y0-rad, obj.y0+rad+1)
    local_max = IF.LocalMax(get_state().image.im0, r=r)  # With bad pixel filter

    ######
    # Update
    W.strehl.update({"center_x": local_max[0],
                     "center_y": local_max[1],
                     "intensity": local_max[2],
                     })
    return

    ###############
    # ANNULUS CANVAS
    #################


def AnnulusEventPhot(obj):  # Called by Gui/Event...py  Event object
    res = {}

    center_x = obj.x0  # from image to array but coord in array type
    center_y = obj.y0
    theta = obj.theta

    if obj.outter_u < obj.inner_u:  # put outter radius after inner
        tmp = obj.inner_u
        obj.inner_u = obj.outter_u
        obj.outter_u = tmp

    # DEIFINE THE Bollean of being inside the elliptical aperture
    ru = obj.ru
    rv = obj.ru * obj.rapport
    bol_e = EllipticalAperture(obj.array, dic={"center_x": center_x, "center_y": center_y, "ru": ru, "rv": rv, "theta": theta})[
        "bol"]  # ellipse , photomretry

    ru, rv = obj.inner_u, obj.inner_u*obj.rapport
    bol_i = EllipticalAperture(obj.array, dic={
                               "center_x": center_x, "center_y": center_y, "ru": ru, "rv": rv, "theta": theta})["bol"]  # inner

    ru, rv = obj.outter_u, obj.outter_u*obj.rapport
    bol_o = EllipticalAperture(obj.array, dic={
                               "center_x": center_x, "center_y": center_y, "ru": ru, "rv": rv, "theta": theta})["bol"]  # outter

    bol_a = bol_o ^ (bol_i)  # annulus  inside out but not inside in
    phot, number_count = np.sum(obj.array[bol_e]), len(obj.array[bol_e])
    back, number_back = np.sum(obj.array[bol_a]), len(obj.array[bol_a])

    # PHOT and back
    iminfo_cut = ImageInfo(obj.array[bol_a])
    res["background_dic"] = iminfo_cut.sky()
    res["my_background"] = res["background_dic"]["mean"]
    res["phot"] = np.sum(obj.array[bol_e])
    res["my_photometry"] = res["phot"] - \
        len(obj.array[bol_e])*res["my_background"]

    log(2, "phot1 :", res["phot"])
    log(2, "phot2 :", res["my_photometry"])
    log(2, "back :", res["my_background"], "\n")


# Helpers
######################################################################

def Photometry(grid, background, rectangle=None):
    """Make photometry of region
    In: center, r99
        Only one reading variable photometric type
        background
    Returns: photometry, total, number_count
             1. total phtotometric adu (backgound subtracted)
             Other. to estimate error
    Note Background must be called before
    """
    photometry = total = number_count = 0

    r99x, r99y = W.strehl['r99x'], W.strehl['r99y']
    r99u, r99v = W.strehl['r99u'], W.strehl['r99v']
    theta = W.strehl.get('theta', 0)

    x0, y0 = W.strehl['center_x'], W.strehl['center_y']
    ax1, ax2 = int(x0-r99x), int(x0+r99x)
    ay1, ay2 = int(y0-r99y), int(y0+r99y)

    # FIT
    if get_state().phot_type == 'fit':
        W.strehl["my_photometry"] = W.strehl["photometry_fit"]
        log(3, "doing fit  phot in ImageFunction.py ")

    # Rectangle apperture
    elif get_state().phot_type == 'encircled_energy':
        log(3, 'Photometry <- encircled energy (i.e. rectangle)')
        total = np.sum(grid[ax1:ax2, ay1:ay2])
        number_count = 4 * r99x * r99y
        photometry = total - number_count * background

    # Elliptical apperture
    elif get_state().phot_type == 'elliptical_aperture':
        log(3, 'Photometry <- elliptical aperture')
        ellipse_dic = {"center_x": x0, "center_y": y0,
                       "ru": r99u, "rv": r99v, "theta": theta}
        bol = IF.EllipticalAperture(grid, dic=ellipse_dic)["bol"]
        image_elliptic = grid[bol]

        stat = get_array_stat(image_elliptic)
        number_count = stat.number_count
        total = stat.sum
        photometry = total  - number_count * background

    # MANUAL
    elif get_state().phot_type == 'manual':
        stat = get_state().image.RectanglePhot(rectangle)
        total = stat.sum
        number_count = stat.number_count
        photometry = total  - number_count * background


    return photometry, total, number_count


def Background(grid, rectangle):
    # Log
    background_type = get_state().noise_type
    log(3, 'Getting Background with type', background_type)

    res = 0

    # BAckground and rms
    dic = W.strehl
    r = rectangle

    # IN RECT
    if get_state().noise_type == 'in_rectangle':  # change noise  from fit
        dic['my_background'] = back / back_count
        rms = 0.
        for i in listrms:
            rms += (i-dic['my_background'])**2
        rms = np.sqrt(rms/(len(listrms)-1))
        dic['rms'] = rms

    # 8 RECTS
    elif get_state().noise_type == '8rects':
        xtmp, ytmp = dic['center_x'], dic['center_y']
        r99x, r99y = dic["r99x"], dic["r99y"]
        restmp = IF.EightRectangleNoise(
            grid, (xtmp-r99x, xtmp+r99x, ytmp-r99y, ytmp+r99y))
        dic['my_background'], dic['rms'] = restmp["background"], restmp['rms']
        log(3, "ImageFunction.py : Background, I am in 8 rects ")

    # MANUAL
    elif get_state().noise_type == "manual":
        dic["my_background"] = get_state().i_background
        dic["rms"] = 0

    # FIT
    elif get_state().noise_type == 'fit':
        if get_state().fit_type == "None":
            log(0, "\n\n Warning, cannot estimate background with fit if fit type = None, return to Annnulus background")
            param = param.copy()
            param.update({"noise": "annulus"})
            return Background(get_state().image.im0, param=param)
        try:
            dic['rms'] = W.psf_fit[1]['background']
        except:
            dic['rms'] = ["No_in_fit"]
        dic['my_background'] = dic["background"]

    # NONE
    elif get_state().noise_type == 'None':
        dic['my_background'] = dic['my_background'] = 0
        # dic['rms'] = 0

    # ELLIPTICAL ANNULUS
    elif get_state().noise_type == "elliptical_annulus":
        W.ell_inner_ratio, W.ell_outer_ratio = 1.3, 1.6
        rui, rvi = 1.3 * W.strehl["r99u"], 1.3 * W.strehl["r99v"]
        ruo, rvo = 1.6 * W.strehl["r99u"], 1.6 * W.strehl["r99v"]

        # CUT
        myrad = max(ruo, rvo) + 2  # In case
        ax1 = int(W.strehl["center_x"] - myrad)
        ax2 = int(W.strehl["center_x"] + myrad)
        ay1 = int(W.strehl["center_y"] - myrad)
        ay2 = int(W.strehl["center_y"] + myrad)
        ax1, ax2, ay1, ay2 = IF.Order4((ax1, ax2, ay1, ay2), grid=grid)
        image_cut = get_state().image.im0[ax1: ax2, ay1: ay2]

        bol_i = IF.EllipticalAperture(
            image_cut, dic={"center_x": myrad, "center_y": myrad, "ru": rui,
                            "rv": rvi, "theta": W.strehl["theta"]})["bol"]

        bol_o = IF.EllipticalAperture(
            image_cut, dic={"center_x": myrad, "center_y": myrad, "ru": ruo,
                            "rv": rvo, "theta": W.strehl["theta"]})["bol"]

        bol_a = bol_o ^ bol_i

        iminfo_cut = ImageInfo(image_cut[bol_a])
        tmp = iminfo_cut.sky()
        dic['rms'] = tmp["rms"]
        dic['my_background'] = tmp["mean"]

    else:
        dic['rms'] = -99
        dic['my_background'] = -99

    return dic

    ###############
    # BINARY
    ###############


# TODO refactor all that in the caller discriminator
def enhance_fit_type(name):  # strange but works
    fit_type = name
    try:
        if get_state().b_aniso and not '2D' in fit_type:
            fit_type += '2D'
        elif not get_state().b_aniso:
            fit_type = fit_type.replace('2D', '')
    except BaseException:
        if fit_type.find('2D') == -1:
            fit_type += '2D'
    if not fit_type.find('None') == -1:
        fit_type = 'None'

    log(0, 'Fit Type = ' + fit_type)
    return fit_type

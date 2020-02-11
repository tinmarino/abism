"""
    To pretty print the answer, may go to FrameText
    C'est le bordel !
"""

from abc import ABC, abstractmethod

import tkinter as tk
import numpy as np
import matplotlib

# Back
from abism.back import ImageFunction as IF
import abism.back.fit_template_function as BF

# Plugin
from abism.util import log, get_root, get_state, get_av, EA, EPick, EPhot, ESky


def tktext_insert_answer(self, answer, with_error=False, tags=None):
    """Insert an answer in a tktext"""
    # Clean in
    # # Convert answer
    if isinstance(answer, EA):
        answer = get_state().get_answer_obj(answer)
    # # Convert error
    if with_error:
        error = answer.error
    else:
        error = None
    # # Convert unit && Convert tag
    if not isinstance(answer.unit, (list, tuple)):
        answer.unit = answer.unit, answer.unit
    if not tags: tags = []

    # Get set tab len
    i_tab = vars(self).get('i_tab_len', 0)
    self.i_tab_len = max(i_tab, len(answer.text))

    # Init Stg with name
    stg = answer.text + ":\t"

    # Get value and error
    if get_state().s_answer_unit == 'detector':
        stg += answer.str_detector()
        if error:
            stg += ' ± ' + error.str_detector()
        stg += answer.unit[0]
    else:
        stg += answer.str_sky()
        if error:
            stg += ' ± ' + error.str_sky()
        stg += answer.unit[1]

    # Add new line
    stg += "\n"

    # Insert
    self.insert(tk.END, stg, tags)
tk.Text.insert_answer = tktext_insert_answer


def tktext_insert_warnings(self):
    """Insert all warning from analyse in tk text widget"""
    stg = ''

    # Saturated
    if 'intensity' not in get_state().d_fit_param:  # binary
        intensity = get_state().d_fit_param["intensity0"] + get_state().d_fit_param["intensity1"]
    else:
        intensity = get_state().d_fit_param["intensity"]

    if intensity > get_root().header.non_linearity_level:
        if intensity > 1.0 * get_root().header.saturation_level:
            stg += "!!! SATURATED !!!  Strehl is UNRELIABLE\n"
        else:
            stg += "!!! NON-LINEAR Strehl may be  unreliable\n"

    # Undersampled
    is_undersampled = "sinf_pixel_scale" in vars(get_root().header)
    is_undersampled = is_undersampled and get_root().header.sinf_pixel_scale <= 0.01
    if is_undersampled:
        stg += "!!! UNDER-SAMPLED !!! Use FWHM\n (SR under-estimated)\n"

    # Binary too far
    if get_state().e_pick_type in (EPick.BINARY, EPick.TIGHT):
        max_dist = max(get_state().d_fit_param["spread_x0"] + get_state().d_fit_param["spread_x1"],
                       get_state().d_fit_param["spread_y0"] + get_state().d_fit_param["spread_y1"])
        sep = (get_state().d_fit_param["x0"] - get_state().d_fit_param["x1"])**2
        sep += (get_state().d_fit_param["y0"] - get_state().d_fit_param["y1"])**2
        sep = np.sqrt(sep)

        if max_dist*15 < sep:  # means too high separation
            stg += "Wide Binary\npick objects individually\n"

        if max_dist*3 > sep:  # means too high separation
            stg += "Tight Binary\nmay be unreliable\n"

    # Insert
    self.insert(tk.END, stg, ['tag-important', 'tag-center'])
tk.Text.insert_warnings = tktext_insert_warnings


def tktext_insert_answer_list(self, lst):
    """answer, error, tags"""
    for ans in lst:
        l = len(ans)
        answer = ans[0]
        with_error = ans[1] if l > 1 else False
        tags = ans[2] if l > 2 else None
        self.insert_answer(answer, with_error=with_error, tags=tags)
tk.Text.insert_answer_list = tktext_insert_answer_list


def show_answer():
    """Draw && Print answer i.e. Image and Text
    Discirminate according to pick"""
    pick = get_state().e_pick_type

    if pick == EPick.ONE:
        PrinterOne().work()
        plot1d_one()
        plot2d_one()

    elif pick in (EPick.BINARY, EPick.TIGHT):
        PrinterBinary().work()
        plot1d_binary()
        plot2d_binary()

    elif pick == EPick.ELLIPSE:
        PrinterEllipse().work()


class AnswerPrinter(ABC):
    """Base class to print answer in text frame"""
    def work(self, with_warning=True, on_coord=show_answer):
        # Grid tk text
        text = get_root().frame_answer.get_new_text_frame(on_coord)

        # Get class dependant list
        lst = self.get_list()

        # Insert CHI2
        if EA.CHI2 in get_state().answers:
            if get_av(EA.CHI2) > 100:
                lst.append([EA.CHI2, False, ['tag-important']])
            else:
                lst.append([EA.CHI2, False, ['tag-blue']])

        # Insert element in text
        text.insert_answer_list(lst)

        # Insert Warnings
        if with_warning:
            text.insert_warnings()

        # Disable edit
        text.configure(state=tk.DISABLED)

    @abstractmethod
    def get_list(self):
        """Declare return list: EAnswer, do_print_error, l_tag"""


class PrinterOne(AnswerPrinter):
    """For pick one"""
    def get_list(self):
        return [
            [EA.STREHL, True, ['tag-important']],
            [EA.STREHL_EQ, True],
            [EA.CENTER],
            [EA.FWHM_ABE],
            [EA.PHOTOMETRY],
            [EA.BACKGROUND, True],
            [EA.SN, True],
            [EA.INTENSITY],
        ]


class PrinterBinary(AnswerPrinter):
    """For binary pick or tight binary"""
    def get_list(self):
        return [
            [EA.STREHL1, True, ['tag-important']],
            [EA.STREHL2, True, ['tag-important']],
            [EA.STAR1],
            [EA.STAR2],
            [EA.FWHM1],
            [EA.FWHM2],
            [EA.SEPARATION, True],
            [EA.BACKGROUND, True],
            [EA.PHOTOMETRY1, True],
            [EA.PHOTOMETRY2, True],
            [EA.FLUX_RATIO, True],
            [EA.ORIENTATION],
            [EA.CHI2, False, ['tag-blue']],
        ]


class PrinterEllipse(AnswerPrinter):
    """For ellipse pick"""
    def get_list(self):
        return [
            # TODO error
            [EA.STREHL, True, ['tag-important']],
            [EA.CENTER],
            [EA.PHOTOMETRY],
            [EA.BACKGROUND, True],
            [EA.INTENSITY],
        ]


###############
#   1D 1D 1D
###############


def plot1d_one():
    center = (get_state().d_fit_param['center_x'], get_state().d_fit_param['center_y'])
    #################
    # PLOT radius profile
    params = get_state().d_fit_param
    log(3, 'center=', center)

    fit_fct = BF.get_fit_function()

    # Get ax
    ax = get_root().frame_fit.reset_figure_ax(
        xlabel='Pixel', ylabel='Intensity')

    # Plot x, y
    # we need to give the center (of course)
    x, y = IF.get_profile_x(get_state().image.im0, center)
    # we get a smaller bin for the fitted curve.
    a = np.arange(min(x), max(x), 0.1)
    # RAW  DATA in X
    # x+0.5 to recenter the bar
    ax.plot(x+0.5, y, color='black', drawstyle='steps', linestyle='--',
            linewidth=1, label='Data')

    # Plot encircle line
    r99 = (get_state().d_fit_param['r99x']+get_state().d_fit_param['r99y'])/2
    x0cut, x1cut = center[0]-r99, center[0]+r99
    ax.axvline(x=x0cut, color='black', linestyle='-.', label='99% EE')
    ax.axvline(x=x1cut, color='black', linestyle='-.')
    ax.axhline(y=get_state().get_answer(EA.BACKGROUND), color='black', linestyle=':', label='Sky')

    # Plot Fit
    if get_state().s_fit_type != 'None':
        I_theory = fit_fct((a, params['center_y']), params)
        ax.plot(a, I_theory, color='purple', linewidth=2, label='Fit')

    # Plot perfect diffraction pattern <- putain de if
    if not get_root().header.wavelength*1e-6/get_root().header.diameter/(get_root().header.pixel_scale/206265) < 2:
        params2 = {'diameter': get_root().header.diameter,
                   'lambda': get_root().header.wavelength,
                   'center_x': params['center_x'],
                   'center_y': params['center_y'],
                   'pixelscale': get_root().header.pixel_scale,
                   'phot': get_av(EA.PHOTOMETRY),
                   'obstruction': get_root().header.obstruction/100,
                   }
        bessel = BF.DiffractionPatern((a, params['center_y']), params2)
        ax.plot(a, bessel+ get_av(EA.BACKGROUND),
                color='blue', linewidth=2, label='Ideal PSF')

    #  def Percentage(y):  # y is the intensity
    #      res = 100*(max(MyBessel)-get_state().get_answer(EA.BACKGROUND))*y
    ax.set_xlim(center[0]-r99-5, center[0] + r99 + 5)

    # Update skin && Legend && Draw
    ax.legend(loc=1, prop={'size': 8})
    get_root().frame_fit.redraw()


def plot1d_binary():
    """Draw 1D of binary system"""
    x0, y0 = get_state().d_fit_param["x0"], get_state().d_fit_param["y0"]
    x1, y1 = get_state().d_fit_param["x1"], get_state().d_fit_param["y1"]
    fwhm0, fwhm1 = get_state().d_fit_param["spread_x0"], get_state().d_fit_param["spread_x1"]

    #######
    # EXTREMITIES OF PROFILE LINE ...
    # following the line x0,x1
    # Do not by pass the image borders
    line_len = np.sqrt((x1-x0)**2 + (y1-y0)**2)
    dx0 = (x0-x1) / line_len * 5 * fwhm0
    dy0 = (y0-y1) / line_len * 5 * fwhm0
    dx1 = (x1-x0) / line_len * 5 * fwhm1
    dy1 = (y1-y0) / line_len * 5 * fwhm1

    extremity1 = IF.DoNotPassBorder(get_state().image.im0, (int(x0+dx0), int(y0+dy0)))
    extremity2 = IF.DoNotPassBorder(get_state().image.im0, (int(x1+dx1), int(y1+dy1)))

    ab, od, points = IF.get_radial_line(
        get_state().image.im0, (extremity1, extremity2), return_point=1)
    # TODO use get_fit_fct
    if "Moffat" in get_state().s_fit_type:
        s_fit_type = "Moffat2pt"
    else:
        s_fit_type = "Gaussian2pt"


    # Get star center
    ab_star1 = IF.project_on_radial_line(
        (extremity1, extremity2), reversed(get_av(EA.STAR1)))
    ab_star2 = IF.project_on_radial_line(
        (extremity1, extremity2), reversed(get_av(EA.STAR2)))

    # Smooth fit vectors
    ab_range = ab[0], ab[-1]
    x_range = extremity1[0], extremity2[0]
    y_range = extremity1[1], extremity2[1]
    ab_th = np.arange(ab_range[0], ab_range[1], 0.1)
    x_theory = np.interp(ab_th, ab_range, x_range)
    y_theory = np.interp(ab_th, ab_range, y_range)
    if get_state().s_fit_type is not None:
        I_theory = vars(BF)[s_fit_type](
            (x_theory, y_theory), get_state().d_fit_param)
    else:
        I_theory = 0*x_theory


    ################
    # PLOT
    ax = get_root().frame_fit.reset_figure_ax()

    # Plot fit (0.5 to center)
    ax.plot(ab_th, I_theory, label='Fitted PSF', color='purple', linewidth=2)
    # Plot data
    ax.plot(ab, od, label='Real Profile', color='black', linestyle='steps', linewidth=1)
    # Plot perfect diffraction pattern <- putain de if
    if not get_root().header.wavelength*1e-6/get_root().header.diameter/(get_root().header.pixel_scale/206265) < 2:
        params1 = {'diameter': get_root().header.diameter,
                   'lambda': get_root().header.wavelength,
                   'center_x': get_av(EA.STAR1)[1],
                   'center_y': get_av(EA.STAR1)[0],
                   'pixelscale': get_root().header.pixel_scale,
                   'phot': get_av(EA.PHOTOMETRY1),
                   'obstruction': get_root().header.obstruction/100,
                   }
        bessel1 = BF.DiffractionPatern((x_theory, y_theory), params1)
        params2 = {'diameter': get_root().header.diameter,
                   'lambda': get_root().header.wavelength,
                   'center_x': get_av(EA.STAR2)[1],
                   'center_y': get_av(EA.STAR2)[0],
                   'pixelscale': get_root().header.pixel_scale,
                   'phot': get_av(EA.PHOTOMETRY2),
                   'obstruction': get_root().header.obstruction/100,
                   }
        bessel2 = BF.DiffractionPatern((x_theory, y_theory), params2)
        ax.plot(ab_th, bessel1 + bessel2 + get_av(EA.BACKGROUND),
                color='blue', linewidth=1, label='Ideal PSF')

    # Plot sky
    ax.axhline(y=get_state().get_answer(EA.BACKGROUND), color='black', linestyle=':', label='Sky')
    # Plot star center
    ax.axvline(x=ab_star1, color='black', linestyle='-.', label='Star center')
    ax.axvline(x=ab_star2, color='black', linestyle='-.')

    # Draw
    ax.legend(loc=1, prop={'size': 8})
    get_root().frame_fit.redraw()


####################
#   2D 2D 2D
####################


def plot2d_one():
    """Note the fitted image is in leastqs bound return fit[3]"""
    x0, y0 = get_state().d_fit_param["center_x"], get_state().d_fit_param["center_y"]
    r99x, r99y = get_state().d_fit_param["r99x"], get_state().d_fit_param["r99y"]
    dx1 = int(max(x0-4*r99x, 0))
    dx2 = int(min(x0+4*r99x, len(get_state().image.im0) + 1))
    dy1 = int(max(y0-4*r99y, 0))
    dy2 = int(min(y0+4*r99y, len(get_state().image.im0) + 1))
    r = (dx1, dx2, dy1, dy2)

    x, y = np.arange(r[0], r[1]), np.arange(r[2], r[3])
    Y, X = np.meshgrid(y, x)

    def plot_data(ax):
        ax.imshow(
            get_state().image.im0[r[0]:r[1], r[2]:r[3]],
            vmin=get_state().i_image_min_cut, vmax=get_state().i_image_max_cut,
            cmap=get_root().frame_image._cbar.mappable.get_cmap().name,
            origin='lower')
        # extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")
        #G.ax31.format_coord=lambda x,y: "%.1f"%get_state().image.im0[r[2]+y,r[0]+x]
        ax.format_coord = lambda x, y: ""

    def plot_fit(ax):
        s_fit_type = get_state().s_fit_type
        fit_fct = BF.get_fit_function()
        ax.imshow(
            fit_fct((X, Y), get_state().d_fit_param),
            vmin=get_state().i_image_min_cut, vmax=get_state().i_image_max_cut,
            cmap=get_root().frame_image._cbar.mappable.get_cmap().name,
            origin='lower',
        )
        ax.format_coord = lambda x, y: ""

    # Get && Reset figure
    figure = get_root().frame_result.reset_figure()
    ax1 = figure.add_subplot(121)
    ax2 = figure.add_subplot(122)

    # Plot first image (data)
    plot_data(ax1)

    # Plot second image (fit)
    if get_state().s_fit_type != "None":
        plot_fit(ax2)
    else:
        plot_data(ax2)

    # APERTTURES
    params = get_state().d_fit_param
    log(9, 'Plot2D: background type', get_state().e_sky_type)

    # NOISE 8 RECT
    if get_state().e_sky_type == ESky.RECT8:
        rect = (x0 - params['r99x'], x0 + params['r99x'],
                y0 - params['r99y'], y0 + params['r99y'])
        var = IF.EightRectangleNoise(get_state().image.im0, rect, return_rectangle=1)[2]
        for p in var:
            center_tmp = (p[0][0]-r[0]-p[1]/2, p[0][1]-r[2]-p[2]/2)
            a = matplotlib.patches.Rectangle(
                (center_tmp[1], center_tmp[0]), p[2], p[1], facecolor='orange', edgecolor='black')
            ax2.add_patch(a)
        center = x0 - r[0], y0-r[2]

    # NOISE ANNULUS
    elif get_state().e_sky_type == ESky.ANNULUS:
        # INNER
        # TODO hardcode as in strehlimage.py
        tmpmin, tmpmax = 1.3, 1.6
        tmpstep = (tmpmax-tmpmin)/3
        lst = np.arange(tmpmin, tmpmax + tmpstep, tmpstep)
        for rt in lst:
            width = 2*params["r99v"]*rt  # invert
            height = 2*params["r99u"]*rt
            angle = params["theta"] * 180./np.pi
            x = params["center_y"] - r[2]
            y = params["center_x"] - r[0]
            a = matplotlib.patches.Ellipse(
                (x, y), width, height, angle, fc="none", ec="yellow", linestyle="solid", alpha=0.6)
            ax2.add_patch(a)

    # PHOT RECT
    if get_state().e_phot_type == EPhot.RECTANGLE:
        tx = params["center_x"] - r[0]
        ty = params["center_y"] - r[2]
        a = matplotlib.patches.Rectangle(
            (ty-params['r99y'], tx-params['r99x']), 2*params['r99y'], 2*params['r99x'], facecolor='none', edgecolor='black')
        ax2.add_patch(a)

    # PHOT ELL
    elif get_state().e_phot_type == EPhot.ELLIPTICAL:
        width = 2*params["r99v"]
        height = 2*params["r99u"]
        angle = params["theta"] * 180./np.pi
        x = params["center_y"] - r[2]
        y = params["center_x"] - r[0]
        a = matplotlib.patches.Ellipse(
            (x, y), width, height, angle, fc="none", ec="black")
        ax2.add_patch(a)

    #####
    # LABEL
    ax1.set_title("True Image")
    ax2.set_title("Fit")

    ax2.set_yticks((0, r[1]-r[0]))
    ax2.set_yticklabels((str(int(r[0])), str(int(r[1]))))
    ax2.set_xticks((0, r[3]-r[2]))
    ax2.set_xticklabels((str(int(r[2])), str(int(r[3]))))
    ax1.set_xticks(())
    ax1.set_yticks(())

    get_root().frame_result.redraw()
    return


def plot2d_binary():
    x0, y0 = get_state().d_fit_param["x0"], get_state().d_fit_param["y0"]
    x1, y1 = get_state().d_fit_param["x1"], get_state().d_fit_param["y1"]
    xr, yr = 3*abs(x0-x1), 3*abs(y0-y1)  # ditances
    side = max(xr, yr)  # side of the displayed square
    rx1, rx2 = int(min(x0, x1) - side / 2), int(max(x0, x1) + side / 2)
    ry1, ry2 = int(min(y0, y1) - side / 2), int(max(y0, y1) + side / 2)
    r = (rx1, rx2, ry1, ry2)

    # define coord for the fitted function display
    x, y = np.arange(r[0], r[1]), np.arange(r[2], r[3])
    Y, X = np.meshgrid(y, x)

    ###########
    # IMAGES draw
    # TRUE
    figure = get_root().frame_result.reset_figure()
    cmap = get_state().s_image_color_map

    ax1 = figure.add_subplot(121)
    ax1.imshow(
        get_state().image.im0[r[0]:r[1], r[2]:r[3]],
        vmin=get_state().i_image_min_cut, vmax=get_state().i_image_max_cut,
        cmap=cmap, origin='lower')

    # extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")
    ax1.format_coord = lambda x, y: "%.1f" % get_state().image.im0[y, x]
    ax1.format_coord = lambda x, y: ""
    # FIT
    if "Moffat" in get_state().s_fit_type:
        stg = "Moffat2pt"
    elif "Gaussian" in get_state().s_fit_type:
        stg = "Gaussian2pt"
    else:
        stg = "Moffat2pt"
        log(0, 'Warning, binary only has Gaussian and Moffat. Fallback to Moffat')

    fit_fct = lambda points, params: vars(BF)[stg](
        points, params, aniso=get_state().b_aniso, same_psf=get_state().b_same_psf)

    ax2 = figure.add_subplot(122)
    ax2.imshow(
        fit_fct((X, Y), get_state().d_fit_param),
        vmin=get_state().i_image_min_cut, vmax=get_state().i_image_max_cut,
        cmap=cmap, origin='lower',
        # extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")
        )  # need to comment the extent other wise too crowded and need to change rect positio
    #ax2.format_coord= lambda x,y:'%.1f'% vars(BF)[stg]((y,x),get_state().d_fit_param)
    ax2.format_coord = lambda x, y: ""
    get_root().frame_result.redraw()

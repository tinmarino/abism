"""
    To pretty print the answer, may go to FrameText
    C'est le bordel !
"""


import tkinter as tk
import numpy as np
import matplotlib

# Front
import abism.front.util_front as G

# Back
from abism.back import ImageFunction as IF
import abism.back.fit_template_function as BF

# Plugin
from abism.util import log, get_root, get_state, get_aa, EA, EPick


def tktext_insert_answer(self, answer, error=None, tags=None):
    """Insert an answer in a tktext"""
    # Clean in
    # # Convert answer
    if isinstance(answer, EA):
        answer = get_state().get_answer_obj(answer)
    # # Convert error
    if isinstance(error, EA):
        error = get_state().get_answer_obj(error)
    # # Convert unit && Convert tag
    if not isinstance(answer.unit, (list, tuple)):
        answer.unit = answer.unit, answer.unit
    if not tags: tags = []

    # Get name
    stg = answer.text + ":\t"

    # Get value and error
    if get_state().s_answer_unit == 'detector':
        stg += answer.str_detector()
        if error:
            stg += ' +/- ' + error.str_detector()
        stg += answer.unit[0]
    else:
        stg += answer.str_sky()
        if error:
            stg += ' +/- ' + error.str_sky()
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
        max_dist = max(get_state().d_fit_param["fwhm_x0"] + get_state().d_fit_param["fwhm_x1"],
                       get_state().d_fit_param["fwhm_y0"] + get_state().d_fit_param["fwhm_y1"])
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
        error = ans[1] if l > 1 else None
        tags = ans[2] if l > 2 else None
        self.insert_answer(answer, error=error, tags=tags)
tk.Text.insert_answer_list = tktext_insert_answer_list


def show_answer():  # CALLER
    """Draw && Print answer i.e. Image and Text"""
    plot_result()


def plot_result():
    """Discirminate according to pick"""
    pick = get_state().e_pick_type

    if pick == EPick.ONE:
        print_one(); return

    if pick in (EPick.BINARY, EPick.TIGHT):
        print_binary(); return

    if pick == EPick.ELLIPSE:
        print_ellipse(); return


def grid_button_change_coord():
    # Declare button info
    if get_state().s_answer_unit == "detector":
        s_button = u"\u21aa"+'To sky     '
        s_label = "In detector units"
    else:
        s_button = u"\u21aa"+'To detector'
        s_label = "In sky units"

    def callback():
        if get_state().s_answer_unit == 'detector':
            get_state().s_answer_unit = 'sky'
        else:
            get_state().s_answer_unit = 'detector'
        show_answer()

    button = tk.Button(
        get_root().frame_answer, text=s_button, command=callback)

    label = tk.Label(
        get_root().frame_answer, text=s_label, justify=tk.LEFT, anchor="nw")

    # Grid Buttons
    button.grid(column=1, sticky="wnse")
    label.grid(column=0, sticky="wnse")


def get_new_text_frame():
    # Pack fit type in Frame
    get_root().frame_answer.set_fit_type_text(get_state().s_fit_type)
    get_root().frame_answer.clear()

    # Button to change cord
    grid_button_change_coord()

    text = get_root().frame_answer.grid_text_answer()

    return text


def print_one():
    # Grid tk text
    text = get_new_text_frame()

    # Declare return list
    lst = [
        [EA.STREHL, EA.ERR_STREHL, ['tag-important']],
        [EA.STREHL_EQ, EA.ERR_STREHL_EQ],
        [EA.CENTER],
        [EA.FWHM_ABE],
        [EA.PHOTOMETRY],
        [EA.BACKGROUND, EA.NOISE],
        [EA.SN],
        [EA.INTENSITY],
    ]
    # Insert element in text
    text.insert_answer_list(lst)

    # Insert Warnings
    text.insert_warnings()

    # Disable edit
    text.configure(state=tk.DISABLED)


def print_ellipse():
    # Grid tk text
    text = get_new_text_frame()

    # Declare return list
    lst = [
        # TODO error
        [EA.STREHL, None, ['tag-important']],
        [EA.CENTER],
        [EA.PHOTOMETRY],
        # TODO error rms (easy win), callled noise
        [EA.BACKGROUND],
        [EA.INTENSITY],
    ]

    # Insert element in text
    text.insert_answer_list(lst)

    # Warnings TODO W.Sthrel dependant
    # text.insert_warnings()

    # Disable edit
    text.configure(state=tk.DISABLED)


def print_binary():
    # Grid tk text
    text = get_new_text_frame()

    # Declare return list
    lst = [
        [EA.STREHL1, None, ['tag-important']],
        [EA.STREHL2, None, ['tag-important']],
        [EA.BINARY],
        [EA.STAR1],
        [EA.STAR2],
        [EA.SEPARATION, EA.ERR_SEPARATION],
        [EA.PHOTOMETRY1],
        [EA.PHOTOMETRY2],
        [EA.FLUX_RATIO],
        [EA.ORIENTATION],
    ]

    # Insert elements in text
    text.insert_answer_list(lst)

    # Insert Warnings
    text.insert_warnings()

    # Disable edit
    text.configure(state=tk.DISABLED)



###############
#   1D 1D 1D
###############





def PlotStar():
    """Discriminate 1 or 2 object"""
    if get_state().e_pick_type in (EPick.BINARY, EPick.TIGHT):
        PlotBinaryStar1D()
    else:
        PlotOneStar1D()
        PlotStar2()


def PlotOneStar1D():
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
    x, y = IF.XProfile(get_state().image.im0, center)
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
    ax.axhline(y=get_state().get_answer(EA.BACKGROUND), color='black', linestyle='-.')

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
                   'phot': get_aa(EA.PHOTOMETRY),
                   'obstruction': get_root().header.obstruction/100,
                   }
        bessel = BF.DiffractionPatern((a, params['center_y']), params2)
        ax.plot(a, bessel+params['my_background'],
                color='blue', linewidth=2, label='Ideal PSF')

    # Draw Legend
    ax.legend(loc=1, prop={'size': 8})

    #  def Percentage(y):  # y is the intensity
    #      res = 100*(max(MyBessel)-get_state().get_answer(EA.BACKGROUND))*y
    ax.set_xlim(center[0]-r99-5, center[0] + r99 + 5)

    # Update skin && Draw
    get_root().frame_fit.get_canvas().draw()


def PlotBinaryStar1D():
    """Draw 1D of binary system"""
    x0, y0 = get_state().d_fit_param["x0"], get_state().d_fit_param["y0"]
    x1, y1 = get_state().d_fit_param["x1"], get_state().d_fit_param["y1"]
    fwhm0, fwhm1 = get_state().d_fit_param["fwhm_x0"], get_state().d_fit_param["fwhm_x1"]

    #######
    # EXTREMITIES OF PROFILE LINE ...
    # following the line x0,x1
    # Do not by pass the image borders
    line_len = np.sqrt((x1-x0)**2 + (y1-y0)**2)
    dx0 = (x0-x1) / line_len * 5 * fwhm0
    dy0 = (y0-y1) / line_len * 5 * fwhm0
    dx1 = (x1-x0) / line_len * 5 * fwhm1
    dy1 = (y1-y0) / line_len * 5 * fwhm1

    extremity0 = IF.DoNotPassBorder(get_state().image.im0, (int(x0+dx0), int(y0+dy0)))
    extremity1 = IF.DoNotPassBorder(get_state().image.im0, (int(x1+dx1), int(y1+dy1)))

    ab, od, points = IF.RadialLine(
        get_state().image.im0, (extremity0, extremity1), return_point=1)

    if "Moffat" in get_state().s_fit_type:
        s_fit_type = "Moffat2pt"
    else:
        s_fit_type = "Gaussian2pt"
    ab_range = ab[0], ab[-1]
    x_range = points[0][1], points[0][-1]
    y_range = points[1][1], points[1][-1]

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
    ax.plot(ab_th+0.5, I_theory, color='purple',
            linewidth=2, label='Fitted PSF')
    #G.ax2.plot(ab_th,I_theory,color='purple',linewidth=2,label='Fitted PSF')
    ax.plot(ab, od, color='black', linestyle='steps', linewidth=1,
            label='Real Profile')  # x+0.5 to recenter the bar
    ax.legend(loc=1, prop={'size': 8})      # Legend
    get_root().frame_fit.redraw()



####################
#   2D 2D 2D
####################


def PlotStar2():
    """the two images colormesh"""
    if get_state().e_pick_type == EPick.ONE:
        PlotOneStar2D()
    if get_state().e_pick_type in (EPick.BINARY, EPick.TIGHT):
        PlotBinaryStar2D()


def PlotOneStar2D():
    x0, y0 = get_state().d_fit_param["center_x"], get_state().d_fit_param["center_y"]
    r99x, r99y = get_state().d_fit_param["r99x"], get_state().d_fit_param["r99y"]
    dx1, dx2 = int(max(x0-4*r99x, 0)), int(min(x0+4*r99x,
                                               len(get_state().image.im0) + 1))  # d like display
    dy1, dy2 = int(max(y0-4*r99y, 0)), int(min(y0+4*r99y,
                                               len(get_state().image.im0) + 1))  # c like cut If borders
    r = (dx1, dx2, dy1, dy2)  # Teh local cut applied to the image. To show it

    x, y = np.arange(r[0], r[1]), np.arange(r[2], r[3])
    Y, X = np.meshgrid(y, x)

    def plot_data(ax):
        ax.imshow(
            get_state().image.im0[r[0]:r[1], r[2]:r[3]],
            vmin=get_state().i_image_min_cut, vmax=get_state().i_image_max_cut,
            cmap=G.cbar.mappable.get_cmap().name, origin='lower')
        # extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")
        #G.ax31.format_coord=lambda x,y: "%.1f"%get_state().image.im0[r[2]+y,r[0]+x]
        ax.format_coord = lambda x, y: ""

    def plot_fit(ax):
        s_fit_type = get_state().s_fit_type
        fit_fct = BF.get_fit_function()
        if "Gaussian_hole" in s_fit_type:
            s_fit_type = "Gaussian_hole"
        ax.imshow(
            fit_fct((X, Y), get_state().d_fit_param),
            vmin=get_state().i_image_min_cut, vmax=get_state().i_image_max_cut,
            cmap=G.cbar.mappable.get_cmap().name, origin='lower',
                                          # extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")
                                          )  # need to comment the extent other wise too crowded and need to change rect position
        #G.ax32.format_coord= lambda x,y:'%.1f'% vars(BF)[s_fit_type]((r[2]+y,r[0]+x),get_state().d_fit_param)
        ax.format_coord = lambda x, y: ""

    # Get && Reset figure
    figure = get_root().frame_result.get_figure()
    figure.clf()
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
    #   s   (te center of the rect is in fact the bottm left corner)

    # NOISE 8 RECT
    if (get_state().s_noise_type == "8rects"):
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
    elif (get_state().s_noise_type == "elliptical_annulus"):
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
    if get_state().s_phot_type == "encircled_energy":
        tx = params["center_x"] - r[0]
        ty = params["center_y"] - r[2]
        a = matplotlib.patches.Rectangle(
            (ty-params['r99y'], tx-params['r99x']), 2*params['r99y'], 2*params['r99x'], facecolor='none', edgecolor='black')
        ax2.add_patch(a)

    # PHOT ELL
    elif get_state().s_phot_type == "elliptical_aperture":
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


def PlotBinaryStar2D():

    x0, y0 = get_state().d_fit_param["x0"], get_state().d_fit_param["y0"]
    x1, y1 = get_state().d_fit_param["x1"], get_state().d_fit_param["y1"]
    xr, yr = 3*abs(x0-x1), 3*abs(y0-y1)  # ditances
    side = max(xr, yr)  # side of the displayed square
    rx1, rx2 = int(min(x0, x1) - side / 2),  int(max(x0, x1) + side / 2)
    ry1, ry2 = int(min(y0, y1) - side / 2),  int(max(y0, y1) + side / 2)
    r = (rx1, rx2, ry1, ry2)

    # define coord for the fitted function display
    x, y = np.arange(r[0], r[1]), np.arange(r[2], r[3])
    Y, X = np.meshgrid(y, x)

    ###########
    # IMAGES draw
    # TRUE
    get_root().frame_result.get_figure().clf()
    cmap = get_state().s_image_color_map


    ax1 = get_root().frame_result.get_figure().add_subplot(121)
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

    fit_fct = lambda points, params: vars(BF)[stg](
        points, params, aniso=get_state().b_aniso, same_psf=get_state().b_same_psf)

    ax2 = get_root().frame_result.get_figure().add_subplot(122)
    ax2.imshow(
        fit_fct((X, Y), get_state().d_fit_param),
        vmin=get_state().i_image_min_cut, vmax=get_state().i_image_max_cut,
        cmap=cmap, origin='lower',
        # extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")
        )  # need to comment the extent other wise too crowded and need to change rect positio
    #ax2.format_coord= lambda x,y:'%.1f'% vars(BF)[stg]((y,x),get_state().d_fit_param)
    ax2.format_coord = lambda x, y: ""
    get_root().frame_result.redraw()
    return

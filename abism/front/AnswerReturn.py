"""
    To pretty print the answer, may go to FrameText
    C'est le bordel !
"""

from threading import Thread, currentThread
from abc import ABC, abstractmethod

from tkinter import *
from tkinter import font as tkFont
import numpy as np
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas

# Front
from abism.front.util_front import skin
import abism.front.util_front as G

# Back
from abism.back import ImageFunction as IF
import abism.back.fit_template_function as BF
from abism.back.image import get_array_stat
import abism.back.util_back as W

# Plugin
from abism.plugin import ReadHeader as RH  # to know witch telescope

from abism.util import log, get_root, get_state, abism_val, EA

# new
from abism.back.Strehl import get_equivalent_strehl_ratio

class AnswerLine(ABC):
    """A line to append to a text widget"""
    def __init__(self):
        pass

    @abstractmethod
    def insert_in_tk_text(self, text):
        pass

class AnswerImageSky(AnswerLine):
    """A Line in the answer"""
    def __init__(self, s_variable, o_value, s_image, s_sky, tags=[]):
        """label, variable,
        value as string on image,
        value as string in sky referencial <- '' returns s_image
        """
        self.s_variable = s_variable
        self.o_value = o_value
        self.s_image = s_image
        self.s_sky = s_sky
        self.tags = tags

    def insert_in_tk_text(self, text):
        """Should be the other way.
                    But many things should be the other way
                    !!! It is a wild world !!!
        Hopefully you created a tag-left and tag-right
        And you readed me .....
        """
        text.insert(END, self.s_variable + "\t", self.tags)
        if get_state().s_answer_unit == 'detector' or not self.s_sky:
            text.insert(END, self.s_image, self.tags)
        else:
            text.insert(END, self.s_sky, self.tags)
        text.insert(END, "\n")


def tkable_from_answer(answer, error=None, unit='', tags=[]):
    # Str answser
    s_sky = answer.str_sky()
    s_detector = answer.str_detector()

    # Str error
    if error is not None:
        s_sky += ' +/- ' + error.str_sky()
        s_detector += ' +/- ' + error.str_detector()

    # Unit tupling
    if not isinstance(unit, (tuple, list)): unit = [unit, unit]
    s_detector += unit[0]
    s_sky += unit[1]

    # Return crafted object
    return AnswerImageSky(
        answer.text.value[0],
        answer.value,
        s_detector,
        s_sky,
        tags=tags
        )


class AnswerText(AnswerLine):
    def __init__(self, obj, tags=[]):
        self.s_text = str(obj) + "\n"
        self.tags = tags

    def insert_in_tk_text(self, text):
        text.insert(END, self.s_text, self.tags)


def MyFormat(value, number, letter):
    """This is just to put a "," between the 1,000 for more readability
    MyFormat(var, 1, 'f') -> "%.1f" % var
    TODO remove one day
    """
    try:
        float(value)  # in case
    except:
        return value
    stg = "{:,"
    stg += "." + str(number) + letter + "}"
    return stg.format(value).replace(",", " ")


def Separation(point=((0, 0), (0, 0)), err=((0, 0), (0, 0))):
    """point1i  (and 2) : list of 2 float = (x,y)= row, column
    err_point1 = 2 float = x,y )
    read north position in W
    """
    point1, point2 = point[0], point[1]
    err_point1, err_point2 = err[0], err[1]
    x0, x1, y0, y1 = point1[0],  point1[1], point2[0],  point2[1]
    dx0, dx1, dy0, dy1 = err_point1[0],  err_point1[1], err_point2[0],  err_point2[1]

    ##########
    # SEPARATION DISTANCE
    dist = np.sqrt((y1-y0)**2 + (x1-x0)**2)

    # ERR
    dist_err = np.sqrt(dx0**2 + dx1**2)
    dx0 = np.sqrt(err_point1[0]**2 + err_point1[1]**2)
    dx1 = np.sqrt(err_point2[0]**2 + err_point2[1]**2)

    #############
    # SEPARATION ANGLE
    angle = np.array([(y1-y0),   (x1-x0)])
    angle /= np.sqrt((y0-y1)**2 + (x0-x1)**2)

    im_angle = np.arccos(angle[1]) * 57.295779  # 360/2pi
    sign = np.sign(angle[0])
    im_angle = im_angle + (sign-1)*(-90)

    sky_angle = np.arccos(
        angle[1]*W.north_direction[1] + angle[0] *
        W.north_direction[0]) * 57.295779  # inverted angle and not north
    sign = np.sign(angle[0]*W.east_direction[0] + angle[1]*W.east_direction[1])
    sky_angle = sky_angle + (sign-1)*(-90)

    res = {"im_angle": im_angle,
           "sky_angle": sky_angle,
           "dist": dist, "dist_err": dist_err,
           }
    return res

    ##################
    #  LABELS  LABELS
    ##################


def show_answer():  # CALLER
    """Draw && Print answer i.e. Image and Text"""


    plot_result()


def plot_result():
    """Discirminate according to pick"""
    pick = get_state().pick_type

    if pick == 'one':
        print_one(); return

    if pick in ('binary', 'tightbinary'):
        PlotBinary(); return

    if pick == 'ellipse':
        PlotEllipse(); return

    if pick == "stat":
        PlotStat(); return



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

    button = Button(
        get_root().frame_answser, background='Khaki', borderwidth=1,
        text=s_button, **skin().button_dic,
        command=callback)

    label = Label(
        get_root().frame_answser,
        justify=LEFT, anchor="nw", **skin().fg_and_bg,
        text=s_label)

    # Grid Buttons
    button.grid(column=1, sticky="wnse")
    label.grid(column=0, sticky="wnse")




def answer_strehl():
    return tkable_from_answer(
        get_state().answers[EA.STREHL],
        error=get_state().answers[EA.ERR_STREHL],
        tags=['tag-important'],
        unit=' %')


def answer_strehl_equivalent():
    return tkable_from_answer(
        get_state().answers[EA.STREHL_EQ],
        error=get_state().answers[EA.ERR_STREHL_EQ],
        unit=' %')


def answer_photometry():
    return tkable_from_answer(
        get_state().answers[EA.PHOTOMETRY],
        #error=get_state().answers[EA.ERR_STREHL_EQ],
        unit=(' [adu]', ' [mag]'))


def answer_fwhm():
    return tkable_from_answer(
        get_state().answers[EA.FWHM_ABE],
        unit=(' [pxl]', ' [mas]'))


def answer_background():
    return tkable_from_answer(
        get_state().answers[EA.BACKGROUND],
        error=get_state().answers[EA.NOISE],
        unit=(' [adu]', ' [mag]'))


def answer_signal_on_noise():
    return tkable_from_answer(
        get_state().answers[EA.SN])


def answer_intensity():
    return tkable_from_answer(
        get_state().answers[EA.INTENSITY],
        unit=(' [adu]', ' [mag]'))


def print_one():
    # Pack fit type in Frame
    get_root().frame_answser.set_fit_type_text(get_state().fit_type)
    get_root().frame_answser.clear()

    # Button to change cord
    grid_button_change_coord()

    # <- Calculate Equivalent strehl2.2 and error
    strehl = get_state().answers[EA.STREHL].value / 100
    wavelength = get_root().header.wavelength

    # Get equivalent Strehl ratio
    strehl_eq = get_equivalent_strehl_ratio(strehl, wavelength)

    # Save it
    get_state().add_answer(EA.STREHL_EQ, strehl_eq)

    # Get Error on equivalent strehl
    strehl_eq_err = get_state().answers[EA.ERR_STREHL].value
    strehl_eq_err *= strehl_eq / (strehl * 100)

    # Save it
    get_state().add_answer(EA.ERR_STREHL_EQ, strehl_eq_err)


    # TODO move all preceding in back

    # answers = get_state().reset_answers()
    W.tmp.lst = []

    # Strehl
    W.tmp.lst.append(answer_strehl())

    # Equivalent Strehl Ratio
    W.tmp.lst.append(answer_strehl_equivalent())

    # # Center (need to inverse)
    # line = AnswerImageSky(
    #     "Center x,y: ",
    #     (W.strehl["center_y"], W.strehl["center_x"]),
    #     MyFormat(W.strehl["center_y"], 3, "f") + " , " + MyFormat(W.strehl['center_x'], 3, "f"),
    #     "%s , %s" % (format_sky(W.strehl['center_ra'], W.strehl['center_dec']))
    #     )
    # W.tmp.lst.append(line)

    # FWHM
    W.tmp.lst.append(answer_fwhm())

    # Photometry
    W.tmp.lst.append(answer_photometry())

    # Background
    W.tmp.lst.append(answer_background())

    # Signal / Noise ratio
    W.tmp.lst.append(answer_signal_on_noise())

    # Peak of detection
    W.tmp.lst.append(answer_intensity())

    # Saturated
    if 'intensity' not in W.strehl:  # binary
        intensity = W.strehl["intensity0"] + W.strehl["intensity1"]
    else:
        intensity = W.strehl["intensity"]

    if intensity > get_root().header.non_linearity_level:
        if intensity > 1.0 * get_root().header.saturation_level:
            text = "!!! SATURATED !!!  Strehl is UNRELIABLE"
        else:
            text = "!!! NON-LINEAR Strehl may be  unreliable"
        line = AnswerText(text, tags=['tag-important', 'tag-center'])
        W.tmp.lst.append(line)

    # Undersampled
    is_undersampled = "sinf_pixel_scale" in vars(get_root().header)
    is_undersampled = is_undersampled and get_root().header.sinf_pixel_scale <= 0.01
    if is_undersampled:
        text = "!!! UNDER-SAMPLED !!! Use FWHM\n (SR under-estimated)"
        line = AnswerText(text, tags=['tag-important', 'tag-center'])
        W.tmp.lst.append(line)

    # Binary too far
    if get_state().pick_type == "binary":
        max_dist = max(W.strehl["fwhm_x0"] + W.strehl["fwhm_x1"],
                       W.strehl["fwhm_y0"] + W.strehl["fwhm_y1"])
        sep = (W.strehl["x0"] - W.strehl["x1"])**2
        sep += (W.strehl["y0"] - W.strehl["y1"])**2
        sep = np.sqrt(sep)

        if max_dist*15 < sep:  # means too high separation
            text = "Wide Binary\npick objects individually"
            line = AnswerText(text, tags=['tag-important', 'tag-center'])
            W.tmp.lst.append(line)

        if max_dist*3 > sep:  # means too high separation
            text = "Tight Binary\nmay be unreliable"
            line = AnswerText(text, tags=['tag-important', 'tag-center'])
            W.tmp.lst.append(line)

    refresh_text_answer()



def grid_tuple_obsolete(i):
    log(0, "WARNING for dev, this is obsolete fct, use the AnswerLine class\n\n\n")
    myargs = skin().fg_and_bg.copy()
    myargs.update({"font": font, "justify": LEFT, "anchor": "nw"})
    if i[0] == "Strehl: ":
        myargs["fg"] = "red"
        myargs["font"] = skin().font.strehl
    l1 = Label(get_root().frame_answser, text=i[0], **myargs)
    l2 = Label(get_root().frame_answser, text=i[2], **myargs)
    l1.grid(column=0, sticky="nsew")
    l2.grid(column=1, sticky="nsew")


def on_resize_text(event):
    log(5, 'Answer, Resize text:', event)
    event.widget.configure(tabs=(event.width/2, LEFT))


def refresh_text_answer():
    """Grid formatted text answered
    Nobody can edit text, when it is disabled
    """
    # Create text
    text = Text(get_root().frame_answser, **skin().text_dic)


    # Configure Text
    text.bind("<Configure>", on_resize_text)
    text.tag_configure('tag-important', foreground=skin().color.important)
    text.tag_configure('tag-center', justify=CENTER)

    # Fill text
    for obj in W.tmp.lst:
        if isinstance(obj, (tuple, list)):
            grid_tuple_obsolete(obj)
        else:
            obj.insert_in_tk_text(text)

    # Disable edit
    text.configure(state=DISABLED)

    # Grid text
    text.grid(columnspan=2, sticky='nsew')



def PlotEllipse():
    """TODO clean + not working anymore due to W.tmp.lst"""
    rms = get_root().header.wavelength / 2/np.pi * \
        np.sqrt(-np.log(get_state().answers[EA.STREHL].value/100))
    W.strehl["strehl2_2"] = 100 * np.exp(-(rms*2*np.pi/2.17)**2)
    # <- CAlculate Equivalent strehl2.2

    ########
    # BUTTON
    # to fill th ecolumn on th epossible space
    get_root().frame_answser.columnconfigure(0, weight=1)
    G.bu_answer_type = Button(
        get_root().frame_answser, text='useless', background='Khaki', borderwidth=1, width=9)
    G.lb_answer_type = Label(
        get_root().frame_answser, text="useless", justify=LEFT, anchor="nw", **skin().fg_and_bg)

    ############
    # IMAGE COORD
    if get_state().s_answer_unit == "detector":
        G.bu_answer_type["text"] = u"\u21aa"+'To sky     '
        G.bu_answer_type["command"] = lambda: PlotAnswer(unit="sky")
        G.lb_answer_type["text"] = "In detector units"

        W.tmp.lst = [
            ["Strehl: ", get_state().answers[EA.STREHL].value, MyFormat(
                get_state().answers[EA.STREHL].value, 1, "f") + " +/- " + MyFormat(get_state().answers[EA.ERR_STREHL].value, 1, "f") + " %"],
            ["Intensity: ", W.strehl["intensity"], MyFormat(
                W.strehl["intensity"], 1, "f") + " [adu]"],
            ["Background: ", get_state().get_answer(EA.BACKGROUND), MyFormat(
                get_state().get_answer(EA.BACKGROUND), 1, "f") + ' +/- ' + MyFormat(W.strehl['rms'], 1, "f") + "[adu]"],
            ["Photometry: ", W.strehl["my_photometry"], MyFormat(
                W.strehl["my_photometry"], 1, "f") + " [adu]"],
            #["S/N: "           , W.strehl["snr"]    ,MyFormat(W.strehl["snr"],1,"f") ],
            ["Eq. SR(2.17"+u"\u03bc" + "m): ", W.strehl["strehl2_2"],
                MyFormat(W.strehl["strehl2_2"], 1, "f") + " %"],
            ["Center x,y: ", (W.strehl["center_y"], W.strehl["center_x"]), MyFormat(
                W.strehl["center_y"], 3, "f") + " , " + MyFormat(W.strehl['center_x'], 3, "f")],  # need to inverse
        ]

    ##################
    # SKY COORD
    # including unit = sky :    not =  detector  get_state().s_answer_unit=="sky":
    else:
        G.bu_answer_type["text"] = u"\u21aa"+'To detector'
        G.bu_answer_type["command"] = lambda: PlotAnswer(unit="detector")
        G.lb_answer_type["text"] = "In sky units"

        ###
        # WCS
        try:
            # if len( W.hdulist[0].data.shape ) == 3: # if cube,  just cut the WCS object, see antoine
            #   my_wcs = ProjectWcs(get_root().header.wcs).all_pix2world( np.array([[ W.strehl["center_y"],W.strehl["center_x"] ]]), 0 )
            # else : # not cube
            my_wcs = get_root().header.wcs.all_pix2world(
                np.array([[W.strehl["center_y"], W.strehl["center_x"]]]), 0)
        except:
            import traceback
            traceback.print_exc()
            print("WARNING I did not manage to get WCS")
            my_wcs = np.array([[99, 99], [99, 99]])
        W.strehl["center_ra"], W.strehl["center_dec"] = my_wcs[0, 0], my_wcs[0, 1]

        W.tmp.lst = [
            ["Strehl: ", get_state().answers[EA.STREHL].value, "%.1f" %
                (get_state().answers[EA.STREHL].value) + " +/- "+"%.1f" % get_state().answers[EA.ERR_STREHL].value+" %"],
            ["Intensity: ", W.strehl["intensity"],  "%.1f" % (
                get_root().header.zpt-2.5*np.log10(W.strehl["intensity"]/get_root().header.exptime)) + " [mag]"],
            ["Background: ", get_state().get_answer(EA.BACKGROUND), "%.2f" % (get_root().header.zpt-2.5*np.log10(
                get_state().get_answer(EA.BACKGROUND)/get_root().header.exptime)) + '| rms: ' + "%.2f" % (get_root().header.zpt-2.5*np.log10(W.strehl['rms'])) + " [mag]"],
            ["Photometry: ", W.strehl["my_photometry"], "%.2f" % (
                get_root().header.zpt-2.5*np.log10(W.strehl["my_photometry"]/get_root().header.exptime)) + " [mag]"],
            #["S/N: "           , W.strehl["snr"]    ,MyFormat(W.strehl["snr"],1,"f")  ],
            ["Eq. SR 2.17"+u"\u03bc" + "m: ", W.strehl["strehl2_2"], "%.1f" %
                W.strehl["strehl2_2"] + "%"],
            ["Center RA,Dec: ", (W.strehl["center_ra"], W.strehl["center_dec"]),
             "%.8f" % W.strehl["center_ra"]+","+"%.8f" % W.strehl['center_dec']],
        ]  # label , variable, value as string


def PlotBinary():
    x0, x1, y0, y1 = W.strehl["x0"], W.strehl["x1"], W.strehl["y0"], W.strehl["y1"]
    dx0, dx1 = W.psf_fit[1]["x0"], W.psf_fit[1]["x1"]
    dy0, dy1 = W.psf_fit[1]["y0"], W.psf_fit[1]["y1"]

    tmp = Separation(point=((x0, x1), (y0, y1)), err=((dx0, dx1), (dy0, dy1)))
    separation = tmp["dist"]
    sep_err = tmp["dist_err"]
    im_angle = tmp["im_angle"]
    sky_angle = tmp["sky_angle"]

    # "
    # STREHL
    W.phot0, W.phot1 = W.strehl["my_photometry0"], W.strehl["my_photometry1"]
    bessel_integer = get_root().header.wavelength * \
        10**(-6.) / np.pi / (get_root().header.pixel_scale/206265) / get_root().header.diameter
    bessel_integer = bessel_integer**2 * 4 * \
        np.pi / (1-(get_root().header.obstruction/100)**2)
    Ith0, Ith1 = W.phot0/bessel_integer, W.phot1/bessel_integer
    W.strehl0 = W.strehl["intensity0"] / Ith0 * 100
    W.strehl1 = W.strehl["intensity1"] / Ith1 * 100

    ##############
    # IMAGE COORD
    if get_state().s_answer_unit == "detector":
        G.bu_answer_type["text"] = u"\u21aa"+'To sky     '
        G.bu_answer_type["command"] = lambda: PlotAnswer(unit="sky")
        G.lb_answer_type["text"] = "In detector units"

        W.tmp.lst = [["Binary: ", get_state().fit_type, get_state().fit_type],
                     ["1 Star: ", (y0, x0),  "%.1f , %.1f" % (y0, x0)],
                     ["2 Star: ", (y1, x1),  "%.1f , %.1f" % (y1, x1)],
                     ["Separation: ", separation, "%.2f" %
                         separation + "+/-" + "%.2f" % sep_err + " [pxl]"],
                     ["Phot1: ", W.phot0, "%.1f" % W.phot0 + " [adu]"],
                     ["Phot2: ", W.phot1, "%.1f" % W.phot1 + " [adu]"],
                     ["Flux ratio: ", (W.phot0/W.phot1), "%.1f" %
                      (W.phot0/W.phot1)],
                     ["Orientation: ", im_angle, "%.2f" % im_angle + u'\xb0'],
                     ["Strehl1: ", W.strehl0, "%.1f" % W.strehl0+" %"],
                     ["Strehl2: ", W.strehl1, "%.1f" % W.strehl1+" %"],
                     ]

    ##############
    # SKY COORD
    else:  # Including coor_type from sky = sky
        # "
        # WCS
        my_wcs = get_root().header.wcs.all_pix2world(np.array(
            [[W.strehl["y0"], W.strehl["x0"]],  [W.strehl["y1"], W.strehl["x1"]]]), 0)
        my_wcs = np.array(my_wcs)
        ra, dec = my_wcs[:, 0], my_wcs[:, 1]
        pxll = get_root().header.pixel_scale
        if isinstance(get_root().header, RH.SinfoniHeader):
            pxll = get_root().header.sinf_pixel_scale

        ##########
        W.tmp.lst = [["Binary: ", get_state().fit_type, get_state().fit_type],
                     #["1 Star: ", (ra[0], dec[0]), "%s , %s" %
                     # format_sky(ra[0], dec[0])],
                     # ["2 Star: ", (ra[1], dec[1]), "%s , %s" %
                     #  format_sky(ra[1], dec[1])],
                     ["Separation: ", separation, "%.1f" % (
                         separation*get_root().header.pxll*1000) + "+/-" + "%.1f" % (sep_err*pxll*1000) + " [mas]"],
                     ["Phot1: ", W.phot0, "%.1f" % (
                         get_root().header.zpt - 2.5 * np.log10(W.phot0/get_root().header.exptime)) + " [mag]"],
                     ["Phot2: ", W.phot1, "%.1f" %
                      (get_root().header.zpt - 2.5 * np.log10(W.phot1/get_root().header.exptime)) + " [mag]"],
                     ["Flux ratio: ", (W.phot0/W.phot1), "%.1f" %
                      (W.phot0/W.phot1)],
                     ["Orientation: ", sky_angle, "%.2f" % sky_angle + u'\xb0'],
                     ["Strehl1: ", W.strehl0, "%.1f" % W.strehl0+" %"],
                     ["Strehl2: ", W.strehl1, "%.1f" % W.strehl1+" %"],
                     ]


# "
#   1D 1D 1D
###############


def PlotStat():
    W.r = IF.Order4(W.r)
    sub_array = get_root().image.im0[W.r[0]:W.r[1], W.r[2]:W.r[3]]
    dicr = get_array_stat(sub_array)
    myargs = skin().fg_and_bg.copy()
    myargs.update({"font": skin().font.answer, "justify": LEFT, "anchor": "nw"})
    row = 0
    lst = [
        ["DIM X*DIM Y: ", "%.1f x %.1f" %
            (abs(W.r[0]-W.r[1]), abs(W.r[2]-W.r[3]))],
        ["MIN: ", "%.1f" % dicr["min"]],
        ["MAX: ", "%.1f" % dicr["max"]],
        ["SUM: ", "%.1f" % dicr["sum"]],
        ["MEAN: ", "%.1f" % dicr["mean"]],
        ["MEDIAN: ", "%.1f" % dicr["median"]],
        ["RMS: ", "%.1f" % dicr["rms"]],
    ]

    ax = get_root().frame_result.reset_figure_ax()
    num = 0
    for i in lst:
        print(i[0] + i[1])
        ax.text(0.3, 1.0-float(num)/(len(lst)+1),
                i[0]+i[1], transform=G.ax3.transAxes)
        #G.ax3.text(0.5,0.5, i[0]+i[1],transform = G.ax3.transAxes )
        num += 1

    ax = get_root().frame_result.redraw()




def PlotStar():
    # Binary plot profile
    if (get_state().pick_type == "binary") or (get_state().pick_type == "tightbinary"):
        PlotBinaryStar1D()
    else:  # including only one star  (ie : not binary)
        PlotOneStar1D()
        PlotStar2()


def PlotOneStar1D():
    center = (W.strehl['center_x'], W.strehl['center_y'])
    #################
    # PLOT radius profile
    params = W.strehl
    log(3, 'center=', center)

    # Get ax
    ax = get_root().frame_fit.reset_figure_ax(
        xlabel='Pixel', ylabel='Intensity')

    # Plot x, y
    # we need to give the center (of course)
    x, y = IF.XProfile(get_root().image.im0, center)
    # we get a smaller bin for the fitted curve.
    a = np.arange(min(x), max(x), 0.1)
    # RAW  DATA in X
    # x+0.5 to recenter the bar
    ax.plot(x+0.5, y, color='black', drawstyle='steps', linestyle='--',
            linewidth=1, label='Data')

    # Plot encircle line
    r99 = (W.strehl['r99x']+W.strehl['r99y'])/2
    x0cut, x1cut = center[0]-r99, center[0]+r99
    ax.axvline(x=x0cut, color='black', linestyle='-.', label='99% EE')
    ax.axvline(x=x1cut, color='black', linestyle='-.')
    ax.axhline(y=get_state().get_answer(EA.BACKGROUND), color='black', linestyle='-.')

    # Plot Fit
    if not get_state().fit_type == 'None':
        I_theory = vars(BF)[get_state().fit_type]((a, params['center_y']), params)
        ax.plot(a, I_theory, color='purple', linewidth=2, label='Fit')

    # Plot perfect diffraction pattern
    if not get_root().header.wavelength*1e-6/get_root().header.diameter/(get_root().header.pixel_scale/206265) < 2:
        params2 = {'diameter': get_root().header.diameter,
                   'lambda': get_root().header.wavelength,
                   'center_x': params['center_x'],
                   'center_y': params['center_y'],
                   'pixelscale': get_root().header.pixel_scale,
                   'phot': abism_val(EA.PHOTOMETRY),
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
    get_root().frame_fit.update_skin()
    get_root().frame_fit.get_canvas().draw()


def PlotBinaryStar1D():
    """Draw 1D of binary system"""
    x0, y0 = W.strehl["x0"], W.strehl["y0"]
    x1, y1 = W.strehl["x1"], W.strehl["y1"]
    fwhm0, fwhm1 = W.strehl["fwhm_x0"], W.strehl["fwhm_x1"]

    #######
    # EXTREMITIES OF PROFILE LINE ...
    # following the line x0,x1
    # Do not by pass the image borders
    line_len = np.sqrt((x1-x0)**2 + (y1-y0)**2)
    dx0 = (x0-x1) / line_len * 5 * fwhm0
    dy0 = (y0-y1) / line_len * 5 * fwhm0
    dx1 = (x1-x0) / line_len * 5 * fwhm1
    dy1 = (y1-y0) / line_len * 5 * fwhm1

    extremity0 = IF.DoNotPassBorder(get_root().image.im0, (int(x0+dx0), int(y0+dy0)))
    extremity1 = IF.DoNotPassBorder(get_root().image.im0, (int(x1+dx1), int(y1+dy1)))

    ab, od, points = IF.RadialLine(
        get_root().image.im0, (extremity0, extremity1), return_point=1)

    if "Moffat" in get_state().fit_type:
        fit_type = "Moffat2pt"
    else:
        fit_type = "Gaussian2pt"
    ab_range = ab[0], ab[-1]
    x_range = points[0][1], points[0][-1]
    y_range = points[1][1], points[1][-1]

    ab_th = np.arange(ab_range[0], ab_range[1], 0.1)
    x_theory = np.interp(ab_th, ab_range, x_range)
    y_theory = np.interp(ab_th, ab_range, y_range)
    if get_state().fit_type is not None:
        I_theory = vars(BF)[fit_type](
            (x_theory, y_theory), W.strehl["fit_dic"])
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



def ProfileAnswer():  # 1 and 2D
    def Curve():
        global points  # for the stat

        ax = get_root().frame_fit.reset_figure_ax()

        # DATA
        ab, od, points = IF.RadialLine(
            get_root().image.im0, (G.my_point1, G.my_point2), return_point=1)
        ax.plot(ab, od, '-', linewidth=1, label="Data")

        # FIT
        # if ( get_state().fit_type != "None" ) & ( "strehl" in vars(W) ):
        #  I_theory = vars(BF) [get_state().fit_type ](points,W.strehl["fit_dic"],get_state().fit_type)
        #  G.ax2.plot(ab,I_theory,color='purple',linewidth=2,label='Fitted PSF')

        ax.legend(loc=1, prop={'size': 8})      # Legend
        get_root().frame_fit.redraw()

    def Data():
        log(8, "ProfileAnswer :", zip(points, get_root().image.im0[tuple(points)]))
        # STAT
        # like profile_stat points[0] is x and points[1] is y
        ps = get_array_stat(get_root().image.im0[tuple(points)])

        ax = get_root().frame_result.reset_figure_ax()

        # LEN
        tmp1 = G.my_profile.point1
        tmp2 = G.my_profile.point2
        tlen = np.sqrt((tmp1[0] - tmp2[0])**2 + (tmp1[1] - tmp2[1])**2)

        lst = [
            ["LENGTH: ", tlen],
            ["MIN: ", ps["min"]],
            ["MAX: ", ps["max"]],
            ["MEAN: ", ps["mean"]],
            ["RMS: ", ps["rms"]],
        ]
        num = 1.
        for i in lst:
            ax.text(0.3, 1.0-num/(len(lst)+1), i[0]+"%.1f" % i[1])
            num += 1

        get_root().frame_result.redraw()

    Curve()
    Data()
    return


####################
#   2D 2D 2D
####################


def PlotStar2():   # the two images colormesh
    if (get_state().pick_type == "one") or (get_state().pick_type[0] == "many"):
        PlotOneStar2D()
    elif get_state().pick_type == "binary":
        PlotBinaryStar2D()


def PlotOneStar2D():
    x0, y0 = W.strehl["center_x"], W.strehl["center_y"]
    r99x, r99y = W.strehl["r99x"], W.strehl["r99y"]
    dx1, dx2 = int(max(x0-4*r99x, 0)), int(min(x0+4*r99x,
                                               len(get_root().image.im0) + 1))  # d like display
    dy1, dy2 = int(max(y0-4*r99y, 0)), int(min(y0+4*r99y,
                                               len(get_root().image.im0) + 1))  # c like cut If borders
    r = (dx1, dx2, dy1, dy2)  # Teh local cut applied to the image. To show it

    x, y = np.arange(r[0], r[1]), np.arange(r[2], r[3])
    Y, X = np.meshgrid(y, x)

    def Data(ax):
        ax.imshow(
            get_root().image.im0[r[0]:r[1], r[2]:r[3]],
            vmin=get_state().i_image_min_cut, vmax=get_state().i_image_max_cut,
            cmap=G.cbar.mappable.get_cmap().name, origin='lower')
        # extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")
        #G.ax31.format_coord=lambda x,y: "%.1f"%get_root().image.im0[r[2]+y,r[0]+x]
        ax.format_coord = lambda x, y: ""

    def Fit(ax):
        fit_type = get_state().fit_type
        if "Gaussian_hole" in fit_type:
            fit_type = "Gaussian_hole"
        ax.imshow(
            vars(BF)[fit_type]((X, Y), W.strehl),
            vmin=get_state().i_image_min_cut, vmax=get_state().i_image_max_cut,
            cmap=G.cbar.mappable.get_cmap().name, origin='lower',
                                          # extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")
                                          )  # need to comment the extent other wise too crowded and need to change rect position
        #G.ax32.format_coord= lambda x,y:'%.1f'% vars(BF)[fit_type]((r[2]+y,r[0]+x),W.strehl)
        ax.format_coord = lambda x, y: ""

    # Get && Reset figure
    figure = get_root().frame_result.get_figure()
    figure.clf()
    ax1 = figure.add_subplot(121)
    ax2 = figure.add_subplot(122)
    get_root().frame_result.update_skin()

    # Plot first image (data)
    Data(ax1)

    # Plot second image (fit)
    if get_state().fit_type != "None":
        Fit(ax2)
    else:
        Data(ax2)

    # APERTTURES
    params = W.strehl
    #   s   (te center of the rect is in fact the bottm left corner)

    # NOISE 8 RECT
    if (get_state().noise_type == "8rects"):
        rect = (x0 - params['r99x'], x0 + params['r99x'],
                y0 - params['r99y'], y0 + params['r99y'])
        var = IF.EightRectangleNoise(get_root().image.im0, rect, return_rectangle=1)[2]
        for p in var:
            center_tmp = (p[0][0]-r[0]-p[1]/2, p[0][1]-r[2]-p[2]/2)
            a = matplotlib.patches.Rectangle(
                (center_tmp[1], center_tmp[0]), p[2], p[1], facecolor='orange', edgecolor='black')
            ax2.add_patch(a)
        center = x0 - r[0], y0-r[2]

    # NOISE ANNULUS
    elif (get_state().noise_type == "elliptical_annulus"):
        # INNER
        tmpmin, tmpmax = W.ell_inner_ratio,  W.ell_outer_ratio
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
    if get_state().phot_type == "encircled_energy":
        tx = params["center_x"] - r[0]
        ty = params["center_y"] - r[2]
        a = matplotlib.patches.Rectangle(
            (ty-params['r99y'], tx-params['r99x']), 2*params['r99y'], 2*params['r99x'], facecolor='none', edgecolor='black')
        ax2.add_patch(a)

    # PHOT ELL
    elif get_state().phot_type == "elliptical_aperture":
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
    #plt.xticks( (r[0],r[1] ) )
    #plt.xticks( (r[2],r[3] ) )
    ax1.set_xticks(())
    ax1.set_yticks(())

    get_root().frame_result.redraw()
    return


def PlotBinaryStar2D():
    x0, y0 = W.strehl["x0"], W.strehl["y0"]
    x1, y1 = W.strehl["x1"], W.strehl["y1"]
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
    ax1 = get_root().frame_result.get_figure().add_subplot(121)
    ax1.imshow(
        get_root().image.im0[r[0]:r[1], r[2]:r[3]],
        vmin=get_state().i_image_min_cut, vmax=get_state().i_image_max_cut,
        cmap=G.cbar.mappable.get_cmap().name, origin='lower')

    # extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")
    ax1.format_coord = lambda x, y: "%.1f" % get_root().image.im0[y, x]
    ax1.format_coord = lambda x, y: ""
    # FIT
    if "Moffat" in get_state().fit_type:
        stg = "Moffat2pt"
    elif "Gaussian" in get_state().fit_type:
        stg = "Gaussian2pt"
    ax2 = get_root().frame_result.get_figure().add_subplot(122)
    ax2.imshow(
        vars(BF)[stg]((X, Y), W.strehl),
        vmin=get_state().i_image_min_cut, vmax=get_state().i_image_max_cut,
        cmap=G.cbar.mappable.get_cmap().name, origin='lower',
        # extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")
        )  # need to comment the extent other wise too crowded and need to change rect positio
    #ax2.format_coord= lambda x,y:'%.1f'% vars(BF)[stg]((y,x),W.strehl)
    ax2.format_coord = lambda x, y: ""
    get_root().frame_result.redraw()
    return

    ############
    # OTHERS
    ############


def CallContrastMap():
    """Not called"""
    G.contrast_fig = matplotlib.figure.Figure()
    ax = G.contrast_fig.add_subplot(111)

    ax.text(0.1, 0.7, 'Calculating\nContrast\nPlease Wait\n.....',
            verticalalignment='top', horizontalalignment='left',
            transform=ax.transAxes,
            color='green', fontsize=40)

    G.ContrastWindow = Tk()
    G.ContrastWindow.title("Contrast Map")
    G.ContrastCanvas = FigureCanvas(G.contrast_fig, master=G.ContrastWindow)
    G.ContrastCanvas.get_tk_widget().pack(side=TOP, expand=0, fill=BOTH)
    G.contrast_fig.canvas.draw()

    G.ContrastButtonFrame = Frame(G.ContrastWindow, bg="black")
    G.ContrastButtonFrame.pack(side=TOP, expand=0, fill=X)

    G.ContrastButton1Frame = Frame(G.ContrastWindow, bg="black")
    G.ContrastButton1Frame.pack(side=TOP, expand=0, fill=X)

    W.strehl["contrast_max"] = W.strehl["intensity"]

    Label(G.ContrastButton1Frame, text="Peak Intensity",
          **skin().fg_and_bg).grid(row=0, column=0, sticky="snew")

    G.TEXT = Text(G.ContrastButton1Frame, height=1)
    G.TEXT.bind()

    #G.v1= [ ]
    #v =  StringVar()
    #G.PeakContrast1Entry = Entry(G.ContrastButton1Frame, width=10,textvariable=v,font=skin().font.param )
    # G.PeakContrast1Entry.grid(row=0,column=1,sticky="snew")
    #G.PeakContrast1Entry.bind('<Return>',Get )
    # v.set("%.2f"%W.strehl["contrast_max"])
    # G.v1.append(v)

    def Get(event):
        log(1, G.v.get())

    def Worker():
        import ImageFunction as IF
        x, y, tdic = IF.ContrastMap(get_root().image.im0, (W.strehl["center_x"], W.strehl["center_y"]), interp=True, xmin=0.5, xmax=20, step=2, dic={
                                    "theta": 0, "ru": 1, "rv": 1}, background=0)  # get_state().get_answer(EA.BACKGROUND))

        FigurePlot(x, y, dic=tdic)


    G.contrast_thread = Thread(target=Worker)
    G.contrast_thread.daemon = True  # can close the program without closing this thread
    G.contrast_thread.start()

    G.ContrastWindow.mainloop()


def FigurePlot(x, y, dic={}):
    """ x and y can be simple list
    or also its can be list of list for a multiple axes
    dic : title:"string", logx:bol, logy:bol, xlabel:"" , ylabel:""
    """
    log(3, "MG.FigurePlotCalled")
    default_dic = {"warning": 0, "title": "no-title"}
    default_dic.update(dic)
    dic = default_dic

    def SubPlot(x, y):
        nx, ny = 7, 5
        if "logx" in dic:
            ax.set_xscale("log")
        if "logy" in dic:
            ax.set_yscale("log")
        if "xlabel" in dic:
            ax.set_xlabel(dic["xlabel"])
        if "ylabel" in dic:
            ax.set_ylabel(dic["ylabel"])

        ax.plot(x, y)

        ax2 = ax.twiny()
        ax2.set_xticks(np.arange(nx))
        xlist = np.linspace(0, x[-1] * get_root().header.pixel_scale, nx)
        xlist = [int(1000 * u) for u in xlist]
        ax2.set_xticklabels(xlist, rotation=45)
        ax2.set_xlabel(u"Distance [mas]")

        ax3 = ax.twinx()
        ax3.set_yticks(np.arange(ny))
        ylist = np.linspace(0, y[0], ny)
        ylist = [int(u) for u in ylist]
        ax3.set_yticklabels(ylist)
        ax3.set_ylabel(u"number count per pixel")
        ############
        # TWIN axes

    log(3, 50 * '_', "\n", currentThread().getName(),
        "Starting------------------\n")

    global ax
    G.contrast_fig.clf()
    # tfig.canvas.set_window_title(dic["title"])

    if not isinstance(x[0], list):  # otherwise multiple axes
        log(3, "FigurePlot, we make a single plot")
        ax = G.contrast_fig.add_subplot(111)
        #from mpl_toolkits.axes_grid1 import host_subplot
        #ax = host_subplot(111)
        SubPlot(x, y)
        log(3, "I will show ")
        G.contrast_fig.canvas.draw()

    # Over
    log(3, '_' * 50 + "\n", currentThread().getName(),
        'Exiting' + 20 * '-' + "\n")

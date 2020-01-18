"""
    Util functions
"""

# Standard
import re
from sys import argv as sys_argv
from os.path import dirname, abspath
from functools import lru_cache

# Package
from tkinter import RAISED, IntVar, PhotoImage
import matplotlib


_verbose = 10


def get_version():
    """Return: version string"""
    return '0.901'


def get_verbose():
    """Return verbose module variable"""
    return _verbose


def set_verbose(i_level):
    """Set verbose module variable"""
    _verbose = i_level
    return _verbose


@lru_cache(1)
def root_path():
    """Return: path of this file"""
    return dirname(abspath(__file__))


@lru_cache(1)
def icon_path():
    """Return path of window icon"""
    return root_path() + '/res/bato_chico.gif'


@lru_cache(1)
def _get_logger():
    import logging
    # Logger
    logFormatter = logging.Formatter(
        'ABISM: %(asctime)-8s: %(message)s',
        '%H:%M:%S')

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(logFormatter)

    logger = logging.getLogger('ABISM')
    logger.setLevel(logging.INFO)
    logger.handlers = [consoleHandler]

    return logger


def log(i, *args):
    """Log utility
    @brief: this is a log accroding to the verbose
            very simple function, very large comment
    @param: i is the verbose,
    @param: **args are the strings to print,
    @return: print in the stdout, means the calling terminal
        nickname py  me
        CRITICAL 50  -3
        ERROR    40  -2
        WARNING  30  -1
        INFO     20  1
        DEBUG    10  2
        NOTSET    0  3
    """
    if get_verbose() < i: return

    message = str(i) + ': ' + ' '.join([str(arg) for arg in args])
    _get_logger().info(message)


# TODO remove this
class VoidClass:
    """Helper container"""


def MainVar():
    """Init all <- Called by WindowRoot"""
    WorkVar()  # Initial WorkVar
    GuiVar()  # Initialt Gui vars



def GuiVar():
    """Define the shared variables for the GUI definition"""
    import front.util_front as G

    # BUTTON WIDTH
    G.button_width = 12  # the width of the standard buttons
    G.menu_button_width = 8  # Size of menu buttons

    # GUI FORM
    # we don't hide text frame by default, the text framme is the output frame on the left
    G.hidden_text_bool = 0
    G.scale_menu_type = "column" # can be "column" or "cascade"
    G.all_frame = []                        # all frames will be here to change color
    # Can be tkinter or shell , written interaction with the mainloop
    G.interaction_type = "tkinter"
    G.last_top_size = 300

    # GEO DIC
    G.geo_dic = {}                        # geometry dictionnay
    G.geo_dic['ResultFrame'] = 300

    # COLORS
    G.all_cmaps = sorted([i for i in dir(matplotlib.cm) if hasattr(
        getattr(matplotlib.cm, i), 'N')])  # inclouding inverse


    # SCALE dic for the color and contrast
    G.scale_dic = [{}]
    G.scale_dic[0]["cmap"] = "jet"
    G.scale_dic[0]["contour"] = False
    G.scale_dic[0]["answer"] = "detector"
    G.scale_dic[0]["percent"] = 99.99
    G.scale_dic[0]["scale_cut_type"] = "sigma_clip"
    G.scale_dic[0]["sigma"] = 3
    G.scale_dic[0]["stretch"] = "linear"

    # BOOL TODO remove
    G.manual_cut_bool = 0
    G.more_bool = 0

    G.toolbar_fit_bool = False
    G.toolbar_result_bool = False
    G.manual_back_bool = False
    # the labels on the left, when open image, this is set to true
    G.label_bool = True
    G.result_bool = True                          # show the full results frame
    G.top_bool = True
    G.in_arrow_frame = None                          # no body in lefftoparrowframe

    # CLASS
    # (we save the tkvariables ) # it may be changed see image parameters
    G.tkvar = VoidClass()
    G.tkentry = VoidClass()

    from tkinter import font as tkFont

    G.sub_paned_arg = {"minsize": 22, "pady": 0, "sticky": "nsew"}

    ######################
    #   WORK Variables
    #######################


def WorkVar():
    import back.util_back as W
    import front.util_front as G
    """Define the varaibles that we define the way the calculations should be runned.
    This is an important function of the software.
    """
    # Define verbose level
    set_verbose(5)

    # Cache locally arg in
    W.sys_argv = sys_argv

    class tmp:
        """ Placeholder of the most ugly container
        this is for the temporary variables to pass from one function to an other.
        Like W.tmp.lst... carrefull
        """
    W.tmp = tmp()

    W.imstat = VoidClass()
    W.image_name = 'no_image_name'
    W.strehl_type = 'max'
    W.strehl = {}

    W.type = {}
    W.type["pick"] = 'one'
    W.type["fit"] = 'Moffat2D'                                # FIT  TYPE
    W.type["phot"] = 'elliptical_aperture'  # PHOTOMETRY type
    W.type["noise"] = 'elliptical_annulus'
    W.type["aperture"] = "fit"
    W.err_msg = []
    W.mode = "manual"  # oppsite of automatic
    W.image_click = (0., 0.)
    W.image_release = (0., 0.)

    W.same_center_var = IntVar()
    W.same_center_var.set(1)
    W.aniso_var = IntVar()
    W.aniso_var.set(1)
    W.same_psf_var = IntVar()
    W.same_psf_var.set(1)

    W.cube_bool = 0
    W.cube_num = -1
    W.rect_phot_bool = 0  # for rectanglephot called by command
    W.same_psf = 1

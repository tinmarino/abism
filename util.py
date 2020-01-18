"""
    Util functions
"""

# Standard
import re
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
    """Log utility read verbose"""
    if get_verbose() < i: return

    message = str(i) + ': ' + ' '.join([str(arg) for arg in args])
    _get_logger().info(message)


##################################################
##################################################
##################################################
# TODO remove this below
class VoidClass:
    """Helper container"""


def MainVar():
    """Init all <- Called by WindowRoot"""
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


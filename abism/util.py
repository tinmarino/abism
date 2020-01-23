"""
    Util functions
    Include answer.py in scope (see import at bottom)
"""

# Standard
import sys
import os
from os.path import dirname, abspath
from functools import lru_cache
from enum import Enum

# Local
from abism import __version__

_verbose = 10  # Verbose level
_parsed_args = None  # Arguments from argparse

# Keep a trace
# this global removes others
_root = None





def parse_argument():
    # pylint: disable=global-statement
    global _parsed_args, _verbose

    from argparse import ArgumentParser
    from sys import argv
    parser = ArgumentParser(description='Adaptive Background Interferometric Strehl Meter')

    # Image
    parser.add_argument(
        '-i', '--image', metavar='image.fits', type=str,
        action='append',
        help='image to diplay: filepath of the .fits')

    parser.add_argument(
        'image', metavar='image.fits', type=str,
        default='',
        nargs='?', action='append',
        help='image to diplay: the first one is chosen')

    parser.add_argument(
        '-v', '--verbose', type=int,
        default=0, action='store',
        help='verbosity level: 0..10')


    # Custom
    parsed_args = parser.parse_args()
    log(3, 'Parsed initially:', parsed_args)
    parsed_args.script = argv[0]
    parsed_args.image = parsed_args.image[0]

    # set
    _parsed_args = parsed_args
    _verbose = _parsed_args.verbose


def get_colormap_list():
    """Favorite colormap of Tinmarino (me)
    Link: https://matplotlib.org/examples/color/colormaps_reference.html
    Perceptually Uniform Sequential:
        magma       <- the (3) others have a high too yellow (
    Diverging:
        RdYlBlu     <- high contrast (need one), more than Spectral
        PrGn        <- diffrent: 2 colors: no blue, rew, black, white
    Miscellanous:
        cubehelix   <- enhanced B&W (with some pink, greeny blue) awesome!

    """
    return [
        ['Black&White', 'bone'],
        ['Magma', 'magma'],
        ['Cubehelix', 'cubehelix'],
        ['RdYlBu_r', 'RdYlBu_r'],
        ['PRGn', 'PRGn']]


def get_stretch_list():
    """Alias for scale function for image display
    fct should only go in comment, they are in MyNormalize
    """
    return [
        ["Lin", "x", "linear"],
        ["Sqrt", "x**0.5", "sqrt"],
        ["Square", "x**2", "square"],
        ["Log", "np.log(x+1)/0.69", "log"],
        ["Arcsinh", "", "arcsinh"]]


def get_cut_list():
    """Min and max cut
    label , s_type, key, value
    Note: you can remove key
    """
    return [
        ["RMS", "sigma_clip", "sigma", 3],
        ["99.95%", "percent", "percent", 99.95],
        ["99.9%", "percent", "percent", 99.9],
        ["99%", "percent", "percent", 99],
        ["90%", "percent", "percent", 90],
        ["None", "None", "truc", "truc"]]


def get_fit_list():
    """3 fct or just no fit"""
    return ["Gaussian", "Moffat", "Bessel1", "None"]


def abism_val(enum_answer):
    return get_state().answers[enum_answer].value


class EA(Enum):
    """Enum of Answer names
    EX.value = (s_display_text, class_ctor)
    Center:   # sky -> ra, dec; detector -> x, y
    """
    from abism.answer import AnswerNum, AnswerLuminosity, AnswerFwhm

    # Main
    STREHL = ['Strehl', AnswerNum]
    STREHL_EQ = [u'Eq. SR(2.17\u03bcm)', AnswerNum]

    # Detail
    CENTER = ['Center', AnswerNum]
    FWHM_ABE = ['FWHM a,b,e', AnswerFwhm]
    PHOTOMETRY = ['Photometry', AnswerLuminosity]
    BACKGROUND = ['Sky', AnswerLuminosity]
    NOISE = ['Sky RMS', AnswerLuminosity]
    SN = ['S/N', AnswerNum]

    # Luxury
    R99 = ['R99', AnswerNum]
    INTENSITY = ['Peak', AnswerLuminosity]
    INTENSITY_THEORY = ['Ith', AnswerLuminosity]

    # Errors
    ERR_STREHL = ['Strehl Error', AnswerNum]
    ERR_STREHL_EQ = ['Strehl Equivalent Error', AnswerNum]


class AbismState:
    """Confiugration from user (front) to science (back)"""
    def __init__(self):
        # The returns dictionary: EAnswer -> Answser Object
        self.answers = {}

        # Type
        self.fit_type = get_fit_list()[1]
        self.pick_type = 'one'
        self.phot_type = 'elliptical_aperture'
        self.noise_type = 'elliptical_annulus'
        self.aperture_type = 'fit'
        self.pick_old = ''
        self.b_aniso = True
        self.b_same_psf = True
        self.b_same_center = True

        # The value of the manually added sky level (rarely used)
        self.i_background = 0

        # UI
        self.s_answer_unit = 'detector'  # detector or 'sky'
        self.s_image_color_map = get_colormap_list()[0][1]
        self.s_image_stretch = get_stretch_list()[0][2]
        self.s_image_cut = get_cut_list()[0][1]  # fct
        self.i_image_cut = get_cut_list()[0][3]  # param
        self.i_image_min_cut = 0
        self.i_image_max_cut = 0
        self.b_image_contour = False
        self.b_image_reverse = False

    def reset_answers(self):
        self.answers = {}
        return self.answers

    def add_answer(self, enum_answer, value, *arg, **args):
        # Check if overwork
        if enum_answer in self.answers:
            log(0, 'Warning the', enum_answer, 'has already been calculated')

        # Retrieve class ctor from enum
        class_answer = enum_answer.value[1]

        # Craft anwser
        answer = class_answer(enum_answer, value, *arg, **args)

        # Save answer
        self.answers[enum_answer] = answer

    def get_answer(self, enum_answer):
        """Get only the value"""
        return self.answers[enum_answer].value



@lru_cache(1)
def get_state():
    return AbismState()


def get_root():
    return _root


def set_root(root):
    # pylint: disable=global-statement
    global _root; _root = root


def quit_process():
    """Kill process"""
    log(1, 'Closing Abism, Goodbye. Come back soon.' + "\n" + 100 * '_' + 3 * "\n")
    # parent.destroy()
    sys.exit(0)


def restart():
    """ TODO move me to Global Definer, WritePref and ReadPref
        Pushing this button will close ABISM and restart it the same way it was launch before.
        Programmers: this is made to reload the Software if a modification in the code were made.
    """

    ###########
    # PREPARE STG command line args
    stg = 'python ' + _parsed_args.script + ' '
    arg_dic = vars(_parsed_args)
    for key, value in arg_dic.items():
        if key == 'script' or not value: continue
        print(key, ' ', arg_dic[key])
        stg += '--' + key + ' ' + str(value) + ' '
    stg += '&'
    log(0, "\n\n\n" + 80 * "_" + "\n",
        "Restarting ABISM with command:\n" + stg + "\nplease wait")

    ##########
    # DESTROY AND LAUNCH
    get_root().destroy()  # I destroy Window,
    os.system(stg)         # I call an other instance
    sys.exit(0)         # I exit the current process.
    # As the loop is now opened, this may not be necessary but anyway it is safer


def get_version():
    """Return: version string"""
    return __version__


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
    return dirname(abspath(__file__)) + '/'


class DotDic(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


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


# Impersonate answser
import abism.answer
for truc in dir(abism.answer):
    # pylint: disable = exec-used
    exec(truc + ' = ' + 'abism.answer.' + truc)

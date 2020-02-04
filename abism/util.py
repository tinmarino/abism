"""
    Abism util functions
"""

# Standard
import sys
import os
import re
import inspect
from os.path import dirname, abspath, basename
from functools import lru_cache
from enum import Enum


_parsed_args = None  # Arguments from argparse


@lru_cache(1)
def parse_argument():
    """Do not call get_state here -> infinite loop"""
    # pylint: disable=global-statement
    global _parsed_args

    from argparse import ArgumentParser
    from sys import argv
    parser = ArgumentParser(description='Adaptive Background Interferometric Strehl Meter')

    # Image
    parser.add_argument(
        '-i', '--image', metavar='image.fits', type=str, action='append',
        help='image to diplay: filepath of the .fits')

    parser.add_argument(
        'image', metavar='image.fits', type=str, nargs='?', action='append',
        default='',
        help='image to diplay: the first one is chosen')

    parser.add_argument(
        '-v', '--verbose', type=int, action='store',
        default=0,
        help='verbosity level: 0..10')

    # Gui
    #####

    # Geometry (defaults for a 1080 x 1920)
    parser.add_argument(
        '--gui-geometry', type=str, action='store', nargs='?',
        default='1200x920+150+50',
        help=('window geometry: wxh±x±y | ex: 12+34-56+78 '
              '<- where 12 is width, 34 is height, '
              '56 is leftmost, 78 is topmost'))

    # Sash1
    parser.add_argument(
        '--gui-sash-root', type=int, action='store', nargs='?',
        default=400,
        help='separator (main vertical) position from left (in pixel)')

    # Sash2
    parser.add_argument(
        '--gui-sash-image', type=int, action='store', nargs='?',
        default=700,
        help='separator (image vertical) position from top (in pixel)')


    # Image View
    ############

    # Colormap
    parser.add_argument(
        '-c', '--cmap', metavar='ColorMap', type=str, nargs='?', action='store',
        default='bone',
        help='Colormap for the image')

    parser.add_argument(
        '--stretch', metavar='StretchFunction', type=str, nargs='?', action='store',
        default='log',
        help='Stretch function of the displayed image '
             '(linear, sqrt, square, log, arcsinh')

    parser.add_argument(
        '--cut', metavar='CutType', type=str, nargs='?', action='store',
        default='99.9%',
        help='Type of cut min and max value for image display scale '
             'Can in (%%) percentage or in (s) sigma '
             '(99%, 3s, None')

    # Custom
    try:
        # Parse from sys args
        parsed_args = parser.parse_args()
    except SystemExit as e:
        if str(e) == '0': sys.exit()
        print('Argument Parsing error:', str(e))
        parsed_args = parser.parse_args([])

    parsed_args.script = argv[0]
    parsed_args.image = parsed_args.image[0]

    # set
    _parsed_args = parsed_args

    return _parsed_args


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


def get_fit_list():
    """3 fct or just no fit"""
    return ["Gaussian", "Moffat", "Bessel1", "None"]


def get_av(enum_answer):
    """Get Abism Answer, shortcut"""
    return get_state().get_answer(enum_answer)


def set_aa(enum_answer, value, *arg, unit=None, **args):
    """Set Abism Answer shortcut"""
    return get_state().add_answer(enum_answer, value, *arg, unit=unit, **args)


def get_aa(enum_answer):
    """Get Abism Answer, shortcut"""
    return get_state().get_answer_obj(enum_answer)


def str_pretty(obj, indent=2, depth=4, rec=0, key='', silent=[]):
    """Returns: pretty str of an object
    obj    <- object to print
    indent <- indent per depth
    depth  <- maximum recursion depth
    rec, key <- used in recursion
    silent <- str name of class OR variable to not recurse
    """
    # pylint: disable = too-many-arguments, dangerous-default-value
    # Check in: recursion depth
    if rec >= depth: return ''

    # Init
    s_indent = ' ' * indent * rec
    stg = s_indent

    if key != '': stg += str(key) + ': '

    # Discriminate && Check if final
    items = {}
    if isinstance(obj, list):
        items = enumerate(obj)
    elif isinstance(obj, dict):
        items = obj.items()
    elif '__dict__' in dir(obj):
        items = obj.__dict__.items()
    if not items:
        return stg + str(obj).replace('\n', '\n' + s_indent)

    # Recurse
    stg += '(' + type(obj).__name__ + ')\n'
    items = dict(sorted(items)).items()
    if str(key) not in silent and type(obj).__name__ not in silent:
        for k, v in items:
            stg += str_pretty(v, indent=indent, rec=rec+1, key=k, silent=silent) + "\n"
    else:
        stg += ' ' * (indent) * (rec + 1) + "Silenced !\n"

    # Return without empty lines
    return re.sub(r'\n\s*\n', '\n', stg)[:-1]


class DotDic(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __repr__ = str_pretty


class EA(Enum):
    """Enum of Answer names
    EX.value = (s_display_text, class_ctor
    Center:   # sky -> ra, dec; detector -> x, y
    """
    from abism.answer import AnswerNum, AnswerLuminosity, AnswerFwhm, \
        AnswerPosition, AnswerDistance, AnswerObject, AnswerAngle

    # Main
    STREHL = ['Strehl', AnswerNum]
    STREHL_EQ = [u'Eq. SR(2.17\u03bcm)', AnswerNum]

    # Detail <- used for calculation
    CENTER = ['Center', AnswerPosition]
    FWHM_ABE = ['FWHM a,b,e', AnswerFwhm]
    PHOTOMETRY = ['Photometry', AnswerLuminosity]
    BACKGROUND = ['Sky', AnswerLuminosity]
    SN = ['S/N', AnswerNum]

    # Luxury
    R99 = ['R99', AnswerNum]
    INTENSITY = ['Peak', AnswerLuminosity]
    INTENSITY_THEORY = ['Ith', AnswerLuminosity]
    BESSEL_INTEGER = ['Ith', AnswerNum]

    # Binary
    BINARY = ['Binary', AnswerObject]
    STAR1 = ['1 Star', AnswerPosition]
    STAR2 = ['2 Star', AnswerPosition]
    PHOTOMETRY1 = ['Phot1', AnswerLuminosity]
    PHOTOMETRY2 = ['Phot2', AnswerLuminosity]
    INTENSITY1 = ['Peak1', AnswerLuminosity]
    INTENSITY2 = ['Peak2', AnswerLuminosity]
    FLUX_RATIO = ['Flux ratio', AnswerNum]
    SEPARATION = ['Separation', AnswerDistance]
    ORIENTATION = ['Orientation', AnswerAngle]
    STREHL1 = ['Strehl1', AnswerNum]
    STREHL2 = ['Strehl2', AnswerNum]


class EPick(Enum):
    """Pick type -> class in pick"""
    NO = 1
    ONE = 2
    BINARY = 3
    TIGHT = 4
    STAT = 5
    PROFILE = 6
    ELLIPSE = 7


class EPhot(Enum):
    """Photometric type: enum, description
    See implementation in StrehlImage
    """
    FIT = 'Mesured from the fitted function'
    ELLIPTICAL = ('Mesured from an elliptical aperture containing 99%% of the energy, '
                  'which bound are determined by the fit')
    RECTANGLE = ('Mesured from a rectangle aperture containing 99%% of the energy, '
                 'which bound are determined by the fit')
    MANUAL = 'Mesured from the rectangle section total inensity'


class ESky(Enum):
    """Sky mesurement methos: enum, description"""
    ANNULUS = 'Elliptical annulus around object'
    FIT = 'Fitted sky parameter (alias background)'
    RECT8 = ('8 Rectangles around object, distance estimated from fit, '
             'in the futur, it may enable non straight sky')
    MANUAL = 'Given by a wise user'
    NONE = 'Zero sky <- from a well reduced image'


class AbismState(DotDic):
    """Confiugration from user (front) to science (back)"""
    # pylint: disable = super-init-not-called
    def __init__(self):
        import tkinter as tk

        self.verbose = parse_argument().verbose

        # ImageInfo cutom type, setted when open_file
        self.image = None

        # The returns dictionary: EAnswer -> Answser Object
        self.answers = {}
        # String -> float
        self.d_fit_param = {}
        self.d_fit_error = {}

        # Record the root gui for get_root
        self.tk_root = None

        # The last pick string, to dissconnect
        self.e_pick_type = EPick.ONE
        self.pick = None
        self.tk_pick = tk.StringVar()
        self.tk_pick.set(self.e_pick_type)

        # Type
        self.s_fit_type = get_fit_list()[1]
        self.e_phot_type = EPhot.ELLIPTICAL
        self.e_sky_type = ESky.ANNULUS
        self.b_aniso = True
        self.b_same_psf = True

        # The value of the manually added sky level (rarely used)
        self.i_background = 0

        # UI image
        self.s_image_color_map = parse_argument().cmap
        self.s_image_stretch = parse_argument().stretch
        self.s_image_cut = parse_argument().cut
        self.i_image_min_cut = 0
        self.i_image_max_cut = 0
        self.b_image_contour = False
        self.b_image_reverse = False

        # UI text
        self.s_answer_unit = 'detector'  # detector or 'sky'

    def reset_answers(self):
        self.answers = {}
        return self.answers

    def add_answer(self, enum_answer, value, *arg, unit=None, **args):
        from abism.answer import AnswerSky

        # Check if overwork
        if enum_answer in self.answers:
            log(1, 'Warning the', enum_answer, 'has already been calculated')

        # Retrieve class ctor from enum
        text, cls = enum_answer.value

        # Craft anwser
        if isinstance(value, AnswerSky):
            answer = value
            answer.text = text
        else:
            answer = cls(text, value, *arg, **args)

        # Add unit
        if unit is not None:
            answer.unit = unit

        # Save answer
        self.answers[enum_answer.name] = answer

        # Return
        return answer

    def get_answer_obj(self, enum_answer):
        return self.answers[enum_answer.name]

    def get_answer(self, enum_answer):
        """Get only the value"""
        return self.get_answer_obj(enum_answer).value

    def __repr__(self):
        l_silent = ['pick', 'tk_pick', 'tk_root']
        return str_pretty(self, silent=l_silent, depth=6)


@lru_cache(1)
def get_state():
    return AbismState()


def get_root():
    return get_state().tk_root


def quit_process():
    """Kill process"""
    log(1, 'Closing Abism, Goodbye. Come back soon.' + "\n" + 100 * '_' + 3 * "\n")
    get_root().destroy()


def restart():
    """ TODO move me to Global Definer, WritePref and ReadPref
        Pushing this button will close ABISM and restart it the same way it was launch before.
    """

    ###########
    # PREPARE STG command line args
    stg = 'python ' + _parsed_args.script + ' '
    arg_dic = vars(_parsed_args)
    for key, value in arg_dic.items():
        if key == 'script' or not value: continue
        log(3, 'Cmd (key, value)', key, ' ', arg_dic[key])
        key = key.replace('_', '-')
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


@lru_cache(1)
def root_path():
    """Return: path of this file"""
    return dirname(abspath(__file__)) + '/'


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
    if get_state().verbose < i: return

    message = str(i) + ': ' + ' '.join([str(arg) for arg in args])
    if get_state().verbose > 3:
        caller = inspect.currentframe().f_back.f_code
        message += ('    (' + caller.co_name
                    + '.' + str(caller.co_firstlineno)
                    + '@' + basename(caller.co_filename) + ')')

    _get_logger().info(message)

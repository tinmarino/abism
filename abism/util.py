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

# Keep a trace
# this global removes others
_root = None





@lru_cache(1)
def parse_argument():
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

    # Custom
    try:
        # Parse from sys args
        parsed_args = parser.parse_args()
    except SystemExit as e:
        log(0, 'Argument Parsing error', str(e))
        parsed_args = parser.parse_args([])

    parsed_args.script = argv[0]
    parsed_args.image = parsed_args.image[0]

    # set
    _parsed_args = parsed_args

    get_state().verbose = parsed_args.verbose

    log(0, 'Parsed initially:', parsed_args)

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
    return get_state().get_answer(enum_answer)


def str_pretty(obj, indent=2, depth=4, rec=0, key=''):
    """Returns: pretty str of an object
    obj    <- object to print
    indent <- indent per depth
    depth  <- maximum recursion depth
    rec, key <- used in recursion
    """
    # Check in: recursion depth
    if rec >= depth: return ''

    # Init
    s_indent = ' ' * indent * rec
    items = {}
    stg = s_indent

    if key != '': stg += str(key) + ': '

    # Discriminate && Check if final
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
    for k, v in items:
        stg += str_pretty(v, indent=indent, rec=rec+1, key=k) + "\n"

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

    # Detail
    CENTER = ['Center', AnswerPosition]
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

    # Binary
    BINARY = ['Binary', AnswerObject]
    STAR1 = ['1 Star', AnswerPosition]
    STAR2 = ['2 Star', AnswerPosition]
    PHOTOMETRY1 = ['Phot1', AnswerLuminosity]
    PHOTOMETRY2 = ['Phot2', AnswerLuminosity]
    FLUX_RATIO = ['Flux ratio', AnswerNum]
    SEPARATION = ['Separation', AnswerDistance]
    ORIENTATION = ['Orientation', AnswerAngle]
    STREHL1 = ['Strehl1', AnswerNum]
    STREHL2 = ['Strehl2', AnswerNum]

    # Error Binary
    ERR_SEPARATION = ['Separation Error', AnswerDistance]


class AbismState(DotDic):
    """Confiugration from user (front) to science (back)"""
    # pylint: disable = super-init-not-called
    def __init__(self):
        self.verbose = 0

        # IamgeInfo cutom type, setted when open_file
        self.image = None

        # The returns dictionary: EAnswer -> Answser Object
        self.answers = {}

        # The last pick string, to dissconnect
        # TODO better be an object
        self.pick_type = 'one'
        self.pick_old = ''
        self.pick = None
        self.tk_pick = None

        # Type
        self.fit_type = get_fit_list()[1]
        self.phot_type = 'elliptical_aperture'
        self.noise_type = 'elliptical_annulus'
        self.aperture_type = 'fit'
        self.b_aniso = True
        self.b_same_psf = True
        self.b_same_center = True

        # The value of the manually added sky level (rarely used)
        self.i_background = 0

        # UI image
        self.s_image_color_map = get_colormap_list()[0][1]
        self.s_image_stretch = get_stretch_list()[0][2]
        self.s_image_cut = get_cut_list()[0][1]  # fct
        self.i_image_cut = get_cut_list()[0][3]  # param
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
        # Check if overwork
        if enum_answer in self.answers:
            log(1, 'Warning the', enum_answer, 'has already been calculated')

        # Retrieve class ctor from enum
        text, cls = enum_answer.value

        # Craft anwser
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
    get_root().destroy()


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

"""
    Util functions
"""

# Standard
import re
from os.path import dirname, abspath
from functools import lru_cache
from argparse import ArgumentParser

# Package
from tkinter import RAISED, IntVar, PhotoImage
import matplotlib



_verbose = 10  # Verbose level
_parsed_args = None  # Arguments from argparse

# Keep a trace
# this global removes others
_root = None


def parse_argument():
    parser = ArgumentParser(description='Adaptive Background Interferometric Strehl Meter')

    parser.add_argument(
        'image_name', metavar='image.fits', type=str,
        default='', nargs='?',
        help='image to diplay: filepath of the .fits')

    parser.add_argument(
        '-v', '--verbose',
        dest='verbose', action='store', type=int, default=0,
        help='verbosity level: 0..10')

    # set
    global _parsed_args, verbose
    _parsed_args = parser.parse_args()
    _verbose = _parsed_args.verbose


def get_root():
    """tricky but not that much"""
    return _root


def set_root(root):
    global _root; _root = root


class ImageInfo:
    "Image and its info"""
    def __init__(self):
        """
        image_name
        image_click = (0., 0.)
        image_release = (0., 0.)
        """
        # Current image filepath
        self.name = _parsed_args.image_name
        self.is_cube = False  # Cube it is not
        self.cube_num = -1
        self.click = (0., 0.)  # Mouse click position
        self.release = (0., 0.)  # You guess ?

        self.bpm = None  # Bad Pixel mask array
        self.bpm_name = None  # Bad Pixel Mask filepath

        # Now we speak
        self.hdulist = None  # From fits.open
        self.im0 = None  # np.array the image !!
        self.sort = None  # Sorted image for cut and histograms


class AbismState:
    """Confiugration from user (front) to science (back)"""
    def __init__(self):
        """Radio button state
        What is the user asking for ?
        """
        pass


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

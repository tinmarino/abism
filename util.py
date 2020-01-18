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
_image_name = None  # the current image filepath


def parse_argument():
    parser = ArgumentParser(description='Adaptive Background Interferometric Strehl Meter')

    parser.add_argument(
        'image_name', metavar='image.fits', type=str,
        default='no_image_name', nargs='?',
        help='image to diplay: filepath of the .fits')

    parser.add_argument(
        '-v', '--verbose',
        dest='verbose', action='store', type=int, default=0,
        help='verbosity level: 0..10')

    # set
    global _verbose, _image_name
    _parsed_args = parser.parse_args()
    _verbose = _parsed_args.verbose
    _image_name = _parsed_args.image_name


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

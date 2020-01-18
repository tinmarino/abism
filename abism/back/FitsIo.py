"""
    Fits image format io
"""

from astropy.io import fits
from numpy import isnan

from plugin.ReadHeader import CallHeaderClass
from back.Stat import Stat

from .util import log

import front.util_front as G
import back.util_back as W


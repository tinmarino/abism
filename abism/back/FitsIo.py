"""
    Fits image format io
"""

from astropy.io import fits
from numpy import isnan

from abism.plugin.ReadHeader import CallHeaderClass
from abism.back.Stat import Stat

from abism.util import log

import abism.front.util_front as G
import abism.back.util_back as W


"""
    Used as cache
"""

from sys import argv as std_argv
from abism.util import get_state


sys_argv = std_argv

class VoidClass:
    """ Placeholder of the most ugly container
    this is for the temporary variables to pass from one function to an other.
    Like W.tmp.lst... carrefull
    """
tmp = VoidClass()

imstat = VoidClass()
strehl_type = 'max'
strehl = {}

err_msg = []
mode = "manual"  # oppsite of automatic


rect_phot_bool = 0  # for rectanglephot called by command
same_psf = 1

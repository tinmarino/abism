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
    Clean  AnswerFrame
    """
tmp = VoidClass()

strehl_type = 'max'
strehl = {}


rect_phot_bool = 0  # for rectanglephot called by command

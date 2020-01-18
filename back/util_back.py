"""
    Used as cache
"""

from sys import argv as std_argv
import util


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

type = {}
type["pick"] = 'one'
type["fit"] = 'Moffat2D'                                # FIT  TYPE
type["phot"] = 'elliptical_aperture'  # PHOTOMETRY type
type["noise"] = 'elliptical_annulus'
type["aperture"] = "fit"
err_msg = []
mode = "manual"  # oppsite of automatic


rect_phot_bool = 0  # for rectanglephot called by command
same_psf = 1

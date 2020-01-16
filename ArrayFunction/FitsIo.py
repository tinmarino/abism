"""
    Fits image format io
"""

import pyfits
from numpy import isnan

from ReadHeader import CallHeaderClass
from Stat import Stat


import GuyVariables as G
import WorkVariables as W


def OpenImage(new_fits=True):
    """Open image from path
    new_fits if a new file, and not cube scrolling
    Fully global ...
    """

    if new_fits:
        W.hdulist = pyfits.open(W.image_name)
        W.Im0 = W.hdulist[0].data  # define the 2d image : W.Im0
        W.Im0[isnan(W.Im0)] = 0  # delete the np.nan
        # Parse header
        CallHeaderClass(W.hdulist[0].header)

    if len(W.hdulist[0].data.shape) == 3:
        if new_fits:
            # we start with the last index
            W.cube_num = W.hdulist[0].data.shape[0] - 1
        # should run if abs(G.cube_num)<len(G.hdulist)
        if abs(W.cube_num) < len(W.hdulist[0].data[:, 0, 0]):
            if W.cube_bool == 0:  # to load cube frame
                W.cube_bool = 1
                G.ImageFrame.Cube()
            W.Im0 = W.hdulist[0].data[W.cube_num]

        else:
            W.cube_num = W.hdulist[0].data.shape[0] - 1
            W.log(1, '\nERROR InitImage@MyGui.py :' + W.image_name
                  + ' has no index ' + str(W.cube_num)
                  + 'Go back to the last cube index :'
                  + str(W.cube_num) + "\n")
        G.cube_var.set(int(W.cube_num + 1))

    else:  # including image not a cube, we try to destroy cube frame
        W.cube_bool = 0
        G.ImageFrame.Cube()

    if new_fits:
        ScienceVariable()


def ScienceVariable():
    """ Get variable, stat from image
    Fully global ....
    """
    # BPM
    if "bpm_name" in vars(W):
        hdu = pyfits.open(W.bpm_name)
        W.Im_bpm = hdu[0].data
    else:
        W.Im_bpm = 0 * W.Im0 + 1
    # Sorted image
    W.sort = W.Im0.flatten()
    W.sort.sort()
    # STAT
    vars(W.imstat).update(Stat(W.Im0))

    # Image parameters
    if "ManualFrame" in vars(G):
        for i in G.image_parameter_list:
            vars(G.tkvar)[i[1]].set(vars(W.head)[i[1]])
        # to restore the values in the unclosed ImageParameters Frame
        G.LabelFrame.set_image_parameters("", destroy=False)
    # LABELS
    G.LabelFrame.update()
    # TODO, after refactoring INitGui and MyGui
    from MyGui import FitType
    FitType(W.type["fit"])


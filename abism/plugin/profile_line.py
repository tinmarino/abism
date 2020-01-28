"""
    Profile line user shower, callback of a tool
"""

import numpy as np
import tkinter as tk

from abism.back import ImageFunction as IF
from abism.back.image_info import get_array_stat

from abism.util import get_state, get_root, log

def show_profile(point1, point2):
    """Callback for Profile Pick: 1 and 2D"""
    # Get data to plot
    ab, od, points = IF.RadialLine(
        get_state().image.im0, (point1, point2), return_point=1)

    # FIT
    # if ( get_state().fit_type != "None" ) & ( "strehl" in vars(W) ):
    #  I_theory = vars(BF) [get_state().fit_type ](points,W.strehl["fit_dic"],get_state().fit_type)
    #  G.ax2.plot(ab,I_theory,color='purple',linewidth=2,label='Fitted PSF')

    # Plot <- Reset
    ax = get_root().frame_fit.reset_figure_ax()
    ax.plot(ab, od, '-', linewidth=1, label="Data")
    ax.legend(loc=1, prop={'size': 8})
    get_root().frame_fit.redraw()

    log(8, "ProfileAnswer :", zip(points, get_state().image.im0[tuple(points)]))

    # Get stat
    ps = get_array_stat(get_state().image.im0[tuple(points)])
    # LEN
    tlen = np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    lst = [
        ["LENGTH: ", tlen],
        ["MIN: ", ps.min],
        ["MAX: ", ps.max],
        ["MEAN: ", ps.mean],
        ["RMS: ", ps.rms],
    ]

    # Plot <- Reset
    ax = get_root().frame_result.reset_figure_ax()
    # like profile_stat points[0] is x and points[1] is y
    for num, (label, value) in enumerate(lst):
        ax.text(0.3, 1.0 - num / (len(lst) + 1), label + "%.1f" % value)
    get_root().frame_result.redraw()

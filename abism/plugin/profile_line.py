"""
    Profile line user shower, callback of a tool
"""

import numpy as np

from abism.back import ImageFunction as IF
from abism.back.fit_template_function import get_fit_function
from abism.back.image_info import get_array_stat

from abism.util import get_state, get_root, log

def show_profile(point1, point2):
    """Callback for Profile Pick: 1 and 2D"""
    # Get data to plot
    ab, od, points = IF.RadialLine(
        get_state().image.im0, (point1, point2), return_point=1)

    # Plot <- Reset
    ax = get_root().frame_fit.reset_figure_ax()
    ax.legend(loc=1, prop={'size': 8})

    # Data
    ax.plot(ab, od, '-', linewidth=2, label="Data")

    # Fit
    fit_fct = get_fit_function()
    do_plot_fit = get_state().s_fit_type != "None"
    do_plot_fit = do_plot_fit and fit_fct is not None
    do_plot_fit = do_plot_fit and get_state().d_fit_param
    if do_plot_fit:
        od_fit = fit_fct(points, get_state().d_fit_param)
        ax.plot(ab, od_fit, color='purple', linewidth=2, label='Fitted PSF')

    # Redraw
    log(8, "ProfileAnswer :", zip(points, get_state().image.im0[tuple(points)]))
    get_root().frame_fit.redraw()

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

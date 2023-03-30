#!/usr/bin/env python3

"""
Intensity profile drawer
along a user defined line

Profile line user shower, callback of a tool
"""

import numpy as np

from abism.back import image_function as IF
from abism.back.fit_template_function import get_fit_function
from abism.back.image_info import get_array_stat

from abism.front.answer_return import AnswerPrinter

from abism.util import get_state, get_root, log
from abism.answer import AnswerDistance, AnswerLuminosity


def show_profile(point1, point2):
    """ Callback for Profile Pick: 1 and 2D """
    # Get data to plot
    abscissa, ordinate, points = IF.get_radial_line(
        get_state().image.im0, (point1, point2), return_point=1)

    # Plot <- Reset
    axe = get_root().frame_fit.reset_figure_ax()

    # Data
    axe.plot(abscissa, ordinate, color='black', drawstyle='steps', linestyle='--',
            linewidth=1, label="Data")

    # Fit
    fit_fct = get_fit_function()
    do_plot_fit = get_state().s_fit_type != "None"
    do_plot_fit = do_plot_fit and fit_fct is not None
    do_plot_fit = do_plot_fit and get_state().d_fit_param
    if do_plot_fit:
        try:
            od_fit = fit_fct(points, get_state().d_fit_param)
            axe.plot(
                abscissa,
                od_fit,
                color='purple',
                linewidth=2,
                label='Fitted PSF')
        # pylint: disable=broad-except
        except Exception as exc:
            log(3, 'Warning, plot_profile could not plot fit, error:', exc)

    # Redraw
    log(8, "ProfileAnswer :", zip(
        points, get_state().image.im0[tuple(points)]))
    axe.legend(loc=1, prop={'size': 8})
    get_root().frame_fit.redraw()

    # Get stat
    profile_stat = get_array_stat(get_state().image.im0[tuple(points)])
    # LEN
    tlen = np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    class StatPrinter(AnswerPrinter):
        """ Stat values printer: with answer type """

        def get_list(self):
            return [
                [AnswerDistance('Length', tlen, error=1)],
                [AnswerLuminosity('Min', profile_stat.min, error=profile_stat.rms), True],
                [AnswerLuminosity('Max', profile_stat.max, error=profile_stat.rms), True],
                [AnswerLuminosity('Mean', profile_stat.mean, error=np.sqrt(profile_stat.rms))],
                [AnswerLuminosity('Rms', profile_stat.rms)]
            ]

    def print_answer():
        StatPrinter().work(with_warning=False, on_coord=print_answer)
    print_answer()

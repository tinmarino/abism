"""
    Profile line user shower, callback of a tool
"""
import numpy as np

from abism.back import ImageFunction as IF
from abism.back.fit_template_function import get_fit_function
from abism.back.image_info import get_array_stat

from abism.front.AnswerReturn import AnswerPrinter

from abism.util import get_state, get_root, log
from abism.answer import AnswerDistance, AnswerLuminosity


def show_profile(point1, point2):
    """Callback for Profile Pick: 1 and 2D"""
    # Get data to plot
    ab, od, points = IF.get_radial_line(
        get_state().image.im0, (point1, point2), return_point=1)

    # Plot <- Reset
    ax = get_root().frame_fit.reset_figure_ax()

    # Data
    ax.plot(ab, od, color='black', drawstyle='steps', linestyle='--',
            linewidth=1, label="Data")

    # Fit
    fit_fct = get_fit_function()
    do_plot_fit = get_state().s_fit_type != "None"
    do_plot_fit = do_plot_fit and fit_fct is not None
    do_plot_fit = do_plot_fit and get_state().d_fit_param
    if do_plot_fit:
        try:
            od_fit = fit_fct(points, get_state().d_fit_param)
            ax.plot(ab, od_fit, color='purple', linewidth=2, label='Fitted PSF')
        except Exception as e:
            log(3, 'Warning, plot_profile could not plot fit, error:', e)

    # Redraw
    log(8, "ProfileAnswer :", zip(points, get_state().image.im0[tuple(points)]))
    ax.legend(loc=1, prop={'size': 8})
    get_root().frame_fit.redraw()


    # Get stat
    ps = get_array_stat(get_state().image.im0[tuple(points)])
    # LEN
    tlen = np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


    class StatPrinter(AnswerPrinter):
        """Stat values printer: with answer type"""
        def get_list(self):
            return [
                [AnswerDistance('Length', tlen, error=1)],
                [AnswerLuminosity('Min', ps.min, error=ps.rms), True],
                [AnswerLuminosity('Max', ps.max, error=ps.rms), True],
                [AnswerLuminosity('Mean', ps.mean, error=np.sqrt(ps.rms))],
                [AnswerLuminosity('Rms', ps.rms)]
            ]
    def print_answer():
        StatPrinter().work(with_warning=False, on_coord=print_answer)
    print_answer()

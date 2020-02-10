"""
    Statistic rectangle widget callback
"""
import numpy as np

from abism.back import ImageFunction as IF
from abism.back.image_info import get_array_stat
from abism.front.AnswerReturn import AnswerPrinter

from abism.util import get_state, log
from abism.answer import AnswerDistance, AnswerLuminosity, AnswerNum

def show_statistic(rectangle):
    """Get and Print statistics from a rectangle selection"""
    # Get stat <- subarray
    rectangle = IF.Order4(rectangle, intify=True)
    log(3, 'Stat on rectangle:', rectangle)
    sub_array = get_state().image.im0[
        rectangle[0]:rectangle[1], rectangle[2]:rectangle[3]]
    log(3, sub_array.shape)
    stat = get_array_stat(sub_array)
    i_sq_nb = np.sqrt(stat.number_count)

    class StatPrinter(AnswerPrinter):
        """Stat values printer: with answer type"""
        def get_list(self):
            return [
                [AnswerDistance('DimX', rectangle[1] - rectangle[0])],
                [AnswerDistance('DimY', rectangle[3] - rectangle[2])],
                [AnswerNum('Count', stat.number_count)],
                [AnswerLuminosity('Min', stat.min, error=stat.rms), True],
                [AnswerLuminosity('Max', stat.max, error=stat.rms), True],
                [AnswerLuminosity('Sum', stat.sum, error=stat.rms * i_sq_nb), True],
                [AnswerLuminosity('Mean', stat.mean, error=stat.rms / i_sq_nb), True],
                [AnswerLuminosity('Median', stat.median, error=stat.rms / i_sq_nb), True],
                [AnswerLuminosity('Rms', stat.rms)]
            ]
    def print_answer():
        StatPrinter().work(with_warning=False, on_coord=print_answer)
    print_answer()

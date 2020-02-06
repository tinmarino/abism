"""
    Statistic rectangle widget callback
"""
import tkinter as tk

from abism.back import ImageFunction as IF
from abism.back.image_info import get_array_stat

from abism.util import get_state, get_root, log

def show_statistic(rectangle):
    """Get and Print statistics from a rectangle selection"""
    # Get stat <- subarray
    rectangle = IF.Order4(rectangle)
    sub_array = get_state().image.im0[rectangle[0]:rectangle[1], rectangle[2]:rectangle[3]]
    dicr = get_array_stat(sub_array)

    # Clear answer frame
    get_root().frame_answer.clear()

    # Create text
    text = get_root().frame_answer.grid_text_answer()

    lst = [
        ["DIM X*DIM Y:\t", "%.1f x %.1f" %
         (abs(rectangle[0]-rectangle[1]), abs(rectangle[2]-rectangle[3]))],
        ["MIN:\t", "%.1f" % dicr["min"]],
        ["MAX:\t", "%.1f" % dicr["max"]],
        ["SUM:\t", "%.1f" % dicr["sum"]],
        ["MEAN:\t", "%.1f" % dicr["mean"]],
        ["MEDIAN:\t", "%.1f" % dicr["median"]],
        ["RMS:\t", "%.1f" % dicr["rms"]],
    ]

    stg = ''
    text.i_tab_len = 0
    for name, value in lst:
        log(0, name, value)
        stg += name + value + "\n"
        text.i_tab_len = max(len(name), text.i_tab_len)
    text.insert(tk.END, stg)

    # Disable edit
    text.configure(state=tk.DISABLED)

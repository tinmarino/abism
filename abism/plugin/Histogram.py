"""This is drawing the histogram of pixel values. It may be usefull.
Programmers, We can implement a selection of the scale cut of the image
with a dragging the vertical lines., with a binning of the image,
this could even be in real time.
"""

from abism.util import log
from abism.front.util_front import set_figure_skin
import abism.front.util_front as G


def Histopopo(figure, image_sorted, skin=None):
    """Single (useless) method for a single (useless) functionality
    figure: matplotlib figure
    image_sorted: 1D sorted array of pixel value
    """
    # Reset figure
    figure.clf()
    ax = figure.add_subplot(111)
    # Hide x, y label in toolbar
    ax.format_coord = lambda x, y: ''

    # Draw tick
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)
    ax.axvline(x=get_state().i_image_min_cut,
               linestyle='-', linewidth=2)
    ax.axvline(x=get_state().i_image_max_cut,
               linestyle='-', linewidth=2)
    ax.set_xticklabels(image_sorted)

    # Caclulate histogram
    ax.hist(image_sorted, 100, log=True)  # n, bin, patches

    # Set skin
    if skin:
        set_figure_skin(figure, skin)

    # Fraw
    figure.canvas.draw()

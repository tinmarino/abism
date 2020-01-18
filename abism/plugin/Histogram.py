"""This is drawing the histogram of pixel values. It may be usefull.
Programmers, We can implement a selection of the scale cut of the image
with a dragging the vertical lines., with a binning of the image,
this could even be in real time.
"""

from abism.util import log
import abism.front.util_front as G


def Histopopo(figure, image_sorted, fg='black'):
    """Single (useless) method for a single (useless) functionality
    figure: matplotlib figure
    image_sorted: 1D sorted array of pixel value
    """
    # Reset figure
    figure.clf()
    ax = figure.add_subplot(111)
    ax.format_coord = lambda x, y: ""  # not see x y label in the toolbar

    # Draw tick
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)
    ax.axvline(x=G.scale_dic[0]["min_cut"],
               color=fg, linestyle='-', linewidth=2)
    ax.axvline(x=G.scale_dic[0]["max_cut"],
               color=fg, linestyle='-', linewidth=2)
    ax.set_xticklabels(image_sorted)

    # Caclulate histogram
    ax.hist(image_sorted, 100, log=True)  # n, bin, patches

    # Fraw
    figure.canvas.draw()

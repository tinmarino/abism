#!/usr/bin/env python3

"""
This is drawing the histogram of pixel values. It may be usefull.
Programmers, We can implement a selection of the scale cut of the image
with a dragging the vertical lines., with a binning of the image,
this could even be in real time.
"""

from abism.util import get_state


def histopopo(figure, image_sorted):
    """Single (useless) method for a single (useless) functionality
    figure: matplotlib figure
    image_sorted: 1D sorted array of pixel value
    """
    # Reset figure
    figure.clf()
    axe = figure.add_subplot(111)
    # Hide x, y label in toolbar
    axe.format_coord = lambda x, y: ''

    # Draw tick
    for tick in axe.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)
    axe.axvline(x=get_state().i_image_min_cut,
               linestyle='-', linewidth=2)
    axe.axvline(x=get_state().i_image_max_cut,
               linestyle='-', linewidth=2)
    axe.set_xticklabels(image_sorted)

    # Calculate histogram
    axe.hist(image_sorted, 100, log=True)  # n, bin, patches

    # Fraw
    figure.canvas.draw()

"""This is drawing the histogram of pixel values. It may be usefull.
Programmers, We can implement a selection of the scale cut of the image
with a dragging the vertical lines., with a binning of the image,
this could even be in real time.
"""

import front.util_front as G
import back.util_back as W


def Histopopo():
    """Single (useless) method for a single (useless) functionality"""
    G.figfit.clf()
    G.ax2 = G.figfit.add_subplot(111)
    G.ax2.format_coord = lambda x, y: ""  # not see x y label in the toolbar

    for tick in G.ax2.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)
    G.ax2.axvline(x=G.scale_dic[0]["min_cut"],
                  color='black', linestyle='-', linewidth=2)
    G.ax2.axvline(x=G.scale_dic[0]["max_cut"],
                  color='black', linestyle='-', linewidth=2)
    G.ax2.set_xticklabels(W.sort)
    G.hist = G.ax2.hist(W.sort, 100, log=True)  # n, bin, patches

    G.figfit.canvas.draw()

"""
    Utilities for Abism GUI
"""

# Standard
from sys import exit as sys_exit

import WorkVariables as W

"""
    Read globalDefiner
"""

# Gui parent
parent = None

def Quit():
    """Kill process"""
    W.log(1, 'Closing Abism, Goodbye. Come back soon.' + "\n" + 100 * '_' + 3 * "\n")
    parent.destroy()
    sys_exit(1)


# if "DrawPaned" in G.geo_dic:
#     G.MainPaned.add(G.DrawPaned, width=float(G.geo_dic["DrawPaned"]))
# else:  # including don't set width
#     G.MainPaned.add(G.DrawPaned)
# G.all_frame.append("G.DrawPaned")

# TODO remove this
class VoidClass:
    """Helper container"""


"""
TODO this in shpinx

0 |  parent      | Tkinter.Tk | Is the main Window, it handles the main loop, all other things ar his children

1 |  MainPaned   |  Tk.PanedWindow  |  A paned Window enabling to resize btween left and right the (all but not menu) frame. See later.

2 |  DrawPaned   |   Tk.PanedWindow | Child of Main Paned, at the right side, serves for image and graph display, it is vertically divided.

2 | TextPaned   | Tk.PanedWindow |  on the left of MainPaned
2.5| TextFrame   | Tk.PanedWindow |  on the left of MainPaned

3 | ImageFrame   | Tk.Frame   | Child od DrawPaned, it is used to display the full image, to click on ....

3 | RightBottomPaned | Tk.PanedWindow | Child of DrawPaned, it is at the bottom and is horrizontally divided. It will contain the two last frames

3 | ButtonFrame  | Tk.Frame | Son of TextFrame,

3 | LabelFrame | | SOn of TextPaned

3 | leftTop | | son of TextPaned,

3 | LeftBottomFrame | | son of textPaned

4 | ResultLabelFrame - | son of leftBottomFrame

4 | Button1Frame | | with button exit, restart and staff

4 | FitFrame    | Tk.Frame   | Chile of RightBottomPaned, it is used to display the fit in one dimension, here I ca see the ADU of the star

5 | ResultFrame | Tk.Frame   | Even if it has a bad name, it is used, to see the star from above, I 2D, just like a zoom of the ImageFrame, on this graph, There is also the fitted image. Do both look the same ? If not, the result is wrong.

"""

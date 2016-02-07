from Tkinter import *

"""
    Read globalDefiner
"""
class GuiGlobals:
    # I mean these vars are local to the main tk loop, but as it is the main
    # loop, they are globzal to ABISM current runtime
    def __init__(self):
        self.parent =  instance  # This is the parent of everything. The first
#defined and the one doing the mainloop

# TODO remove this
class VoidClass:
    pass

"""

0 |  parent      | Tkinter.Tk | Is the main Window, it handles the main loop, all other things ar his children

1 |  MainPaned   |  Tk.PanedWindow  |  A paned Window enabling to resize btween left and right the (all but not menu) frame. See later.

2 |  DrawPaned   |   Tk.PanedWindow | Child of Main Paned, at the right side, serves for image and graph display, it is vertically divided.
2

3 | ImageFrame   | Tk.Frame   | Child od DrawPaned, it is used to display the full image, to click on ....

3 | RightBottomPaned | Tk.PanedWindow | Child of DrawPaned, it is at the bottom and is horrizontally divided. It will contain the two last frames

4 | FitFrame    | Tk.Frame   | Chile of RightBottomPaned, it is used to display the fit in one dimension, here I ca see the ADU of the star

5 | ResultFrame | Tk.Frame   | Even if it has a bad name, it is used, to see the star from above, I 2D, just like a zoom of the ImageFrame, on this graph, There is also the fitted image. Do both look the same ? If not, the result is wrong.

"""

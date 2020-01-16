"""
    The Tkinter Frame using matplotlib
"""

from tkinter import Frame

import GuyVariables as G

class Plot(Frame):
    """Base class"""
    def __init__(self, parent, **args):
        super().__init__(parent, **args)



class ImageFrame(Plot):
    """Frame with science image"""
    def __init__(self, parent):
        super().__init__(parent, bg=G.bg[0])

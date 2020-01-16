"""
    The Tkinter Frame using matplotlib
    TODO stop putting all in G
"""

from tkinter import Frame, PanedWindow, Label, \
    VERTICAL, HORIZONTAL

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas, \
    NavigationToolbar2Tk

import GuyVariables as G

class Plot(Frame):
    """Base class"""
    def __init__(self, parent, **args):
        super().__init__(parent, bg=G.bg[0], **args)
        # Helper auto add (can get confusing)
        parent.add(self)

        self._fig = None

    def get_figure(self):
        """Return the figure for a direct matplotlib use
        You should avoid that
        """
        return self._fig


class ImageFrame(Plot):
    """Frame with science image"""
    def __init__(self, parent):
        super().__init__(parent)

        self.rowconfigure(0, weight=100)
        self.rowconfigure(1, weight=1)  # not resize the toolbar
        self.columnconfigure(0, weight=1)  # not resize the toolbar

        # Create figure && Adjust size and color
        self._fig = Figure()
        self._fig.subplots_adjust(left=0.07, right=0.93, top=0.95, bottom=0.05)
        self._fig.set_facecolor(G.bg[0])

        # Create Canvas
        self._canvas = FigureCanvas(self._fig, master=self)
        self._canvas.get_tk_widget()['bg'] = G.bg[0]
        # to have no little border use to know if I have focus
        self._canvas.get_tk_widget()["highlightthickness"] = 0
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        # G.all_frame.append("G.ImageCanvas.get_tk_widget()")
        Label(self, text="Image", **G.frame_title_arg).place(x=0, y=0)

        ###########
        # TOOLBAR
        toolbar_frame = Frame(self)
        toolbar_frame.grid(row=1, column=0, sticky="nsew")
        self._toolbar = NavigationToolbar2Tk(self._canvas, toolbar_frame)
        # G.toolbar.grid(row=1,column=0,sticky="nsew")
        self._toolbar.pack()
        self._toolbar["bg"] = G.bg[0]
        for i in self._toolbar.winfo_children():
            i["bg"] = G.bg[0]

    def get_toolbar(self):
        """Getter for global"""
        return self._toolbar

    def get_canvas(self):
        """Getter for global"""
        return self._canvas


class FitFrame(Plot):
    """Frame with the curve of the fit (1d)"""
    def __init__(self, parent):
        super().__init__(parent)


class ResultFrame(Plot):
    """Frame with some results, dependant on operation"""
    def __init__(self, parent):
        super().__init__(parent)


class RightFrame(PanedWindow):
    """Full Container"""
    def __init__(self, parent):
        # Append self, vertically splited
        super().__init__(parent, orient=VERTICAL, **G.paned_dic)
        parent.add(self)

        # Add science image frame
        G.ImageFrame = ImageFrame(self)

        # Append bottom, horizontally splitted container of 2 frames
        G.RightBottomPaned = PanedWindow(
            self, orient=HORIZONTAL, **G.paned_dic)
        self.add(G.RightBottomPaned)

        # Add Fit (bottom left)
        G.FitFrame = FitFrame(G.RightBottomPaned)

        # Add Result (bottom right)
        G.ResultFrame = ResultFrame(G.RightBottomPaned)

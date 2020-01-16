"""
    The Tkinter Frame using matplotlib
    TODO stop putting all in G
"""

from tkinter import Frame, PanedWindow, Label, PhotoImage, Button, \
    VERTICAL, HORIZONTAL

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas, \
    NavigationToolbar2Tk

import GuyVariables as G


# TODO this should not be here
import WorkVariables as W

class Plot(Frame):
    """Base class"""
    def __init__(self, parent, **args):

        super().__init__(parent, bg=G.bg[0], **args)

        # Grid stuff
        self.rowconfigure(0, weight=100)
        self.rowconfigure(1, weight=1)  # not resize the toolbar
        self.columnconfigure(0, weight=1)  # not resize the toolbar

        # Helper auto add (can get confusing)
        parent.add(self)

        self._fig = None  # Figure
        self._arrow = None  # Button
        self._toolbar_frame = None  # Container for toolbar
        # See toolbar by default cause it is grided
        #   And in case no hide button, I see it (cf: Image)
        self._see_toolbar = True

    def init_canvas(self, fig):
        """Init canvas && Init toolbar inside
        Canvas requires _fig
        Toolbar requires canvas
        """
        self._canvas = FigureCanvas(fig, master=self)
        self._canvas.get_tk_widget()['bg'] = G.bg[0]
        # No borders: used to locate focus
        self._canvas.get_tk_widget()["highlightthickness"] = 0
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # TOOLBAR
        self._toolbar_frame = Frame(self)
        self._toolbar_frame.grid(row=1, column=0, sticky="nsew")
        self._toolbar = NavigationToolbar2Tk(self._canvas, self._toolbar_frame)
        self._toolbar["bg"] = G.bg[0]
        for i in self._toolbar.winfo_children():
            i["bg"] = G.bg[0]
        self._toolbar.grid(row=0, column=0, sticky="nsew")

    def init_label(self, s_label):
        """Create label bottom left"""
        Label(self, text=s_label, **G.frame_title_arg).place(x=0, y=0)

    def init_toolbar_button(self):
        """Create toolbar button"""
        photo_up = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
        self._arrow = Button(
            self, command=self.toogle_toolbar, image=photo_up, **G.bu_arg)
        self._arrow.image = photo_up  # Garbage safety
        self._arrow.place(relx=1., rely=1., anchor="se")
        self.toogle_toolbar()

    def toogle_toolbar(self):
        """Toogle toolbar visibility"""
        self._see_toolbar = not self._see_toolbar

        # CREATE
        if self._see_toolbar:
            W.log(3, "Showing toolbar")
            photo_down = PhotoImage(file=W.path + "/Icon/arrow_down.gif")
            self._arrow.configure(image=photo_down)
            self._arrow.image = photo_down  # Garbage safety
            self._toolbar_frame.grid(row=1, column=0, sticky="nsew")

        # DESTROY
        else:
            W.log(3, "Hidding toolbar")
            photo_up = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
            self._arrow.configure(image=photo_up)
            self._arrow.image = photo_up  # Garbage safety
            self._toolbar_frame.grid_forget()

    def get_figure(self):
        """Return the figure for a direct matplotlib use
        You should avoid that
        """
        return self._fig

    def get_canvas(self):
        """Getter for global"""
        return self._canvas

    def get_toolbar(self):
        """Getter for global"""
        return self._toolbar


class ImageFrame(Plot):
    """Frame with science image"""
    def __init__(self, parent):
        super().__init__(parent)

        # Create figure && Adjust size and color
        self._fig = Figure()
        self._fig.subplots_adjust(left=0.07, right=0.93, top=0.95, bottom=0.05)
        self._fig.set_facecolor(G.bg[0])

        # Label && Canvas
        self.init_label("Image")
        self.init_canvas(self._fig)


class FitFrame(Plot):
    """Frame with the curve of the fit (1d)"""
    def __init__(self, parent):
        super().__init__(parent)

        # Create figure && Adjust size and color
        self._fig = Figure(figsize=(5, 2.5))
        self._fig.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.2)
        self._fig.set_facecolor(G.bg[0])

        # Label && Canvas
        self.init_label("Photometric Profile")
        self.init_canvas(self._fig)
        self.init_toolbar_button()


class ResultFrame(Plot):
    """Frame with some results, dependant on operation"""
    def __init__(self, parent):
        super().__init__(parent)

        # Create figure && Adjust size and color
        self._fig = Figure(figsize=(3, 2.5))
        self._fig.subplots_adjust(left=0.1, right=0.9, top=1.05, bottom=-0.15)
        self._fig.set_facecolor(G.bg[0])

        # Label && Canvas
        self.init_label("2D Shape")
        self.init_canvas(self._fig)
        self.init_toolbar_button()


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

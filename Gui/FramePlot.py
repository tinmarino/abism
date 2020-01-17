"""
    The Tkinter Frame using matplotlib
    TODO stop putting all in G
"""

from tkinter import Frame, PanedWindow, Label, PhotoImage, Button, \
    StringVar, Entry, \
    VERTICAL, HORIZONTAL, TOP, X, CENTER

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas, \
    NavigationToolbar2Tk
from numpy import sqrt, float32

from ImageFunction import PixelMax
from DraggableColorbar import DraggableColorbar


import GuyVariables as G

# TODO this should not be here
import WorkVariables as W

class PlotFrame(Frame):
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
        self._toolbar = None
        self._canvas = None
        # See toolbar by default cause it is grided
        #   And in case no hide button, I see it (cf: Image)
        self._see_toolbar = True
        self._cbar = None  # ColorBar

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
        self._arrow = Button(
            self, command=self.toogle_toolbar, image=G.photo_up, **G.bu_arg)
        self._arrow.place(relx=1., rely=1., anchor="se")
        self.toogle_toolbar()

    def toogle_toolbar(self):
        """Toogle toolbar visibility"""
        self._see_toolbar = not self._see_toolbar

        # CREATE
        if self._see_toolbar:
            W.log(3, "Showing toolbar")
            self._arrow.configure(image=G.photo_down)
            self._toolbar_frame.grid(row=1, column=0, sticky="nsew")

        # DESTROY
        else:
            W.log(3, "Hidding toolbar")
            self._arrow.configure(image=G.photo_up)
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


class ImageFrame(PlotFrame):
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


    def draw_image(self, new_fits=True):
        """Init image
        From Work variable
        """
        # Reset
        try:
            self._cbar.disconnect()
            del self._cbar
            self._fig.clf()
        except BaseException:
            W.log(2, 'InitImage, cannot delete cbar')


        # Scale (much faster also draw_artist can help ?)
        import re
        from WindowRoot import Scale
        if re.match(r".*\.fits", W.image_name):
            G.current_image = W.Im0.astype(float32)
            W.log(3, "dic init", G.scale_dic[0])
            Scale(dic=G.scale_dic[0], load=1)  # not to draw the image.
        else:
            G.current_image = W.Im0

        # Display
        G.ax1 = self._fig.add_subplot(111)
        drawing = G.ax1.imshow(
            G.current_image,
            vmin=G.scale_dic[0]["min_cut"], vmax=G.scale_dic[0]["max_cut"],
            # orgin=lower to get low y down
            cmap=G.scale_dic[0]["cmap"], origin='lower')

        # Compass
        try:
            self.RemoveCompass()
        except BaseException:
            pass
        self.DrawCompass()

        # ColorBar && TooBar
        self._toolbar.update()
        self._cbar = G.fig.colorbar(drawing, pad=0.02)
        # TODO not here :
        G.cbar = self._cbar
        self._cbar = DraggableColorbar(self._cbar, drawing)
        self._cbar.connect()

        # Image levels
        def z(x, y):
            return W.Im0[y, x]

        def z_max(x, y):
            return PixelMax(W.Im0, r=(y - 10, y + 11, x - 10, x + 11))[1]

        def format_coordinate(x, y):
            x, y = int(x), int(y)
            return "zmax=%5d, z=%5d, x=%4d, y=%4d" % (z_max(x, y), z(x, y), x, y)

        # Head up display
        G.ax1.format_coord = format_coordinate

        # Draw
        self._fig.canvas.draw()

        #####################
        ###  SOME  CLICKS #
        #####################
        # TODO move me ::
        import Pick
        Pick.RefreshPick("one")  # assuming that the default PIck is setted yet

        # I don't know why I need to pu that at the end but it worls like that
        # # does not work it put in Science Variables
        if new_fits:
            G.label_bool = 0
            G.LabelFrame.update()


    def RemoveCompass(self):
        G.ax1.texts.remove(G.north)
        G.ax1.texts.remove(G.east)
        G.ax1.texts.remove(G.north_text)
        G.ax1.texts.remove(G.east_text)


    def DrawCompass(self):
        """Draw WCS compass to see 'north'"""
        if not (("CD1_1" in vars(W.head)) and ("CD2_2" in vars(W.head))):
            W.log(0, "WARNING WCS Matrix not detected,",
                  "I don't know where the north is")
            W.head.CD1_1 = W.head.pixel_scale * 3600
            W.head.CD2_2 = W.head.pixel_scale * 3600

        if not (("CD1_2" in vars(W.head)) and ("CD2_1" in vars(W.head))):
            W.head.CD1_2, W.head.CD2_1 = 0, 0

        north_direction = [-W.head.CD1_2, -W.head.CD1_1] / \
            sqrt(W.head.CD1_1**2 + W.head.CD1_2**2)
        east_direction = [-W.head.CD2_2, -W.head.CD2_1] / \
            sqrt(W.head.CD2_1**2 + W.head.CD2_2**2)

        # CALCULATE ARROW SIZE
        coord_type = "axes fraction"
        if coord_type == "axes fraction":    # for the arrow in the image, axes fraction
            arrow_center = [0.95, 0.1]  # in figura fraction
            # -  because y is upside down       think raw collumn
            north_point = arrow_center + north_direction / 10
            east_point = arrow_center + east_direction / 15

        # for the arrow IN the image coords can be "data" or "figure fraction"
        elif coord_type == "data":
            # in figure fraction
            arrow_center = [0.945 * len(W.Im0), 0.1 * len(W.Im0)]
            # -  because y is upside down       think raw collumn
            north_point = [arrow_center + north_direction / 20 * len(W.Im0),
                           arrow_center - north_direction / 20 * len(W.Im0)]
            east_point = [north_point[1] + east_direction / 20 * len(W.Im0),
                          north_point[1]]
        W.north_direction = north_direction
        W.east_direction = east_direction
        W.log(3, "north", north_point, east_point,
              arrow_center, north_direction, east_direction)

        #################
        # 2/ DRAW        0 is the end of the arrow
        if W.head.wcs is not None:
            G.north = G.ax1.annotate(
                "",
                # we invert to get the text at the end of the arrwo
                xy=arrow_center, xycoords=coord_type,
                xytext=north_point, textcoords=coord_type, color="purple",
                arrowprops=dict(
                    arrowstyle="<-", facecolor="purple", edgecolor="purple"),
                # connectionstyle="arc3"),
                )
            G.east = G.ax1.annotate(
                "",
                xy=arrow_center, xycoords=coord_type,
                xytext=east_point, textcoords=coord_type, color="red",
                arrowprops=dict(
                    arrowstyle="<-", facecolor='red', edgecolor='red'),
                # connectionstyle="arc3"),
                )
            G.north_text = G.ax1.annotate(
                'N', xytext=north_point,
                xy=north_point, textcoords=coord_type, color='purple')
            G.east_text = G.ax1.annotate(
                'E', xytext=east_point,
                xy=east_point, textcoords=coord_type, color='red')


    def Cube(self):
        """Prepare Cube buttons"""
        if not W.cube_bool:
            try:
                G.CubeFrame.destroy()
            except BaseException:
                pass
        else:
            # FRAME
            G.CubeFrame = Frame(G.ButtonFrame, **G.fr_arg)
            G.CubeFrame.pack(side=TOP, expand=0, fill=X)

            # CUBE IMAGE SELECTION
            # LEFT
            G.bu_cubel = Button(G.CubeFrame, text='<-',
                                command=lambda: self.CubeDisplay("-"), **G.bu_arg)

            # ENTRY
            G.cube_var = StringVar()
            G.cube_entry = Entry(
                G.CubeFrame, width=10, justify=CENTER,
                textvariable=G.cube_var, **G.en_arg)
            G.cube_var.set(W.cube_num + 1)
            G.cube_entry.bind("<Return>", lambda x: self.CubeDisplay("0"))

            # RIGHT
            G.bu_cuber = Button(
                G.CubeFrame, text='->',
                command=lambda: self.CubeDisplay("+"), **G.bu_arg)

            # GRID
            for i in range(3):
                G.CubeFrame.columnconfigure(i, weight=1)
            Label(G.CubeFrame, text="Cube Number", **
                  G.frame_title_arg).grid(row=0, column=0, columnspan=3, sticky="w")
            G.bu_cubel.grid(row=1, column=0, sticky="nsew")
            G.cube_entry.grid(row=1, column=1, sticky="nsew")
            G.bu_cuber.grid(row=1, column=2, sticky="nsew")


    def CubeDisplay(self, stg_click):
        """Callback for cube button + -"""
        if stg_click == '+':
            W.cube_num += 1
        elif stg_click == '-':
            W.cube_num -= 1
        elif stg_click == '0':
            W.cube_num = float(G.cube_var.get())

        G.cube_var.set(W.cube_num + 1)
        self.draw_image(new_fits=False)






class FitFrame(PlotFrame):
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


class ResultFrame(PlotFrame):
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

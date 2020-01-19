"""
    The Tkinter Frame using matplotlib
    TODO stop putting all in G
"""
import re

import tkinter as tk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas, \
    NavigationToolbar2Tk
from numpy import sqrt, float32

# Local
from abism.back import  Scale  # otherwise get in conflict with Tkinter
from abism.front.DraggableColorbar import DraggableColorbar, zoom_fun
from abism.front.util_front import photo_up, photo_down, skin, TitleLabel, \
    set_figure_skin
import abism.front.util_front as G

# TODO must be remooved
from abism.front import Pick
# TODO this should not be here
from abism.back.ImageFunction import PixelMax
import abism.back.util_back as W
from abism.front.AnswerReturn import PlotStar2
from abism.front.DraggableColorbar import MyNormalize

from abism.util import log, get_root

class PlotFrame(tk.Frame):
    """Frame with a mpl figure"""
    def __init__(self, parent):
        super().__init__(parent, skin().frame_dic)

        # Grid stuff
        self.rowconfigure(0, weight=100)
        self.rowconfigure(1, weight=1)  # not resize the toolbar
        self.columnconfigure(0, weight=1)  # not resize the toolbar

        # Helper auto add (can get confusing)
        parent.add(self)

        self._fig = None  # Figure
        self._arrow = None  # Button
        # At bottom
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
        # Figure
        fig.set_facecolor(skin().color.bg)

        self._canvas = FigureCanvas(fig, master=self)
        self._canvas.get_tk_widget()['bg'] = skin().color.bg
        # No borders: used to locate focus
        self._canvas.get_tk_widget()["highlightthickness"] = 0
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # TOOLBAR
        self._toolbar_frame = tk.Frame(self, **skin().frame_dic)
        self._toolbar_frame.grid(row=1, column=0, sticky="nsew")
        self._toolbar = NavigationToolbar2Tk(self._canvas, self._toolbar_frame)
        self._toolbar["bg"] = skin().color.bg
        for i in self._toolbar.winfo_children():
            i["bg"] = skin().color.bg
        self._toolbar.grid(row=0, column=0, sticky="nsew")

    def init_label(self, s_label):
        """Create label bottom left"""
        TitleLabel(self, text=s_label).place(x=0, y=0)

    def init_toolbar_button(self):
        """Create toolbar button"""
        self._arrow = tk.Button(
            self, command=self.toogle_toolbar, image=photo_up(), **skin().button_dic)
        self._arrow.place(relx=1., rely=1., anchor="se")
        self.toogle_toolbar()

    def toogle_toolbar(self):
        """Toogle toolbar visibility"""
        self._see_toolbar = not self._see_toolbar

        # CREATE
        if self._see_toolbar:
            log(3, "Showing toolbar")
            self._arrow.configure(image=photo_down())
            self._toolbar_frame.grid(row=1, column=0, sticky="nsew")

        # DESTROY
        else:
            log(3, "Hidding toolbar")
            self._arrow.configure(image=photo_up())
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

    def update_skin(self):
        """Update skin, appearance"""
        # Update parameters
        set_figure_skin(self._fig, skin())

        # Redraw
        self._fig.canvas.draw()

    def reset_figure_ax(
            self,
            format_coord=lambda x, y: '',
            xlabel='', ylabel='',
    ):
        """Reset figure, return ax
        format_coord: fct x,y -> format
        """
        self._fig.clf()
        ax = self._fig.add_subplot(111)
        ax.format_coord = format_coord
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        return ax


class ImageFrame(PlotFrame):
    """Frame with science image"""
    def __init__(self, parent):
        super().__init__(parent)

        # Create figure && Adjust size and color
        self._fig = Figure()
        self._fig.subplots_adjust(left=0.07, right=0.93, top=0.95, bottom=0.05)

        # Label && Canvas
        self.init_label("Image")
        self.init_canvas(self._fig)


    def set_figure_scrollable(self):
        """Enable scroll with mouse"""
        def zoom_handler(event):
            zoom_fun(event, G.ax1, self._fig.canvas.draw, base_scale=1.2)

        self._fig.canvas.mpl_connect('scroll_event', zoom_handler)


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
            log(2, 'InitImage, cannot delete cbar')


        # Scale (much faster also draw_artist can help ?)
        if re.match(r".*\.fits", get_root().image.name):
            im0 = get_root().image.im0.astype(float32)
            log(3, "dic init", G.scale_dic[0])
            self.CutImageScale(dic=G.scale_dic[0], load=1)  # not to draw the image.
        else:
            im0 = get_root().image.im0

        # Display
        G.ax1 = self._fig.add_subplot(111)
        drawing = G.ax1.imshow(
            im0,
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
        self._cbar = DraggableColorbar(self._cbar, drawing, self.Draw)
        self._cbar.connect()

        # Image levels
        def z(x, y):
            return get_root().image.im0[y, x]

        def z_max(x, y):
            return PixelMax(get_root().image.im0, r=(y - 10, y + 11, x - 10, x + 11))[1]

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
        Pick.RefreshPick("one")  # assuming that the default PIck is setted yet

        # I don't know why I need to pu that at the end but it worls like that
        # # does not work it put in Science Variables
        if new_fits:
            G.label_bool = 0
            G.LabelFrame.update_label()

        self.set_figure_scrollable()


    def CutImageScale(self, dic={}, load=0, run=""):
        """Cut Image Scale
        Change contrast and color , load if it is loaded with InitImage
        remember that we need to update G.scael_dic in case we opne a new image,
        but this is not really true

        cmap: Image Color
            A menu button will be displayed and in this,
            there is waht is called some radio buttons,
            which permits to select a color for the image.
            And there is at the bottom a button for plotting the contours of objects.
            You have for colors from bright to faint:\n\n"
            ->jet: red,yellow,green,blue\n"
            ->Black&White: White,Black\n"
            ->spectral:red,yellow,green,blue, purple\n"
            ->RdYlBu: blue, white, red\n"
            ->BuPu: purple, white\n"
            ->Contour: This will display the 3 and 5 sigma contours of the objects
                on the image. To delete the contours that may crowd your image,
                just click again on contour.\n"

        fct: Rescale Image Function
            A menu button with some radio button is displayed. Chose the function
            that will transforme the image according to a function. This function
            is apllied to the images values rescaled from 0 to 1 and then the image
            is mutliplied again fit the true min and max cut made.\n\n"
            Programmers, This function is trabsforming G.current_image when the
            true image is stocked under get_root().image.im0 \nIf you want to add some function
            look at the InitGuy.py module, a function with some (2,3,4) thresholds
            (=steps) could be usefull to get stars of (2,3,4) differents color,
            nothing more, one color for each intensity range. This can be done with
            if also.

        scale_cut_type: Cut Image Scale
            A menu button with some radio button is displayed. You need to chose
            the cut for scaling the displaued color of the image (ie: the values of
            the minimum and maximum color). Youhave different way of cutting :\n\n"
            -> None, will take the true max and min values of th image to set the
            displayed color range. Usefull for saturated objects.\n" -> Percentage,
            set the max (min) color as the maximum (minimum) value of the central
            percent% values. For example, 95% reject the 2.5% higher values and
            then take the maximum of the kept values.\n" -> RMS, will take make a
            -1,5 sigma for min and max\n" -> Manual, The power is in your hand, a
            new frame is displayed, enter the min and max value. When satified,
            please close the frame.\n" \n\nProgrammers, a cut setted with the
            histogram can be nice but not so usefull.
        """
        log(2, "Scale called with:", dic)

        # RUN THE Stff to change radio button for mac
        if run != "":
            log(3, "Scale, run=", run)
            exec(run, globals())

            #######
            # INIT  WITH CURRENT IMAGE parameters.
        # try :
        if not load:
            G.scale_dic[0]["cmap"] = self._cbar.mappable.get_cmap().name  # Image color
            G.scale_dic[0]["min_cut"] = self._cbar.cbar.norm.vmin  # Image color
            G.scale_dic[0]["max_cut"] = self._cbar.cbar.norm.vmax  # Image color

        ###########
        # CONTOURS
        if("contour" in dic) and not isinstance(dic["contour"], bool):
            log(3, "contour ? ", G.scale_dic[0]["contour"])
            G.scale_dic[0]["contour"] = not G.scale_dic[0]["contour"]
            if G.scale_dic[0]["contour"]:
                if "median" not in G.scale_dic[0]:
                    tmp = vars(W.imstat)
                mean, rms = tmp["mean"], tmp["rms"]
                c0, c1, c2, c3, c4, c5 = mean, mean + rms, mean + 2 * \
                    rms, mean + 3 * rms, mean + 4 * rms, mean + 5 * rms
                G.contour = G.ax1.contour(get_root().image.im0, (c2, c5),
                                        origin='lower', colors="k",
                                        linewidths=3)
                # extent=(-3,3,-2,2))
                log(0, "---> Contour of 3 and 5 sigma, "
                    "clik again on contour to delete its.")

            else:  # include no contour  delete the contours
                if not load:
                    for coll in G.contour.collections:
                        G.ax1.collections.remove(coll)

        ############
        # UPDATE UPDATE
        log(2, " MG.scale ,Scale_dic ", G.scale_dic[0])
        dic["contour"] = G.scale_dic[0]["contour"]
        G.scale_dic[0].update(dic)  # UPDATE DIC

        ###########
        # CUT
        if "scale_cut_type" in dic:
            if dic["scale_cut_type"] == "None":
                # IG.ManualCut()
                G.scale_dic[0]["min_cut"] = W.imstat.min
                G.scale_dic[0]["max_cut"] = W.imstat.max
            else:
                dictmp = {"whole_image": "useless"}
                dictmp.update(G.scale_dic[0])
                tmp = Scale.MinMaxCut(get_root().image.im0, dic=dictmp)
                G.scale_dic[0]["min_cut"] = tmp["min_cut"]
                G.scale_dic[0]["max_cut"] = tmp["max_cut"]
            log(2, "I called Scale cut ")

        ######
        # SCALE FCT
        if "stretch" not in G.scale_dic[0]:  # in case
            G.scale_dic[0]["stretch"] = "linear"

        ###############
        #  RELOAD THE IMAGE
        # TODO
        if not load:
            self.Draw()

        ##########
        # RELOAD PlotStar
            try:
                PlotStar2()
            except BaseException:
                pass  # in case you didn't pick the star yet
        return


    def Draw(self, min=None, max=None, cmap=None, norm=False, cbar=True):
        """ Redraw image with new scale"""
        if min is not None:
            G.scale_dic[0]["min_cut"] = min
            G.scale_dic[0]["max_cut"] = max
        if cmap is not None:
            G.scale_dic[0]["cmap"] = cmap

        cmap = G.scale_dic[0]["cmap"]
        min, max = G.scale_dic[0]["min_cut"], G.scale_dic[0]["max_cut"]

        mynorm = MyNormalize(
            vmin=min, vmax=max, stretch=G.scale_dic[0]["stretch"], vmid=min - 5)
        G.ImageFrame._cbar.mappable.set_cmap(cmap)
        G.ImageFrame._cbar.mappable.set_norm(mynorm)

        G.ImageFrame._cbar.cbar.patch.figure.canvas.draw()
        G.ImageFrame.get_canvas().draw()

        try:
            for i in (G.figresult_mappable1, G.figresult_mappable2):
                i.set_norm(mynorm)
                i.set_cmap(cmap)
            G.figresult.canvas.draw()
        except BaseException:
            log(2, "Draw cannot draw in figresult")



    def RemoveCompass(self):
        G.ax1.texts.remove(G.north)
        G.ax1.texts.remove(G.east)
        G.ax1.texts.remove(G.north_text)
        G.ax1.texts.remove(G.east_text)


    def DrawCompass(self):
        """Draw WCS compass to see 'north'"""
        if not (("CD1_1" in vars(get_root().header)) and ("CD2_2" in vars(get_root().header))):
            log(0, "WARNING WCS Matrix not detected,",
                  "I don't know where the north is")
            get_root().header.CD1_1 = get_root().header.pixel_scale * 3600
            get_root().header.CD2_2 = get_root().header.pixel_scale * 3600

        if not (("CD1_2" in vars(get_root().header)) and ("CD2_1" in vars(get_root().header))):
            get_root().header.CD1_2, get_root().header.CD2_1 = 0, 0

        north_direction = [-get_root().header.CD1_2, -get_root().header.CD1_1] / \
            sqrt(get_root().header.CD1_1**2 + get_root().header.CD1_2**2)
        east_direction = [-get_root().header.CD2_2, -get_root().header.CD2_1] / \
            sqrt(get_root().header.CD2_1**2 + get_root().header.CD2_2**2)

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
            arrow_center = [0.945 * len(get_root().image.im0), 0.1 * len(get_root().image.im0)]
            # -  because y is upside down       think raw collumn
            north_point = [arrow_center + north_direction / 20 * len(get_root().image.im0),
                           arrow_center - north_direction / 20 * len(get_root().image.im0)]
            east_point = [north_point[1] + east_direction / 20 * len(get_root().image.im0),
                          north_point[1]]
        W.north_direction = north_direction
        W.east_direction = east_direction
        log(3, "north", north_point, east_point,
              arrow_center, north_direction, east_direction)

        #################
        # 2/ DRAW        0 is the end of the arrow
        if get_root().header.wcs is not None:
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
        # Try to destroy if not a cube
        if not get_root().image.is_cube:
            try:
                G.CubeFrame.destroy()
            except BaseException:
                pass
        # Create a cube interface else
        else:
            # FRAME
            G.CubeFrame = tk.Frame(G.ButtonFrame, **skin().frame_dic)
            G.CubeFrame.pack(side=tk.TOP, expand=0, fill=tk.X)

            # CUBE IMAGE SELECTION
            # LEFT
            G.bu_cubel = tk.Button(G.CubeFrame, text='<-',
                                command=lambda: self.CubeDisplay("-"), **skin().button_dic)

            # ENTRY
            G.cube_var = tk.StringVar()
            G.cube_entry = tk.Entry(
                G.CubeFrame, width=10, justify=tk.CENTER,
                textvariable=G.cube_var, bd=0, **skin().fg_and_bg)
            G.cube_var.set(get_root().image.cube_num + 1)
            G.cube_entry.bind("<Return>", lambda x: self.CubeDisplay("0"))

            # RIGHT
            G.bu_cuber = tk.Button(
                G.CubeFrame, text='->',
                command=lambda: self.CubeDisplay("+"), **skin().button_dic)

            # GRID
            for i in range(3):
                G.CubeFrame.columnconfigure(i, weight=1)
            lt = TitleLabel(G.CubeFrame, text="Cube Number")
            lt.grid(row=0, column=0, columnspan=3, sticky="w")
            G.bu_cubel.grid(row=1, column=0, sticky="nsew")
            G.cube_entry.grid(row=1, column=1, sticky="nsew")
            G.bu_cuber.grid(row=1, column=2, sticky="nsew")


    def CubeDisplay(self, stg_click):
        """Callback for cube button + -"""
        if stg_click == '+':
            get_root().image.cube_num += 1
        elif stg_click == '-':
            get_root().image.cube_num -= 1
        elif stg_click == '0':
            get_root().image.cube_num = float(G.cube_var.get())

        G.cube_var.set(get_root().image.cube_num + 1)
        self.draw_image(new_fits=False)


class FitFrame(PlotFrame):
    """Frame with the curve of the fit (1d)"""
    def __init__(self, parent):
        super().__init__(parent)

        # Create figure && Adjust size and color
        self._fig = Figure(figsize=(5, 2.5))
        self._fig.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.2)

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

        # Label && Canvas
        self.init_label("2D Shape")
        self.init_canvas(self._fig)
        self.init_toolbar_button()


class RightFrame(tk.PanedWindow):
    """Full Container"""
    def __init__(self, root, parent):
        # Append self, vertically splited
        super().__init__(parent, orient=tk.VERTICAL, **skin().paned_dic)
        parent.add(self)

        # Add science image frame
        root.ImageFrame = ImageFrame(self)

        # Append bottom, horizontally splitted container of 2 frames
        G.RightBottomPaned = tk.PanedWindow(
            self, orient=tk.HORIZONTAL, **skin().paned_dic)
        self.add(G.RightBottomPaned)

        # Add Fit (bottom left)
        root.FitFrame = FitFrame(G.RightBottomPaned)

        # Add Result (bottom right)
        root.ResultFrame = ResultFrame(G.RightBottomPaned)

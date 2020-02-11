"""
    The Tkinter Frame using matplotlib
    The right part of the gui with plots
"""
# Module
import tkinter as tk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas, \
    NavigationToolbar2Tk
from numpy import sqrt, float32

# Front
from abism.front.matplotlib_extension import (
    DraggableColorbar, MyNormalize, zoom_handler, center_handler)
from abism.front.util_front import photo_up, photo_down
import abism.front.tk_extension as tk_ext
import abism.front.util_front as G

# Back
from abism.back.ImageFunction import PixelMax

from abism.util import log, get_root, get_state


class RightFrame(tk.PanedWindow):
    """Full Container"""
    def __init__(self, root, parent, width, height):
        # Save self
        root.paned_image = self

        # Append self, vertically splited
        super().__init__(parent, orient=tk.VERTICAL)

        # Add science image frame
        root.frame_image = ImageFrame(self)
        self.add(root.frame_image, height=height)

        # Append bottom && Save
        paned = tk.PanedWindow(
            self, orient=tk.HORIZONTAL)
        self.add(paned)
        root.paned_bottom = paned

        # Add Fit (bottom left)
        root.frame_fit = FitFrame(paned)
        width_half = int(width / 2)
        paned.add(root.frame_fit, width=width_half)

        # Add Result (bottom right)
        root.frame_result = ResultFrame(paned)
        root.paned_bottom.add(root.frame_result)


class PlotFrame(tk.Frame):
    """Frame with a mpl figure"""
    def __init__(self, parent):
        super().__init__(parent)

        # Grid stuff
        self.rowconfigure(0, weight=100)
        self.rowconfigure(1, weight=1)  # not resize the toolbar
        self.columnconfigure(0, weight=1)  # not resize the toolbar

        self._fig = None  # Figure
        self._arrow = None  # Button
        self._l_cid = []  # mpl callback ids (to disconnect)
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
        fig.set_facecolor(tk_ext.scheme.bg)

        self._canvas = FigureCanvas(fig, master=self)
        self._canvas.get_tk_widget()['bg'] = tk_ext.scheme.bg
        # No borders: used to locate focus
        self._canvas.get_tk_widget()["highlightthickness"] = 0
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # TOOLBAR
        self._toolbar_frame = tk.Frame(self)
        self._toolbar_frame.grid(row=1, column=0, sticky="nsew")
        self._toolbar = NavigationToolbar2Tk(self._canvas, self._toolbar_frame)
        self._toolbar["bg"] = tk_ext.scheme.bg
        for i in self._toolbar.winfo_children():
            i["bg"] = tk_ext.scheme.bg
        self._toolbar.grid(row=0, column=0, sticky="nsew")

    def init_label(self, s_label):
        """Create label bottom left"""
        tk_ext.TitleLabel(self, text=s_label).place(x=0, y=0)

    def init_toolbar_button(self):
        """Create toolbar button"""
        self._arrow = tk.Button(
            self, command=self.toogle_toolbar, image=photo_up())
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

    def is_toolbar_active(self):
        # pylint: disable = protected-access
        return self._toolbar._active in ('PAN', 'ZOOM')

    def redraw(self):
        self.set_figure_skin()
        self._fig.canvas.draw()

    def extend_matplotlib(self):
        """Enable scroll with mouse"""
        def get_event_ax(event, axes):
            for ax in axes:
                if event.inaxes == ax:
                    return ax
            return None

        # Scroll
        def zoom_handler_wrapper(event):
            zoom_handler(
                event, get_event_ax(event, self._fig.axes),
                self._fig.canvas.draw, base_scale=1.2)

        # Click
        def center_handler_wrapper(event):
            log(9, 'MPL, detected a click', event)
            if event.button == 3:
                log(5, 'Centering <- right click:', event)
                center_handler(
                    event, get_event_ax(event, self._fig.axes),
                    callback=self._fig.canvas.draw)

        # Diconnect && Connect
        for cid in self._l_cid:
            self._fig.canvas.mpl_disconnect(cid)
        self._l_cid = []
        self._l_cid.append(
            self._fig.canvas.mpl_connect('scroll_event', zoom_handler_wrapper))
        self._l_cid.append(
            self._fig.canvas.mpl_connect('button_press_event', center_handler_wrapper))

    def reset_figure(self):
        self._fig.clf()
        self.extend_matplotlib()
        return self._fig

    def reset_figure_ax(
            self,
            format_coord=lambda x, y: '',
            xlabel='', ylabel='',
    ):
        """Reset figure, return ax
        format_coord: fct x,y -> format
        """
        self.reset_figure()
        ax = self._fig.add_subplot(111)
        ax.format_coord = format_coord
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        return ax


class ImageFrame(PlotFrame):
    """Frame with science image"""
    def __init__(self, parent):
        super().__init__(parent)
        # Keep contours to remove them
        self.contours = None
        self.bad_pixels = None

        # Create figure && Adjust size and color
        self._fig = Figure()
        self._fig.subplots_adjust(left=0.07, right=0.93, top=0.95, bottom=0.05)

        # Label && Canvas
        self.init_label("Image")
        self.init_canvas(self._fig)

        self.north_direction = [0, 0]
        self.east_direction = [0, 0]


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
            log(5, 'InitImage, cannot delete cbar')

        # Create axes
        ax = self._fig.add_subplot(111)

        # Get image arry
        im0 = get_state().image.im0.astype(float32)

        # Display
        drawing = ax.imshow(
            im0,
            vmin=get_state().i_image_min_cut,
            vmax=get_state().i_image_max_cut,
            cmap=get_state().s_image_color_map,
            # orgin=lower to get low y down
            origin='lower')

        # Compass
        try:
            self.RemoveCompass()
        except BaseException:
            pass
        self.DrawCompass()

        # ColorBar && TooBar
        self._toolbar.update()
        self._cbar = self._fig.colorbar(drawing, pad=0.02)
        self._cbar = DraggableColorbar(self._cbar, drawing, self.refresh_image)
        self._cbar.connect()

        # Image levels
        def z(x, y):
            try:
                res = im0[y, x]
            except IndexError:
                res = 0
            return res

        def z_max(x, y):
            return PixelMax(im0, r=(y - 10, y + 11, x - 10, x + 11))[1]

        def format_coordinate(x, y):
            x, y = int(x), int(y)
            return "x=%4d, y=%4d, zmax=%5d, z=%5d" % (x, y, z_max(x, y), z(x, y))

        # Head up display
        ax.format_coord = format_coordinate

        # Cut
        i_min, i_max = get_state().image.get_cut_minmax()
        get_state().i_image_min_cut = i_min
        get_state().i_image_max_cut = i_max

        # I don't know why I need to pu that at the end but it worls like that
        # # does not work it put in Science Variables
        if new_fits:
            # Draw
            self.refresh_image()
            get_root().frame_label.update_label()

        self.extend_matplotlib()


    def add_contour(self):
        im_stat = get_state().image.get_stat()
        mean, rms = im_stat.mean, im_stat.rms

        # Get contour 2 and 5 rms
        sigmas = [1, 2, 4, 8, 16, 32]

        im0 = get_state().image.im0.astype(float32)
        self.contours = self._fig.axes[0].contour(
            im0, [mean + i * rms for i in sigmas],
            origin='lower', cmap='plasma_r',
            linewidths=1)

        for level_id, level in enumerate(self.contours.collections):
            for kp, path in reversed(list(enumerate(level.get_paths()))):
                # go in reversed order due to deletions!
                # (N,2)-shape array of contour line coordinates
                verts = path.vertices
                diameter = np.min(verts.max(axis=0) - verts.min(axis=0))
                max_diameter = 2
                if level_id == 0: max_diameter = 10
                if diameter < max_diameter:
                    del level.get_paths()[kp]

        log(0, "---> Contour of 3 and 5 sigma, "
            "clik again on contour to delete its.")

    def remove_contour(self):
        if self.contours is None: return
        for coll in self.contours.collections:
            coll.remove()
        self.contours = None


    def add_bpm(self):
        # Get points to plot
        if get_state().image.bpm is None:
            get_state().image.create_bad_pixel_mask()
        points_bpm = np.argwhere(get_state().image.bpm)
        if len(points_bpm) == 0:
            log(0, 'No bad pixels on your detector!')
            return
        Y, X = points_bpm[:, 0], points_bpm[:, 1]

        # Plot "scatter plot"
        self.bad_pixels = self._fig.axes[0].scatter(
            X, Y, c='r', marker="s")


    def remove_bpm(self):
        if self.bad_pixels is None: return
        self.bad_pixels.remove()
        self.bad_pixels = None


    def refresh_image(self):
        """Redraw image with new scale"""

        cmap = get_state().s_image_color_map
        i_min, i_max = get_state().i_image_min_cut, get_state().i_image_max_cut

        # Contours
        self.remove_contour()
        if get_state().b_image_contour:
            self.add_contour()

        # Bad pixel map
        self.remove_bpm()
        if get_state().b_image_bpm:
            self.add_bpm()

        # Normalize
        mynorm = MyNormalize(
            vmin=i_min, vmax=i_max,
            vmid=i_min-5,
            stretch=get_state().s_image_stretch)

        self._cbar.mappable.set_cmap(cmap)
        self._cbar.mappable.set_norm(mynorm)

        self._cbar.cbar.patch.figure.canvas.draw()
        self.redraw()

        # Try to draw result frame
        try:
            for ax in get_root().frame_result.get_figure().axes:
                if not ax.images: continue
                mappable = ax.images[0]
                mappable.set_norm(mynorm)
                mappable.set_cmap(cmap)
            get_root().frame_result.redraw()
        except BaseException as e:
            log(2, "Draw cannot draw in Result Figure (bottom right):", e)


    def RemoveCompass(self):
        ax = self._fig.axes[0]
        ax.texts.remove(G.north)
        ax.texts.remove(G.east)
        ax.texts.remove(G.north_text)
        ax.texts.remove(G.east_text)


    def DrawCompass(self):
        """Draw WCS compass to see 'north'"""
        ax = self._fig.axes[0]
        im0 = get_state().image.im0.astype(float32)

        if not (("CD1_1" in vars(get_root().header)) and ("CD2_2" in vars(get_root().header))):
            log(0, "WARNING WCS Matrix not detected,",
                "I don't know where the north is")
            get_root().header.CD1_1 = get_root().header.pixel_scale * 3600
            get_root().header.CD2_2 = get_root().header.pixel_scale * 3600

        if not (("CD1_2" in vars(get_root().header)) and ("CD2_1" in vars(get_root().header))):
            get_root().header.CD1_2, get_root().header.CD2_1 = 0, 0

        self.north_direction = [-get_root().header.CD1_2, -get_root().header.CD1_1] / \
            sqrt(get_root().header.CD1_1**2 + get_root().header.CD1_2**2)
        self.east_direction = [-get_root().header.CD2_2, -get_root().header.CD2_1] / \
            sqrt(get_root().header.CD2_1**2 + get_root().header.CD2_2**2)

        # CALCULATE ARROW SIZE
        coord_type = "axes fraction"
        if coord_type == "axes fraction":    # for the arrow in the image, axes fraction
            arrow_center = [0.95, 0.1]  # in figura fraction
            # -  because y is upside down       think raw collumn
            north_point = arrow_center + self.north_direction / 10
            east_point = arrow_center + self.east_direction / 15

        # for the arrow IN the image coords can be "data" or "figure fraction"
        elif coord_type == "data":
            # in figure fraction
            arrow_center = [0.945 * len(im0), 0.1 * len(im0)]
            # -  because y is upside down       think raw collumn
            north_point = [arrow_center + self.north_direction / 20 * len(im0),
                           arrow_center - self.north_direction / 20 * len(im0)]
            east_point = [north_point[1] + self.east_direction / 20 * len(im0),
                          north_point[1]]
        log(3, "north", north_point, east_point,
            arrow_center, self.north_direction, self.east_direction)

        #################
        # 2/ DRAW        0 is the end of the arrow
        if get_root().header.wcs is not None:
            G.north = ax.annotate(
                "",
                # we invert to get the text at the end of the arrwo
                xy=arrow_center, xycoords=coord_type,
                xytext=north_point, textcoords=coord_type, color="purple",
                arrowprops=dict(
                    arrowstyle="<-", facecolor="purple", edgecolor="purple"),
                # connectionstyle="arc3"),
                )
            G.east = ax.annotate(
                "",
                xy=arrow_center, xycoords=coord_type,
                xytext=east_point, textcoords=coord_type, color="red",
                arrowprops=dict(
                    arrowstyle="<-", facecolor='red', edgecolor='red'),
                # connectionstyle="arc3"),
                )
            G.north_text = ax.annotate(
                'N', xytext=north_point,
                xy=north_point, textcoords=coord_type, color='purple')
            G.east_text = ax.annotate(
                'E', xytext=east_point,
                xy=east_point, textcoords=coord_type, color='red')


class FitFrame(PlotFrame):
    """Frame with the curve of the fit (1d)"""
    def __init__(self, parent):
        super().__init__(parent)

        # Create figure && Adjust size and color
        self._fig = Figure(figsize=(5, 2.5))
        self._fig.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.2)
        self.extend_matplotlib()

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
        self.extend_matplotlib()

        # Label && Canvas
        self.init_label("2D Shape")
        self.init_canvas(self._fig)
        self.init_toolbar_button()

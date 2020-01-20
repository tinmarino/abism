"""
    Abism main GUI
"""

# Standard
from os.path import isfile

# Tkinter
import tkinter as tk
import numpy as np
from astropy.io import fits

# Gui
from abism.front.Menu.MenuBar import MenuBarMaker
from abism.front.Menu.FileMenu import OpenFile
from abism.front.FrameText import LeftFrame
from abism.front.FramePlot import RightFrame
from abism.front.util_front import skin, icon_path
import abism.front.util_front as G

# Variables
import abism.back.util_back as W
from abism.util import root_path, log, set_verbose, \
    ImageInfo, AbismState, set_root, restart

# Plugin
from abism.plugin.ReadHeader import parse_header  # What a name !


class RootWindow(tk.Tk):
    """Main window app object
    May one day destroy util_front ...
    Call me like Tk:
        root_window = WindowRoot()
        root_window.mainloop()
    """
    def __init__(self):
        """Create main app"""
        super().__init__()

        # Parse arguments
        from abism.util import parse_argument
        parse_argument()


        # Variables for my children
        set_root(self)

        # Save spawned children
        self.saved_children = []
        self.image = ImageInfo()
        self.state = AbismState()

        # Global even more dirty
        W.same_center_var = tk.IntVar()
        W.same_center_var.set(1)
        W.aniso_var = tk.IntVar()
        W.aniso_var.set(1)
        W.same_psf_var = tk.IntVar()
        W.same_psf_var.set(1)

        # Give title
        self.set_title()
        self.set_icon()
        self.set_shortcut()

        # Create menu
        MenuBarMaker(self)

        # ALL What is not the menu is a paned windows :
        # I can rezie it with the mouse from left to right,
        # This (all but not the Menu) Frame is called MainPaned
        main_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, **skin().paned_dic)
        main_paned.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # 2 LEFT
        G.TextFrame = LeftFrame(self, main_paned)
        G.LabelFrame = self.LabelFrame
        G.OptionFrame = self.OptionFrame
        G.AnswerFrame = self.AnswerFrame

        # 3 RIGHT
        G.DrawPaned = RightFrame(self, main_paned)
        # Pire encore
        G.ImageFrame = self.ImageFrame
        G.FitFrame = self.FitFrame
        G.ResultFrame = self.ResultFrame


        # ######################
        # Init matplotlib figure
        # TODO this should be done as getter
        # Create Image
        G.fig = G.ImageFrame.get_figure()
        G.ImageCanvas = G.ImageFrame.get_canvas()
        G.toolbar = G.ImageFrame.get_toolbar()

        # Create Fit
        G.figfit = self.FitFrame.get_figure()
        G.dpfit = self.FitFrame.get_canvas()

        # Create Result
        G.figresult = G.ResultFrame.get_figure()
        G.dpresult = G.ResultFrame.get_canvas()

        # Open image if can
        if self.image.name:
            self.open_image()
            G.ImageFrame.draw_image()

    def set_title(self):
        """Create OS's window title, icon and Set geomrtry"""
        self.title('ABISM (' +
                   "/".join(str(self.image.name).split("/")[-3:]) + ')')

    def set_icon(self):
        """Create OS Icon from resources"""
        if isfile(icon_path()):
            bitmap = tk.PhotoImage(file=icon_path())
            self.tk.call('wm', 'iconphoto', self._w, bitmap)
        else:
            log(3, "->you have no beautiful icon "
                "because you didn't set the PATH in Abism.py")

    def set_shortcut(self):
        """Shortcuts with ctrl"""

        self.bind_all(
            "<Control-o>",
            lambda _: OpenFile(self))

        self.bind_all(
            "<Control-r>",
            lambda _: restart())

    def open_image(self, new_fits=True):
        """Open image from path
        new_fits if a new file, and not cube scrolling
        I know this is not front but so central ...
        """
        if new_fits:
            # Get <- Io
            self.image.hdulist = fits.open(self.image.name)
            self.image.im0 = self.image.hdulist[0].data

            # Delete the np.nan
            self.image.im0[np.isnan(self.image.im0)] = 0

            # Parse header
            self.header = parse_header(self.image.hdulist[0].header)

        if len(self.image.hdulist[0].data.shape) == 3:
            if new_fits:
                # we start with the last index
                self.image.cube_num = self.image.hdulist[0].data.shape[0] - 1
            if abs(self.image.cube_num) < len(self.image.hdulist[0].data[:, 0, 0]):
                if self.image.is_cube == 0:  # to load cube frame
                    self.image.is_cube = 1
                    self.ImageFrame.Cube()
                self.image.im0 = self.image.hdulist[0].data[self.image.cube_num]

            else:
                self.image.cube_num = self.image.hdulist[0].data.shape[0] - 1
                log(1, '\nERROR InitImage@WindowRoot.py :' + self.image.name
                    + ' has no index ' + str(self.image.cube_num)
                    + 'Go back to the last cube index :'
                    + str(self.image.cube_num) + "\n")
            G.cube_var.set(int(self.image.cube_num + 1))

        else:  # including image not a cube, we try to destroy cube frame
            self.image.is_cube = False
            G.ImageFrame.Cube()

        if new_fits:
            self.set_science_variable()


    def set_science_variable(self):
        """ Get variable, stat from image
        """
        from abism.back.Stat import Stat
        # BPM
        if self.image.bpm_name is not None:
            hdu = fits.open(self.image.bpm_name)
            self.image.bpm = hdu[0].data
        else:
            self.image.bpm = 0 * self.image.im0 + 1

        # Statistics
        self.image.sort = self.image.im0.flatten()
        self.image.sort.sort()
        vars(W.imstat).update(Stat(self.image.im0))

        # Image parameters
        if "ManualFrame" in vars(G):
            for i in G.image_parameter_list:
                vars(G.tkvar)[i[1]].set(vars(self.header)[i[1]])
            # to restore the values in the unclosed ImageParameters Frame
            G.LabelFrame.set_image_parameters("", destroy=False)
        # LABELS
        G.LabelFrame.update_label()

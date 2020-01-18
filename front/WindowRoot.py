"""
    Abism main GUI
"""


# Standard
from os.path import isfile

# Tkinter
from tkinter import *


# Gui
from front.Menu.MenuBar import MenuBarMaker
from front.FrameText import LeftFrame
from front.FramePlot import RightFrame

# ArrayFunction
from back.FitsIo import OpenImage


# Variables
from util import root_path, log, set_verbose
from front.util_front import skin, icon_path
import front.util_front as G
import back.util_back as W


class RootWindow(Tk):
    """Main window app object
    May one day destroy util_front ...
    Call me like Tk:
        root_window = WindowRoot()
        root_window.mainloop()
    """
    def __init__(self):
        """Create main app"""
        super().__init__()

        # Init globals TODO dirty
        W.path = root_path()

        # Global even more dirty
        set_verbose(5)
        W.same_center_var = IntVar()
        W.same_center_var.set(1)
        W.aniso_var = IntVar()
        W.aniso_var.set(1)
        W.same_psf_var = IntVar()
        W.same_psf_var.set(1)

        # Give title
        self.set_title()
        self.set_icon()

        # Create menu
        MenuBarMaker(self)

        # ALL What is not the menu is a paned windows :
        # I can rezie it with the mouse from left to right,
        # This (all but not the Menu) Frame is called MainPaned
        G.MainPaned = PanedWindow(self, orient=HORIZONTAL, **skin().paned_dic)
        G.MainPaned.pack(side=TOP, fill=BOTH, expand=1)

        # 2 LEFT
        G.TextFrame = LeftFrame(G.MainPaned)

        # 3 RIGHT
        G.DrawPaned = RightFrame(G.MainPaned)
        # Pire encore
        self.ImageFrame = G.ImageFrame


        # ######################
        # Init matplotlib figure
        # TODO this should be done as getter
        # Create Image
        G.fig = G.ImageFrame.get_figure()
        G.ImageCanvas = G.ImageFrame.get_canvas()
        G.toolbar = G.ImageFrame.get_toolbar()

        # Create Fit
        G.figfit = G.FitFrame.get_figure()
        G.dpfit = G.FitFrame.get_canvas()

        # Create Result
        G.figresult = G.ResultFrame.get_figure()
        G.dpresult = G.ResultFrame.get_canvas()

        # in case the user launch the program without giving an image as arg
        # TODO remove hardcoded "no_image_name"
        if W.image_name != "no_image_name":
            OpenImage()
            G.ImageFrame.draw_image()

    def set_title(self):
        """Create OS's window title, icon and Set geomrtry"""
        self.title('ABISM (' +
                   "/".join(str(W.image_name).split("/")[-3:]) + ')')

    def set_icon(self):
        """Create OS Icon from resources"""
        if isfile(icon_path()):
            bitmap = PhotoImage(file=icon_path())
            self.tk.call('wm', 'iconphoto', self._w, bitmap)
        else:
            log(3, "->you have no beautiful icon "
                "because you didn't set the PATH in Abism.py")

    def set_shortcuts(self):
        """TODO not working
        Shortcut, module, function, [  args, kargs  ]
        # Take MG and parents
        """

        for i in [
                ["<Control-o>", "MG", "Open"],
                ["<Control-q>", "G", "Quit"],
                ["<Control-r>", "MG", "Restart"],
                ]:
            self.bind_all(i[0], lambda i=i: vars(i[1])[i[2]]())

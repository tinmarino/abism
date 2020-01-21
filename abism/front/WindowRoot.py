"""
    Abism main GUI
"""

# Standard
from os.path import isfile

# Tkinter
import tkinter as tk
import numpy as np

# Gui
from abism.front.Menu.MenuBar import MenuBarMaker
from abism.front.Menu.FileMenu import OpenFile
from abism.front.FrameText import LeftFrame
from abism.front.FramePlot import RightFrame
from abism.front.util_front import skin, icon_path
import abism.front.util_front as G

# Variables
import abism.back.util_back as W
from abism.back.image import ImageInfo


from abism.util import log, AbismState, set_root, restart
import abism.util as util



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

        # Set icon && shortcut
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

        # Init image
        self.set_image(util._parsed_args.image)


    def set_image(self, filepath):
        # Craft ImageInfo
        self.image = ImageInfo.from_file(util._parsed_args.image)
        self.image.stat.init_all()

        self.set_title()

        # Helper
        self.header = self.image.header

        # Redraw
        self.ImageFrame.draw_image()


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

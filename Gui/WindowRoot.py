"""
    Abism main GUI
"""


# Standard
import sys
import os
from os.path import isfile
import warnings
import threading

# Tkinter
from tkinter import *
from tkinter.filedialog import askopenfilename

# Fancy
from astropy.io import fits
import numpy as np

# Gui
import MenuBar
#from Gui.Menu.MenuBar import MenuBarMaker
from Gui.FrameText import LeftFrame
from Gui.FramePlot import RightFrame

# ArrayFunction
from ArrayFunction.FitsIo import OpenImage


# Variables
from GlobalDefiner import MainVar
import GuyVariables as G
import WorkVariables as W


class RootWindow(Tk):
    """Main window app object
    May one day destroy GuyVariables ...
    Call me like Tk:
        root_window = WindowRoot()
        root_window.mainloop()
    """
    def __init__(self, root_path='.'):
        """Create main app"""
        super().__init__()

        # Init globals TODO dirty
        G.parent = self
        W.path = root_path
        MainVar()

        # Give title
        self.set_title()
        self.set_icon()

        # Create menu
        MenuBar.MenuBarMaker(self)

        # ALL What is not the menu is a paned windows :
        # I can rezie it with the mouse from left to right,
        # This (all but not the Menu) Frame is called MainPaned
        G.MainPaned = PanedWindow(G.parent, orient=HORIZONTAL, **G.paned_dic)
        G.MainPaned.pack(side=TOP, fill=BOTH, expand=1)

        # 2 LEFT
        G.TextFrame = LeftFrame(G.MainPaned)

        # 3 RIGHT
        G.DrawPaned = RightFrame(G.MainPaned)

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
        if isfile(W.path + '/Icon/bato_chico.gif'):
            bitmap = PhotoImage(file=W.path + '/Icon/bato_chico.gif')
            self.tk.call('wm', 'iconphoto', self._w, bitmap)
        else:
            W.log(3, "->you have no beautiful icon "
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

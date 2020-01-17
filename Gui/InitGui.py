"""
    Half os the gui initiallisation is here
"""
import re
import os.path          # For the Icon

from tkinter import *

import MyGui as MG

from MenuBar import MenuBarMaker
from FramePlot import RightFrame
from FrameText import LeftFrame

import GuyVariables as G
import WorkVariables as W


##################
# 0/ Main Caller
#################

def WindowInit():
    """Init main Frame"""
    # Create MenuBar and MainPaned, TextFrame and DrawFrame
    # 1 TOP
    MenuBarMaker()

    # ALL What is not the menu is a paned windows :
    # I can rezie it with the mouse from left to right,
    # This (all but not the Menu) Frame is called MainPaned
    G.MainPaned = PanedWindow(G.parent, orient=HORIZONTAL, **G.paned_dic)
    G.MainPaned.pack(side=TOP, fill=BOTH, expand=1)

    # 2 LEFT
    G.TextFrame = LeftFrame(G.MainPaned)

    # 3 RIGHT
    G.DrawPaned = RightFrame(G.MainPaned)



    ######################
    ### 4/  MORE FRAMES if click on some buttons  #
    ######################

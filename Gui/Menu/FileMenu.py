"""
    Scrolldown on file tab
"""
from tkinter import Menu, Menubutton, Tk, Frame, \
    Scrollbar, Button, Entry, Text, Label, \
    LEFT, RIGHT, BOTH, TOP, X, Y, INSERT, END
from tkinter.filedialog import askopenfilename


import GuyVariables as G
import WorkVariables as W

import MyGui as MG
from Plugin.FitsHeaderWindow import DisplayHeader


def FileMenu(args):
    """Menu, open_image, header
        args is a dictionnary containing the arguments to make all menuENtry
        identical, logical, responsible, pratical
    """
    G.menu = Menubutton(G.MenuBar, **args)
    G.menu.menu = Menu(G.menu, **G.submenu_args)

    G.menu.menu.add_command(label='Open', command=Open)
    G.menu.menu.add_command(
        label='Display Header',
        command=lambda: DisplayHeader(W.image_name, W.head.flathead))

    G.menu['menu'] = G.menu.menu
    return G.menu


def Open():
    """Open an image file
    A click on this button will open a window.
    You need to select a FITS image to load with Abism.
    This is an other way to load an image, the first one is to load it
    directly in the script by bash Abism.sh [-i] image.fits.
    """

    # the same dir as the image
    initialdir = "/".join(W.image_name.split("/")[: -1])
    s_file = askopenfilename(title="Open a FITS image", filetypes=[(
        "fitsfiles", "*.fits"), ("allfiles", "*")], initialdir=initialdir)
    s_file = str(s_file)
    W.log(0, "Opening file : " + s_file)
    W.image_name = s_file
    MG.InitImage()

    # Chancge title
    title = W.image_name.split('/')  # we cut the title
    G.parent.title('Abism (' + title[-1]+')')

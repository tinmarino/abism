"""
    Scrolldown on file tab
"""
from tkinter import Menu, Menubutton
from tkinter.filedialog import askopenfilename


import back.util_back as W
import front.util_front as G

from plugin.FitsHeaderWindow import DisplayHeader


def FileMenu(root, parent, args):
    """Menu, open_image, header
        args is a dictionnary containing the arguments to make all menuENtry
        identical, logical, responsible, pratical
    """
    menu_button = Menubutton(parent, **args)
    menu_button.menu = Menu(menu_button, **G.submenu_args)

    # Open
    initialdir = "/".join(W.image_name.split("/")[: -1])
    menu_button.menu.add_command(
        label='Open',
        command=lambda: OpenFile(root, initialdir=initialdir))

    # Show header
    menu_button.menu.add_command(
        label='Display Header',
        command=lambda: DisplayHeader(
            W.image_name, W.head.header.tostring(sep="\n")))

    menu_button['menu'] = menu_button.menu

    # Caller grid me
    return menu_button


def OpenFile(root, initialdir=''):
    """Open an image file
    A click on this button will open a window.
    You need to select a FITS image to load with Abism.
    This is an other way to load an image, the first one is to load it
    directly in the script by bash Abism.sh [-i] image.fits.
    """
    # Pop window to ak for a file
    s_file = askopenfilename(title="Open a FITS image", filetypes=[(
        "fitsfiles", "*.fits"), ("allfiles", "*")], initialdir=initialdir)

    # Stringigy && Log && Cache
    s_file = str(s_file)
    W.log(0, "Opening file : " + s_file)
    W.image_name = s_file

    root.ImageFrame.draw_image()

    # Change title
    fname = W.image_name.split('/')[-1]
    root.title('Abism (' + fname + ')')

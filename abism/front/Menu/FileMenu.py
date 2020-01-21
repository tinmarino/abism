"""
    Scrolldown on file tab
"""
from tkinter import Menu, Menubutton
from tkinter.filedialog import askopenfilename


from abism.util import log
from abism.front.util_front import skin

from abism.plugin.FitsHeaderWindow import DisplayHeader


def FileMenu(root, parent, args):
    """Menu, open_image, header
        args is a dictionnary containing the arguments to make all menuENtry
        identical, logical, responsible, pratical
    """
    menu_button = Menubutton(parent, **args)
    menu_button.menu = Menu(menu_button, **skin().fg_and_bg)

    # Open
    menu_button.menu.add_command(
        label='Open',
        command=lambda: OpenFile(root))

    # Show header
    menu_button.menu.add_command(
        label='Display Header',
        command=lambda: DisplayHeader(
            root.image.name,
            root.header.header.tostring(sep="\n"),
            save=root.saved_children,
        ))

    menu_button['menu'] = menu_button.menu

    # Caller grid me
    return menu_button


def OpenFile(root):
    """Open an image file
    A click on this button will open a window.
    You need to select a FITS image to load with Abism.
    This is an other way to load an image, the first one is to load it
    directly in the script by bash Abism.sh [-i] image.fits.
    """
    import os

    initialdir = "/".join(root.image.name.split("/")[: -1])
    initialdir = initialdir or os.getcwd()

    # Pop window to ak for a file
    s_file = askopenfilename(title="Open a FITS image", filetypes=[(
        "fitsfiles", "*.fits"), ("allfiles", "*")], initialdir=initialdir)

    # Stringigy && Log && Cache
    s_file = str(s_file)
    log(0, "Opening file : " + s_file)
    root.set_image(s_file)

    root.ImageFrame.draw_image()

    # Change title
    fname = root.image.name.split('/')[-1]
    root.title('Abism (' + fname + ')')

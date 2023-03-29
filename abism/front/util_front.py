#!/usr/bin/env python3

"""
Utility function for Abism GUI
"""

# pylint: disable=broad-except  # To get GUI working
# pylint: disable=import-outside-toplevel

# Standard
import os
from functools import lru_cache
from shutil import which
from subprocess import call

import tkinter as tk

from abism import __version__  # To show it

from abism.util import root_path, log, get_root, get_state

import abism.front.tk_extension as tk_ext  # pylint: disable = unused-import


@lru_cache(1)
def photo_up():
    """ Return path of arrow_up icon """
    return tk.PhotoImage(
        file=root_path() +
        "res/arrow_up.gif",
        master=get_root())


@lru_cache(1)
def photo_down():
    """ Return path of arrow_down icon """
    return tk.PhotoImage(
        file=root_path() +
        "res/arrow_down.gif",
        master=get_root())


@lru_cache(1)
def icon_path():
    """ Return path of window icon """
    return root_path() + 'res/bato_chico.gif'


def about_window():
    """ Pop about window
    Append it to (to)
    """
    # Init
    root = tk.Tk()

    # Conf
    root.title("About Abism")
    txt = ("Adaptive Background Interactive Strehl Meter\n"
           "ABISM version " + __version__ + " (2013 -- 2023) \n"
           "Authors: Girard Julien, Tourneboeuf Martin\n"
           "Emails: juliengirard@gmail.com tinmarino@gmail.com\n")
    label = tk.Label(root, text=txt)
    label.pack(expand=True, fill=tk.BOTH)

    # Go
    root.mainloop()


def system_open(path=""):
    """ Call system default open for file
    path: path of the file to oopen relative to abism root path
    """
    full_path = root_path() + path

    fct = None
    # Paranal acroread
    if not fct and path.endswith('.pdf'):
        fct = which("acroread")

    # Linux sxdg-open
    if not fct:
        fct = which("xdg-open")

    # Linux see
    if not fct:
        fct = which("see")

    # Mac open
    if not fct:
        fct = which("open")

    if fct:
        call(fct + " " + full_path + " &", shell=True)
    else:
        log(0, "ERROR system open : need to be implemented ")


def abism_askopenfilename(**args):
    """ Util: Popup window to get filepath
    try GTK (Ubuntu) or else default TK
    """
    try:
        from abism.plugin.gtk_window_open import gtk_askopenfilename
        fname = gtk_askopenfilename(**args)
        log(3, "Open: GTK returned:", fname)
    except BaseException:
        from tkinter.filedialog import askopenfilename
        fname = askopenfilename(**args)
        log(3, "Open: TK returned:", fname)
    return fname


def open_file():
    """ Open an image file
    A click on this button will open a window.
    You need to select a FITS image to load with Abism.
    This is an other way to load an image, the first one is to load it
    directly in the script by bash Abism.sh [-i] image.fits.
    Used: MenuFile or bind with o
    """
    # Get rootdirecotyr of search
    try:
        initialdir = "/".join(get_state().image.name.split("/")[: -1])
        initialdir = initialdir or os.getcwd()
    except BaseException:
        initialdir = os.getcwd()

    # Pop window to ask for a file
    s_file = abism_askopenfilename(
        title="Open a FITS image",
        filetypes=[("FITS", "*.fits"), ("allfiles", "*")],
        initialdir=initialdir)
    if not s_file:
        return

    # Stringify && Log
    s_file = str(s_file)
    log(0, "Opening file : " + s_file)

    # Set and draw
    get_root().set_image(s_file)


def toggle_header():
    """ Toggle header viewer """

    from abism.plugin.window_text import WindowText

    def on_close():
        toggle_header.window_header.destroy()
        toggle_header.window_header = None

    # Toggle hide
    if toggle_header.window_header is not None:
        on_close()
        return

    toggle_header.window_header = WindowText(
        title='headder(' + get_state().image.name + ')',
        geometry='1000x1000+0+0',
        text=get_root().header.header.tostring(sep="\n")
    )

    toggle_header.window_header.protocol('WM_DELETE_WINDOW', on_close)
    toggle_header.window_header.mainloop()


toggle_header.window_header = None


def toggle_manual():
    """ Toggle interface documentation window """

    from abism.plugin.window_text import WindowText

    def on_close():
        toggle_manual.window_manual.destroy()
        toggle_manual.window_manual = None

    # Toggle hide
    if toggle_manual.window_manual is not None:
        on_close()
        return

    fpath = root_path() + 'doc/interface.md'
    with open(fpath, mode='r', encoding='utf-8') as fil:
        text = fil.read()
    toggle_manual.window_manual = WindowText(
        title='ABISM interface manual',
        geometry='800x1000+0+0',
        text=text,
        color_md=True,
    )

    toggle_manual.window_manual.protocol('WM_DELETE_WINDOW', on_close)
    toggle_manual.window_manual.mainloop()


toggle_manual.window_manual = None


def is_toolbar_active(toolbar):
    """ Check if a matplotlib toolbar is active """
    try:
        from matplotlib.backend_bases import _Mode
        res = toolbar.mode in (_Mode.ZOOM, _Mode.PAN)
    except BaseException:
        log(0, 'Deprecation Warning: toolbar._active do no longer exists, update matplotlib')
        # pylint: disable = protected-access
        res = toolbar._active in ('PAN', 'ZOOM')
    return res


def open_background_and_subtract():
    """ Subtract A background image """
    # Ask for background
    fp_sky = abism_askopenfilename(
        filetypes=[("fitsfiles", "*.fits"), ("allfiles", "*")])

    # Subtract and Redraw
    if get_state().image.subtract_sky(fp_sky):
        get_root().frame_image.draw_image()

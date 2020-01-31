"""
    Utility function for Abism GUI
"""

# Standard
import os
from functools import lru_cache

import tkinter as tk

from abism.util import root_path, log, get_root, get_state

import abism.front.tk_extension as tk_ext  # pylint: disable = unused-import


@lru_cache(1)
def photo_up():
    """Return path of arrow_up icon"""
    return tk.PhotoImage(file=root_path() + "res/arrow_up.gif", master=get_root())


@lru_cache(1)
def photo_down():
    """Return path of arrow_down icon"""
    return tk.PhotoImage(file=root_path() + "res/arrow_down.gif", master=get_root())


@lru_cache(1)
def icon_path():
    """Return path of window icon"""
    return root_path() + 'res/bato_chico.gif'


def about_window():
    """Pop about window
    Append it to (to)
    """
    from abism import __version__
    # Init
    root = tk.Tk()

    # Conf
    root.title("About Abism")
    txt = ("Adaptive Background Interactive Strehl Meter\n"
           "ABISM version " + __version__ + " (2013 -- 2020) \n"
           "Authors: Girard Julien, Tourneboeuf Martin\n"
           "Emails: juliengirard@gmail.com tinmarino@gmail.com\n")
    label = tk.Label(root, text=txt)
    label.pack(expand=True, fill=tk.BOTH)

    # Go
    root.mainloop()


def system_open(path=""):
    """Call system defautl open for file
    path: path of the file to oopen relative to abism root path
    """
    import subprocess
    my_pdf = root_path() + path

    fct = None
    try:  # PARANAL acroread
        subprocess.check_call("acroread", shell=False)
        fct = "acroread"
    except BaseException:
        try:  # Linux see
            subprocess.check_call("see", shell=False)
            fct = "see"
        except BaseException:
            try:  # mac open
                from subprocess import check_call
                check_call("open   " + my_pdf, shell=False)
                fct = "open"
            except BaseException:
                pass

    if fct is not None:
        subprocess.call(fct + " " + my_pdf + " &", shell=True)  # PARANAL
    log(0, "ERROR pdf viewer : need to be implemented ")


def abism_askopenfilename(**args):
    try:
        from abism.plugin.gtk_window_open import gtk_askopenfilename
        fname = gtk_askopenfilename(**args)
        log(3, "Open: GTK returned:", fname)
    except:
        from tkinter.filedialog import askopenfilename
        fname = askopenfilename(**args)
        log(3, "Open: TK returned:", fname)
    return fname


def open_file():
    """Open an image file
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
    except:
        initialdir = os.getcwd()

    # Pop window to ask for a file
    s_file = abism_askopenfilename(
        title="Open a FITS image",
        filetypes=[("FITS", "*.fits"), ("allfiles", "*")],
        initialdir=initialdir)
    if not s_file: return

    # Stringify && Log
    s_file = str(s_file)
    log(0, "Opening file : " + s_file)

    # Set and draw
    get_root().set_image(s_file)


def show_header():
    from abism.plugin.window_header import spawn_header_window
    spawn_header_window(
        get_state().image.name,
        get_root().header.header.tostring(sep="\n"))


def open_backgroud_and_substract():
    """Subtract A background image"""
    # Ask for background
    fp_sky = abism_askopenfilename(
        filetypes=[("fitsfiles", "*.fits"), ("allfiles", "*")])

    # Substract and Redraw
    if get_state().image.substract_sky(fp_sky):
        get_root().frame_image.draw_image()

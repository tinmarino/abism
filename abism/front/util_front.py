"""
    Utilities for Abism GUI
"""

# Standard
from functools import lru_cache
from enum import Enum

import tkinter as tk
from tkinter.filedialog import askopenfilename

from abism.util import root_path, log, get_version, get_root  # pylint: disable=no-name-in-module



""" SOOOO dirty"""

class VoidClass:
    """Helper container"""


# BUTTON WIDTH
button_width = 12  # the width of the standard buttons
menu_button_width = 8  # Size of menu buttons

# GUI FORM
# we don't hide text frame by default, the text framme is the output frame on the left
hidden_text_bool = 0
scale_menu_type = "column" # can be "column" or "cascade"
all_frame = []                        # all frames will be here to change color
# Can be tkinter or shell , written interaction with the mainloop
interaction_type = "tkinter"
last_top_size = 300

# GEO DIC
geo_dic = {}                        # geometry dictionnay
geo_dic['ResultFrame'] = 300


# SCALE dic for the color and contrast
scale_dic = [{}]
scale_dic[0]["cmap"] = "jet"
scale_dic[0]["contour"] = False
scale_dic[0]["answer"] = "detector"
scale_dic[0]["percent"] = 99.99
scale_dic[0]["scale_cut_type"] = "sigma_clip"
scale_dic[0]["sigma"] = 3
scale_dic[0]["stretch"] = "linear"

# BOOL TODO remove
manual_cut_bool = 0
more_bool = 0

toolbar_fit_bool = False
toolbar_result_bool = False
manual_back_bool = False
# the labels on the left, when open image, this is set to true
label_bool = True
result_bool = True                          # show the full results frame
top_bool = True
in_arrow_frame = None                          # no body in lefftoparrowframe

# CLASS
# (we save the tkvariables ) # it may be changed see image parameters
tkvar = VoidClass()
tkentry = VoidClass()



@lru_cache(1)
def photo_up():
    """Return path of arrow_up icon"""
    return tk.PhotoImage(file=root_path() + "res/arrow_up.gif")


@lru_cache(1)
def photo_down():
    """Return path of arrow_down icon"""
    return tk.PhotoImage(file=root_path() + "res/arrow_down.gif")


@lru_cache(1)
def icon_path():
    """Return path of window icon"""
    return root_path() + 'res/bato_chico.gif'


class Font:
    """Font for skin"""
    def __init__(self):
        self.small = tk.font.Font(size=6)
        self.answer = tk.font.Font(size=10)   # all answer in AnswerFrame
        self.strehl = tk.font.Font(size=12)  # just strehl answer
        self.warning = tk.font.Font(size=12)  # just strehl answer
        self.param = tk.font.Font(size=11)  # Image parameters
        self.big = tk.font.Font(size=16)


class DotDic(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class ButtonDic(DotDic):
    """Button arguments"""
    def __init__(self, color):
        super().__init__(self)
        # Cutom
        self.highlightcolor = color.bu_hi
        self.bg = color.bu
        self.fg = color.fg

        # Always
        self.bd = 3
        self.padx = 0
        self.pady = 0
        self.highlightthickness = 0


class PanedDic(DotDic):
    """The sas is the little between windows "glissiere", to resize"""
    def __init__(self, color):
        super().__init__()
        self.bg = color.sash

        self.sashwidth = 2
        self.sashpad = 0
        self.showhandle = 0
        self.borderwidth = 0
        self.sashrelief = tk.RAISED


class FrameDic(DotDic):
    """Just a bg"""
    def __init__(self, color):
        super().__init__()
        self.bg = color.bg


class TitleLabelDic(DotDic):
    """Label titles on top of each text_frame (left)
    OLD:    "fg": "blue", "bg": "white", "font": tkFont.Font(size=10),
        "padx": 3,
        "highlightbackground": "black", "highlightcolor": "black", "highlightthickness": 1,
        "padx": 3,
    """
    def __init__(self, color):
        self.bg = color.label_title_bg
        self.fg = color.label_title_fg
        self.font = tk.font.Font(size=10)
        self.padx = 3
        self.highlightbackground = color.label_title_fg
        self.highlightcolor = color.label_title_fg
        self.highlightthickness = 1


class TitleLabel(tk.Label):
    def __init__(self, parent, **args):
        args.update(skin().label_title_dic)
        super().__init__(parent, **args)


class Scheme(Enum):
    """The colorscheme available"""
    DARK_SOLARIZED = 1
    LIGHT_SOLARIZED = 2

# Global waiting for a better idea
scheme = Scheme.LIGHT_SOLARIZED


class ColorScheme:
    """Colors"""
    # pylint: disable=bad-whitespace
    # pylint: disable=attribute-defined-outside-init
    def __init__(self):
        self.set_solarized_var()
        self.init_solarized_default()
        if scheme == Scheme.DARK_SOLARIZED:
            self.init_dark()
        elif scheme == Scheme.LIGHT_SOLARIZED:
            self.init_light()

    def set_solarized_var(self):
        """Init solarized varaibles"""
        self.solarized_base03   = "#002b36"
        self.solarized_base02   = "#073642"
        self.solarized_base01   = "#586e75"
        self.solarized_base00   = "#657b83"
        self.solarized_base0    = "#839496"
        self.solarized_base1    = "#93a1a1"
        self.solarized_base2    = "#eee8d5"
        self.solarized_base3    = "#fdf6e3"
        self.solarized_yellow   = "#b58900"
        self.solarized_orange   = "#cb4b16"
        self.solarized_red      = "#dc322f"
        self.solarized_magenta  = "#d33682"
        self.solarized_violet   = "#6c71c4"
        self.solarized_blue     = "#268bd2"
        self.solarized_cyan     = "#2aa198"
        self.solarized_green    = "#859900"

    def init_solarized_default(self):
        """Dark and light"""
        self.sash               = self.solarized_blue
        self.quit               = self.solarized_red
        self.restart            = self.solarized_cyan
        self.parameter1         = self.solarized_blue
        self.parameter2         = self.solarized_green
        self.label_title_fg     = self.solarized_blue

    def init_dark(self):
        """Solarized dark"""
        self.bg                 = self.solarized_base02
        self.fg                 = self.solarized_base2
        self.bu                 = self.solarized_base01
        self.bu_hi              = self.solarized_base00
        self.label_title_bg     = self.solarized_base03

    def init_light(self):
        """Solarized light"""
        self.bg                 = self.solarized_base3
        self.fg                 = self.solarized_base03
        self.bu                 = self.solarized_base2
        self.bu_hi              = self.solarized_base3
        self.label_title_bg     = self.solarized_base3


class Skin:
    """Skin to put all default apperance"""
    def __init__(self):
        self.font = Font()
        self.color = ColorScheme()

        self.button_dic = ButtonDic(self.color)
        self.paned_dic = PanedDic(self.color)
        self.frame_dic = FrameDic(self.color)
        self.label_title_dic = TitleLabelDic(self.color)

        self.fg_and_bg = {'fg':self.color.fg, 'bg':self.color.bg}


def update_widget_skin(widget):
    """Update the skin of a widget"""
    from abism.front.FramePlot import PlotFrame

    log(9, 'Updating:', widget.__class__.__name__)

    if isinstance(widget, PlotFrame):
        widget.update_skin()
        log(9, 'And is instance of PlotFrame ------------')
    elif isinstance(widget, tk.Button):
        # Do not change favourites buttons ...
        if widget['bg'] in (
                skin().color.quit,
                skin().color.restart,
                skin().color.parameter1,
                skin().color.parameter2,
                ):
            return
        widget.configure(skin().button_dic)
    elif isinstance(widget, tk.PanedWindow):
        widget.configure(skin().paned_dic)
    elif isinstance(widget, tk.Frame):
        widget.configure(skin().frame_dic)
    elif isinstance(widget, TitleLabel):
        widget.configure(skin().label_title_dic)
    # Scrollbar and Canvas have no fg
    elif isinstance(widget, (tk.Canvas, tk.Scrollbar)):
        widget.configure(bg=skin().color.bg)
    else:
        widget.configure(
            bg=skin().color.bg,
            fg=skin().color.fg
        )


def change_scheme(root, in_scheme):
    """Dark skin"""
    reset_skin(in_scheme)
    for widget in (root, *root.saved_children):
        children_do(widget, update_widget_skin)


@lru_cache(1)
def skin():
    """Singleton trick"""
    log(3, 'Skin requested')
    return Skin()


def reset_skin(in_scheme):
    """Invalidate skin cache
    Used if skin has been updated from callers (the world)
    """
    global scheme
    scheme = in_scheme
    skin.cache_clear()
    skin()


def about_window(save=None):
    """Pop about window
    Append it to (to)
    """
    root = tk.Tk()
    if save is not None: save.append(root)
    root.title("About Abism")
    txt = ("Adaptive Background Interactive Strehl Meter\n"
           "ABISM version " + get_version() + " (2013 -- 2020) \n"
           "Authors: Girard Julien, Tourneboeuf Martin\n"
           "Emails: juliengirard@gmail.com tinmarino@gmail.com\n")
    tk.Label(root, text=txt, **skin().fg_and_bg).pack()
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


def children_do(widget, callback):
    """Recurse and call helper
    callback: function(widget)
    """
    for item in widget.winfo_children():
        callback(item)
        children_do(item, callback)


def set_figure_skin(figure, in_skin):
    """Update skin, caller must redraw"""
    fg = in_skin.color.fg
    bg = in_skin.color.bg

    # Figure
    figure.set_facecolor(bg)

    # Ax
    for ax in figure.axes:
        # Spine
        ax.spines['bottom'].set_color(fg)
        ax.spines['top'].set_color(fg)
        ax.spines['right'].set_color(fg)
        ax.spines['left'].set_color(fg)

        # Tick
        ax.tick_params(axis='x', colors=fg)
        ax.tick_params(axis='y', colors=fg)

        # Label
        ax.yaxis.label.set_color(fg)
        ax.xaxis.label.set_color(fg)

        # Title
        ax.title.set_color(fg)


def open_file():
    """Open an image file
    A click on this button will open a window.
    You need to select a FITS image to load with Abism.
    This is an other way to load an image, the first one is to load it
    directly in the script by bash Abism.sh [-i] image.fits.
    Used: MenuFile or bind with o
    """
    import os

    # Get rootdirecotyr of search
    initialdir = "/".join(get_root().image.name.split("/")[: -1])
    initialdir = initialdir or os.getcwd()

    # Pop window to ask for a file
    s_file = askopenfilename(
        title="Open a FITS image",
        filetypes=[("fitsfiles", "*.fits"), ("allfiles", "*")],
        initialdir=initialdir)
    if not s_file: return

    # Stringify && Log && Cache
    s_file = str(s_file)
    log(0, "Opening file : " + s_file)
    get_root().set_image(s_file)

    get_root().ImageFrame.draw_image()

    # Change title
    fname = get_root().image.name.split('/')[-1]
    get_root().title('Abism (' + fname + ')')

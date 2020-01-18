"""
    Utilities for Abism GUI
"""

# Standard
from sys import exit as sys_exit
from os import system
from functools import lru_cache
from enum import Enum

import tkinter as tk

from util import root_path, log, get_version  # pylint: disable=no-name-in-module
import back.util_back as W


@lru_cache(1)
def photo_up():
    """Return path of arrow_up icon"""
    return tk.PhotoImage(file=root_path() + "/res/arrow_up.gif")


@lru_cache(1)
def photo_down():
    """Return path of arrow_down icon"""
    return tk.PhotoImage(file=root_path() + "/res/arrow_down.gif")


def quit_process():
    """Kill process"""
    log(1, 'Closing Abism, Goodbye. Come back soon.' + "\n" + 100 * '_' + 3 * "\n")
    # parent.destroy()
    sys_exit(1)


def Restart():
    """ TODO move me to Global Definer, WritePref and ReadPref
        Pushing this button will close ABISM and restart it the same way it was launch before.
        Programmers: this is made to reload the Software if a modification in the code were made.
    """

    #################
    # prepare arguments
    arg = W.sys_argv

    # IMAGE_NAME
    matching = [s for s in arg if ".fits" in s]
    if len(matching) > 0:
        arg[arg.index(matching[0])] = W.image_name
    else:
        arg.insert(1, W.image_name)

    # COLOR MAP
    try:
        cmap = ImageFrame.cbar.cbar.get_cmap().name
    except BaseException:
        cmap = "jet"  # if no image loaded
    if not isinstance(cmap, str):
        cmap = "jet"
    for i in [ # TODO see in util and goto util
        # SCALE DIC
        ["--cmap", cmap],
        ["--scale_dic_stretch", scale_dic[0]["stretch"]],
        ["--scale_dic_scale_cut_type", scale_dic[0]["scale_cut_type"]],
        ["--scale_dic_percent", scale_dic[0]["percent"]],


        # FRAME
        ["--parent", parent.geometry()],
        ["--TextPaned", TextPaned.winfo_width()],
        ["--DrawPaned", DrawPaned.winfo_width()],
        ["--LabelFrame", LabelFrame.winfo_width()],
        ["--ResultFrame", ResultFrame.winfo_height()],
        ["--OptionFrame", OptionFrame.winfo_height()],
        ["--ImageFrame", ImageFrame.winfo_height()],
        ["--RightBottomPaned", RightBottomPaned.winfo_height()],
        ["--FitFrame", FitFrame.winfo_width()],
        ["--AnswerFrame", AnswerFrame.winfo_width()],
        ["--ImageName", W.image_name],
    ]:
        if not i[0] in arg:
            arg.append(i[0])
            arg.append('"' + str(i[1]) + '"')
        else:
            arg[arg.index(i[0]) + 1] = '"' + str(i[1]) + '"'

    ###########
    # PREPARE STG command line args
    stg = "python "
    for i in arg:
        stg += " " + i
    stg += " &"  # To keep the control of the terminal
    log(0, "\n\n\n" + 80 * "_" + "\n",
          "Restarting ABISM with command:\n" + stg + "\nplease wait")

    ##########
    # DESTROY AND LAUNCH
    parent.destroy()  # I destroy Window,
    system(stg)         # I call an other instance
    sys_exit(1)         # I exit the current process.
    # As the loop is now opened, this may not be necessary but anyway it is safer


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
    from front.FramePlot import PlotFrame


    if isinstance(widget, PlotFrame):
        widget.update_skin()
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
    elif isinstance(widget, tk.Canvas):
        widget.configure(bg=skin().color.bg)
    else:
        widget.configure(
            bg=skin().color.bg,
            fg=skin().color.fg
        )


def change_scheme(root, in_scheme):
    """Dark skin"""
    reset_skin(in_scheme)
    children_do(root, update_widget_skin)


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


def about_window():
    """Pop about window"""
    root = tk.Tk()
    root.title("About Abism")
    txt = ("Adaptive Background Interactive Strehl Meter\n"
           "ABISM version " + get_version() + " (2013 -- 2020) \n"
           "Authors: Girard Julien, Tourneboeuf Martin\n"
           "Emails: juliengirard@gmail.com tinmarino@gmail.com\n")
    tk.Label(root, text=txt).pack()
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

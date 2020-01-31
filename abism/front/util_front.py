"""
    Utilities for Abism GUI
    Could be called tk_extension for most of it
    Must refactor all as class extension (I did not know the possibility)
"""
import os

# Standard
from functools import lru_cache

import tkinter as tk

from abism.util import root_path, log, get_root, get_state

from abism.front.tk_extension import scheme


# Skin
####################################################################



def update_widget_skin(widget):
    """Update the skin of a widget"""
    log(9, 'Updating:', widget.__class__.__name__)

    custom_call = getattr(widget, 'update_skin', None)
    if callable(custom_call):
        custom_call()
        log(9, 'And is instance of PlotFrame ------------')
    else:
        widget.configure(
            bg=scheme.bg,
            fg=scheme.fg
        )


def change_root_scheme(in_scheme):
    # pylint: disable = global-statement
    global scheme
    root = get_root()
    scheme = in_scheme
    for widget in (root, *root.saved_children):
        children_do(widget, update_widget_skin)


def children_do(widget, callback):
    """Recurse and call helper
    callback: function(widget)
    """
    for item in widget.winfo_children():
        callback(item)
        children_do(item, callback)


def set_figure_skin(figure):
    """Update skin, caller must redraw"""
    fg = scheme.fg
    bg = scheme.bg

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


# Tkinter extension
####################################################################


# Replace Tk to keep a refrence to change color (very important)
tk.old_Tk = tk.Tk
def tk_Tk():
    root = tk.old_Tk()
    def on_close():
        get_root().saved_children.remove(root)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    get_root().saved_children.append(root)
    return root
tk.Tk = tk_Tk


class HoverInfo:
    """Helper class to show a label when mouse on a widget
    Alais toolTip by its author
    """
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.text = ''
        self.x = self.y = 0
        self.on_work = False

    def show(self, text, index=None):
        """Get param in and launch display timer"""
        # Check in: do not work twice
        if self.on_work: return
        self.on_work = True
        self.text = text

        # Check in: do not work for nothing
        if self.tipwindow or not self.text:
            return

        # Calculate position
        self.x, self.y, cx, cy = self.widget.bbox("insert")
        self.x += cx + self.widget.winfo_rootx() + 130
        self.y += cy + self.widget.winfo_rooty() + 20
        if index is not None:
            self.x += self.widget.xposition(index)
            self.y += self.widget.yposition(index)

        # Launch worker: "may the winds be favorable to you"
        self.widget.after(300, self.show_now)

    def show_now(self):
        """Display text in tooltip window"""
        # Check in: maybe too late, if user left -> hide triggered
        if not self.on_work: return

        # Hide my bro
        self.hide()

        # Create widget toplevel
        self.tipwindow = tk.Toplevel(self.widget)
        self.tipwindow.wm_overrideredirect(1)
        self.tipwindow.wm_geometry("+%d+%d" % (self.x, self.y))

        # Pack label
        label = tk.Label(
            self.tipwindow, text=self.text, justify=tk.LEFT,
            background="#ffffe0", relief=tk.SOLID, borderwidth=1,
            font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide(self):
        """Hide hover info window"""
        # Block tip creation until new event
        self.on_work = False

        # If feasable, destroy tip window
        if not self.tipwindow: return
        self.tipwindow.destroy()
        self.tipwindow = None


def bind_widget_hover(self):
    def enter(_):
        self.hover_info.hide()
        self.hover_info.show(self.hover_text)
    def leave(_):
        self.hover_info.hide()
    self.bind('<Enter>', enter)
    self.bind('<Leave>', leave)

def set_hover_info(self, text):
    """Set hover info to widget"""
    self.hover_info = HoverInfo(self)
    self.hover_text = text
    self.bind_widget_hover()

# Create widget member function to add info on hover
tk.Widget.bind_widget_hover = bind_widget_hover
tk.Widget.set_hover_info = set_hover_info


def on_menu_hover(self):
    """Callback: On <<MenuSelect>>
    called by add_entry_info
    """
    index_active = self.index(tk.ACTIVE)
    if index_active in self.idx_text:
        text = self.idx_text[index_active]
        self.hover_info.hide()
        self.hover_info.show(text, index=index_active)
    elif self.hover_info:
        self.hover_info.hide()

def bind_menu_hover(self):
    self.bind("<<MenuSelect>>", lambda _: self.on_menu_hover())
    self.bind("<Leave>", lambda _: self.hover_info.hide())
    self.bind("<FocusOut>", lambda _: self.hover_info.hide())
    self.bind("<FocusIn>", lambda _: self.activate(666))

def add_entry_info(self, text):
    """Add info to last entry"""
    idx = self.index(tk.END)
    if not 'idx_text' in vars(self):
        self.idx_text = {}
        self.hover_info = HoverInfo(self)
    self.idx_text.update({idx: text})
    self.bind_menu_hover()

# Create Menu add_entry_info function member
tk.Menu.bind_menu_hover = bind_menu_hover
tk.Menu.add_entry_info = add_entry_info
tk.Menu.on_menu_hover = on_menu_hover


# Utilities
####################################################################


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

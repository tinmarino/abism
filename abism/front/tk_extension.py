"""
    Extend some tk class and method for:
    1. Skin
    2. Aliases functionality like inseting an abism answer in a text widget
    Should be imported soon enough

    This is faster as moving all to tkk, but if you want to, have a look at:
    link: https://github.com/fgirault/tkcode <- tkcode a ttk text editor (pretty)
"""
from enum import Enum

import tkinter as tk
import tkinter.font  # pylint: disable = unused-import

from abism.util import log, get_root


######################################################################
#               Scheme (alias Style)
######################################################################


class Scheme(Enum):
    """The colorscheme available"""
    DARK_SOLARIZED = 1
    LIGHT_SOLARIZED = 2


class ColorScheme:
    """Colors"""
    # pylint: disable=bad-whitespace
    # pylint: disable=attribute-defined-outside-init
    def __init__(self, e_scheme):
        self.set_solarized_var()
        self.init_solarized_default()
        if e_scheme == Scheme.DARK_SOLARIZED:
            self.init_dark()
        elif e_scheme == Scheme.LIGHT_SOLARIZED:
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
        self.important          = self.solarized_red
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
        self.bg_extreme         = "#000000"

    def init_light(self):
        """Solarized light"""
        self.bg                 = "#ffffff"  # self.solarized_base3
        self.fg                 = self.solarized_base03
        self.bu                 = self.solarized_base2
        self.bu_hi              = self.solarized_base3
        self.label_title_bg     = self.solarized_base3
        self.bg_extreme         = "#ffffff"


# Global waiting for a better idea
scheme = ColorScheme(Scheme.LIGHT_SOLARIZED)


def get_button_dic():
    return dict(
        # Cutom
        highlightcolor=scheme.bu_hi,
        bg=scheme.bu,
        fg=scheme.fg,

        # Always
        bd=3,
        padx=0,
        pady=0,
        highlightthickness=0,
    )


def from_dic(victim, dic_getter):
    """Factory: class from a dic for tk class proxy
    Usurpating a victim (proxified) class calling it in my init
    victim: class proxified
    dic_getter: funtion to get a dic, if a dic itself: not updatable
    """
    name = 'Abism_' + victim.__name__
    bases = (victim,)

    def init_proxy(obj, *args, **kw):
        dic = dic_getter()
        dic.update(kw)
        victim.__init__(obj, *args, **dic)

    def update_skin(obj):
        log(5, "Updating skin", victim, 'with', dic_getter())
        obj.configure(**dic_getter())

    fct_dic = {
        '__init__': init_proxy,
        'update_skin': update_skin
    }
    return type(name, bases, fct_dic)


class Button(tk.Button):
    """Button arguments"""
    def __init__(self, *args, **kw):
        dic = get_button_dic()
        dic.update(kw)
        super().__init__(*args, **dic)

    def update_skin(self):
        # Do not change favourites buttons ...
        if self['bg'] in (
                scheme.quit,
                scheme.restart,
                scheme.parameter1,
                scheme.parameter2,
                ):
            return
        self.configure(get_button_dic())


class Frame(tk.Frame):
    """Some frame (frame_plot) contain a figure (_fig)
    that must be updated as matplotlib (hide set_figure_skin here)
    """
    def __init__(self, *args, **kw):
        self.dic_getter = lambda: {'bg': scheme.bg}
        dic = self.dic_getter()
        dic.update(kw)
        super().__init__(*args, **dic)

    def update_skin(self):
        log(5, 'Updating skin Label with', self.dic_getter())
        self.configure(**self.dic_getter())
        self.set_figure_skin()


    def set_figure_skin(self):
        """Update skin, caller must redraw"""
        if not '_fig' in vars(self): return
        fg = scheme.fg
        bg = scheme.bg

        # Figure
        self._fig.set_facecolor(bg)

        # Ax
        for ax in self._fig.axes:
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

        # Redraw
        self._fig.canvas.draw()




tk.Button = Button
tk.Frame = Frame

TitleLabel = from_dic(tk.Label, lambda: {
    'bg': scheme.label_title_bg,
    'fg': scheme.label_title_fg,
    'font': tk.font.Font(size=10),
    'padx': 3,
    'highlightbackground': scheme.label_title_fg,
    'highlightcolor': scheme.label_title_fg,
    'highlightthickness': 1,
})

tk.Menubutton = from_dic(tk.Menubutton, lambda: {
    'bg': scheme.bg, 'fg': scheme.fg, 'width': 8, 'relief': tk.FLAT
})

tk.Checkbutton = from_dic(tk.Checkbutton, lambda: {
    **get_button_dic(),
    'bg': scheme.bg, 'anchor': 'w', 'selectcolor': scheme.bg_extreme
})

tk.PanedWindow = from_dic(tk.PanedWindow, lambda: {
    'bg': scheme.sash, 'sashwidth': 2, 'sashpad': 0,
    'showhandle': 0, 'borderwidth': 0, 'sashrelief': tk.RAISED
})

tk.Text = from_dic(tk.Text, lambda: {
    'bg': scheme.bg, 'fg': scheme.fg, 'font': tk.font.Font(size=12),
    'padx': 12, 'pady': 12,
    'highlightthickness': 0, 'borderwidth': 0, 'relief': tk.FLAT,
})

tk.Scrollbar = from_dic(tk.Scrollbar, lambda: {'bg': scheme.bu})

tk.Canvas = from_dic(tk.Canvas, lambda: {'bg': scheme.bu})

tk.Entry = from_dic(tk.Entry, lambda: {
    'bg': scheme.bg, 'fg': scheme.fg, 'bd': 0
})

tk.Label = from_dic(tk.Label, lambda: {
    'bg': scheme.bg, 'fg': scheme.fg
})


def children_do(widget, callback):
    """Recurse and call callback for all tk descendant
    callback: function(widget)
    """
    for item in widget.winfo_children():
        callback(item)
        children_do(item, callback)


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
    scheme = ColorScheme(in_scheme)
    for widget in (root, *root.saved_children):
        children_do(widget, update_widget_skin)


######################################################################
#           Hover info (alias tool tip)
######################################################################


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


def tk_bind_widget_hover(self):
    def enter(_):
        self.hover_info.hide()
        self.hover_info.show(self.hover_text)
    def leave(_):
        self.hover_info.hide()
    self.bind('<Enter>', enter)
    self.bind('<Leave>', leave)

def tk_set_hover_info(self, text):
    """Set hover info to widget"""
    self.hover_info = HoverInfo(self)
    self.hover_text = text
    self.bind_widget_hover()

# Create widget member function to add info on hover
tk.Widget.bind_widget_hover = tk_bind_widget_hover
tk.Widget.set_hover_info = tk_set_hover_info


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


######################################################################
#           Top level (alias root), kee track of children
######################################################################


# Replace Tk to keep a refrence to change color (very important)
tk.Tk_save = tk.Tk
class tk_Tk(tk.Tk_save):
    """A root that is added tho children and remove on delete"""
    def __init__(self):
        super().__init__()
        if get_root() is None: return

        # Bind close
        def on_close():
            get_root().saved_children.remove(self)
            self.destroy()
        self.protocol("WM_DELETE_WINDOW", on_close)
        get_root().saved_children.append(self)

        # Bind root binding
        for text, cmd in get_root().l_bind:
            self.bind_all(text, cmd)

tk.Tk = tk_Tk

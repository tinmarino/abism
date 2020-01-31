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

from abism.util import log


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



tk.Button = Button

tk.Menubutton = from_dic(tk.Menubutton, lambda: {
    'bg': scheme.bg, 'fg': scheme.fg, 'width': 8, 'relief': tk.FLAT
})

tk.Checkbutton = from_dic(tk.Checkbutton, lambda: {
    'bg': scheme.bg, 'anchor': 'w', 'selectcolor': scheme.bg_extreme
})

tk.Frame = from_dic(tk.Frame, lambda: {'bg': scheme.bg})
# Helpers

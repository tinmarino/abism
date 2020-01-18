"""
    Menu click on Abism tab
"""
import tkinter as tk

from front.util_front import system_open, about_window, \
    change_scheme, Scheme, skin

from util import quit_process

def AbismMenu(root, parent, args):
    # pylint: disable=unused-argument
    """Create the menu on Abism tab click"""
    menu_button = tk.Menubutton(parent, **args)
    menu_button.menu = tk.Menu(menu_button, **skin().fg_and_bg)

    menu_button.menu.add_command(
        label='About',
        command=about_window)

    menu_button.menu.add_command(
        label='Advanced Manual',
        command=lambda: system_open(path="doc/advanced_manual.pdf"))

    menu_button.menu.add_cascade(
        label="Color Scheme",
        underline=0,
        menu=get_colorscheme_cascade(root, menu_button))

    menu_button.menu.add_command(
        label='Quit',
        command=quit_process)

    menu_button['menu'] = menu_button.menu

    # Caller grid me
    return menu_button


def get_colorscheme_cascade(root, parent):
    """Create the submenu"""
    menu = tk.Menu(parent)

    menu.add_radiobutton(
        label='Dark Solarized',
        command=lambda: change_scheme(root, Scheme.DARK_SOLARIZED))

    menu.add_radiobutton(
        label='Light Solarized',
        command=lambda: change_scheme(root, Scheme.LIGHT_SOLARIZED))

    return menu

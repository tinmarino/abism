"""
    Menu click on Abism tab
"""
import tkinter as tk

from front.util_front import system_open, about_window, quit_process, \
    change_scheme, Scheme
import front.util_front as G


def AbismMenu(root, parent, args):
    # pylint: disable=unused-argument
    """Create the menu on Abism tab click"""
    menu_button = tk.Menubutton(parent, **args)
    menu_button.menu = tk.Menu(menu_button, **G.submenu_args)

    lst = [
        ["About", about_window],
        ["Advanced Manual",
         lambda: system_open(path="doc/advanced_manual.pdf")],
        ["Color Dark",
         lambda: change_scheme(root, Scheme.DARK_SOLARIZED)],
        ["Quit", quit_process],
    ]
    for i in lst:
        if "Appearance" in i[0]:
            i[1]()
        else:
            menu_button.menu.add_command(label=i[0], command=i[1])

    menu_button['menu'] = menu_button.menu

    # Caller grid me
    return menu_button



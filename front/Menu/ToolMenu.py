"""
    Menu for some other tools (in plugin)
"""
import tkinter as Tk

import Pick  # to connect PickOne per defautl

from plugin.DebugConsole import PythonConsole
from plugin.Histogram import Histopopo

import GuyVariables as G


def ToolMenu(root, parent, args):
    """Only function"""
    G.tool_menu = Tk.Menubutton(parent, **args)
    G.tool_menu.menu = Tk.Menu(G.tool_menu, **G.submenu_args)

    lst = [
        ["Profile", lambda: Pick.RefreshPick("profile")],
        ["Stat", lambda: Pick.RefreshPick("stat")],
        ["Histogram", Histopopo],
        ["Python Console", PythonConsole],
    ]
    for i in lst:
        G.tool_menu.menu.add_command(label=i[0], command=i[1])

    G.tool_menu['menu'] = G.tool_menu.menu

    return G.tool_menu

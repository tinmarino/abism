import GuyVariables as G
import MyGui as MG  # TODO remove that
import Pick  # to connect PickOne per defautl
import DebugConsole  # For pythonConsole

import tkinter as Tk
import LaunchCalculator  # TODO put taht in pluggins


def ToolMenu(args):
    G.tool_menu = Tk.Menubutton(G.MenuBar, **args)
    G.tool_menu.menu = Tk.Menu(G.tool_menu, **G.submenu_args)

    lst = [
       ["Profile"   ,  lambda: Pick.RefreshPick("profile") ],
       ["Stat"      ,  lambda: Pick.RefreshPick("stat") ],
       [ "Histogram", MG.Histopopo ],
       [ "Python Console", DebugConsole.PythonConsole ],
       [ u'\u25be '+'Calculator', LaunchCalculator.Calculator],
    ]
    for i in lst:
        G.tool_menu.menu.add_command(label=i[0], command=i[1])

    G.tool_menu['menu'] = G.tool_menu.menu

    return G.tool_menu

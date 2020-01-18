"""
    Menu for some other tools (in plugin)
"""
import tkinter as Tk


from plugin.DebugConsole import PythonConsole
from plugin.Histogram import Histopopo

from front import Pick  # to connect PickOne per defautl
from front.util_front import skin


def ToolMenu(root, parent, args):
    """Only function"""
    # pylint: disable=unused-argument
    tool_menu = Tk.Menubutton(parent, **args)
    tool_menu.menu = Tk.Menu(tool_menu, **skin().fg_and_bg)

    lst = [
        ["Profile", lambda: Pick.RefreshPick("profile")],
        ["Stat", lambda: Pick.RefreshPick("stat")],
        ["Histogram", lambda: Histopopo(
            root.FitFrame.get_figure(),
            root.image.sort,
            fg=skin().fg_and_bg['fg'])],
        ["Python Console", PythonConsole],
    ]
    for i in lst:
        tool_menu.menu.add_command(label=i[0], command=i[1])

    tool_menu['menu'] = tool_menu.menu

    return tool_menu

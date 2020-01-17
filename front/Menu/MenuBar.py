from tkinter import *

import FileMenu
import AbismMenu
import AnalysisMenu
import ToolMenu
import ViewMenu

from front.util_front import skin
import front.util_front as G


def MenuBarMaker(root):
    """Create the menu bar (autopack top)"""

    # Pack bar at top
    menu_bar = Frame(G.parent, bg=skin().color.bg)
    menu_bar.pack(side=TOP, expand=0, fill=X)

    # Prepare argument dic
    args = G.me_arg.copy()
    args.update({"relief": FLAT, "width": G.menu_button_width})

    # For all menu button (tab)
    for col, i in enumerate([
            [AbismMenu.AbismMenu, {"text": u"\u25be "+"ABISM"}],
            [FileMenu.FileMenu, {"text": u"\u25be "+"File"}],
            [AnalysisMenu.AnalysisMenu, {"text": u'\u25be '+'Analysis'}],
            [ViewMenu.ViewMenu, {"text": u'\u25be '+'View'}],
            [ToolMenu.ToolMenu, {"text": u'\u25be '+'Tools'}],
                ]):
        # Same weight
        menu_bar.columnconfigure(col, weight=1)
        # Prepare button args
        args.update(i[1])
        # Create button
        button = i[0](root, menu_bar, args)
        # Grid it
        button.grid(row=0, column=col, sticky="nsew")

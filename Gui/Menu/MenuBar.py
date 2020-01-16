from tkinter import *

import FileMenu
import AbismMenu
import AnalysisMenu
import ToolMenu
import ViewMenu

import GuyVariables as G
import WorkVariables as W

import MyGui as MG  # TODO remove that
import InitGui as IG


def MenuBarMaker():             # CALLER
    global args                 # the args of "MenuButton"

    G.MenuBar = Frame(G.parent, bg=G.bg[0])
    G.all_frame.append("G.MenuBar")
    G.MenuBar.pack(side=TOP, expand=0, fill=X)

    col = 0
    args = G.me_arg.copy()
    args.update({"relief": FLAT, "width": G.menu_button_width})
    for i in [
        [AbismMenu.AbismMenu, {"text": u"\u25be "+"ABISM"}],
        [FileMenu.FileMenu, {"text": u"\u25be "+"File"}],
        [AnalysisMenu.AnalysisMenu,  {"text": u'\u25be '+'Analysis'}],
        [ViewMenu.ViewMenu,  {"text": u'\u25be '+'View'}],
        [ToolMenu.ToolMenu,  {"text": u'\u25be '+'Tools'}],
    ]:
        args.update(i[1])
        button = i[0](args)
        G.MenuBar.columnconfigure(col, weight=1)
        button.grid(row=0, column=col, sticky="nsew")

        col += 1

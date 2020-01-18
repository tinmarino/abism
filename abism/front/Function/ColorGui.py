from tkinter import *

from abism.front.util_front import skin
import abism.front.util_front as G
import abism.back.util_back as W

import abism.util


def BgCl(color=None, who="bg"):
    """
        # Background COlor, change the color of ABism take skin().color.bg t
        # Defined colors, set bg, fg, lists
    """
    if color is not None:
        vars(G)[who][0] = color
    color = vars(G)[who][0]

    # update some dics
    GlobalDefiner.LinkedColor()  # to reload dictionnaries

    def Frames():  # BG for frames in all_frame
        for i in G.all_frame:
            if "Paned" not in i:
                log(7, i)
            try:
                exec(i + "['bg'] = skin().color.bg") in globals(), locals()
                # remove 2 first letter because it is G.
                # done for sed , not Paned please
            except:
                pass

    def Canvas():  # BG for figure
        G.fig.set_facecolor(color)
        G.fig.canvas.draw()
        G.figfit.set_facecolor(color)
        G.figfit.canvas.draw()
        G.figresult.set_facecolor(color)
        G.figresult.canvas.draw()
        for i in G.toolbar.winfo_children():
            i[who] = color

    def MenuBut():
        for i in G.MenuBar.winfo_children():
            i[who] = color
            BackgroundLoop(i, who=who)

    def Rest():
        BackgroundLoop(G.TextPaned, who=who)

    if who == "bg":
        Frames()
    if who == "bg":
        Canvas()
    MenuBut()
    Rest()   # textframe
    return


def BackgroundLoop(widget, who="bg"):
    """
        read var[0], G.fb Colorize all Label and Frame children,
        # WIDGETS TO CHANGE, do not change others
    """
    if who == "bg":
        bolt = (widget.winfo_class() == "Label")
        bolt = bolt or (widget.winfo_class() == "Frame")
        bolt = bolt or (widget.winfo_class() == "Menu")
        bolt = bolt or (widget.winfo_class() == "Checkbutton")
    elif who == "fg":
        bolt = (widget.winfo_class() == "Label")
        bolt = bolt or (widget.winfo_class() == "Menu")
        bolt = bolt or (widget.winfo_class() == "Checkbutton")
        bolt = bolt or (widget.winfo_class() == "Button")

    bolt = bolt and (widget["bg"] != skin().label_title_dic['bg'])
    # not change title of frames

    if bolt:
        widget[who] = vars(G)[who][0]

    for i in widget.winfo_children():
        BackgroundLoop(i, who=who)
    return

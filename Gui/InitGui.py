"""
    Half os the gui initiallisation is here
"""
import re
import os.path          # For the Icon

from tkinter import *

import MyGui as MG

from MenuBar import MenuBarMaker
from FramePlot import RightFrame
from FrameText import LeftFrame

import GuyVariables as G
import WorkVariables as W


##################
# 0/ Main Caller
#################

def WindowInit():
    """Init main Frame"""
    # Create MenuBar and MainPaned, TextFrame and DrawFrame
    # 1 TOP
    MenuBarMaker()

    # ALL What is not the menu is a paned windows :
    # I can rezie it with the mouse from left to right,
    # This (all but not the Menu) Frame is called MainPaned
    G.MainPaned = PanedWindow(G.parent, orient=HORIZONTAL, **G.paned_dic)
    G.MainPaned.pack(side=TOP, fill=BOTH, expand=1)

    # 2 LEFT
    G.TextFrame = LeftFrame(G.MainPaned)

    # 3 RIGHT
    G.DrawPaned = RightFrame(G.MainPaned)



    ######################
    ### 4/  MORE FRAMES if click on some buttons  #
    ######################


def TitleArrow(title, var):
    # TITEL
    if G.in_arrow_frame is None:
        G.arrtitle = Label(G.LeftTopArrowFrame,
                           text=title, **G.frame_title_arg)
        G.arrtitle.pack(side=LEFT, anchor="nw")
        G.in_arrow_frame = var
        return True
    else:
        return False


def ManualBackground():
    if G.manual_back_bool:
        ManualBackClose()

    else:  # including no manula_back_bool
        W.type["noise"] = "manual"
        G.manual_back_bool = not G.manual_back_bool
        G.ManualBackFrame = Frame(G.OptionFrame, bg=G.bg[0])
        G.all_frame.append("G.ManualBackFrame")
        G.ManualBackFrame.pack(side=TOP, expand=0, fill=X)

        G.ManualBackFrame.columnconfigure(0, weight=1)
        G.ManualBackFrame.columnconfigure(1, weight=1)

        def GetValue(event):
            G.background = float(G.tkvar.background.get())
            if W.verbose > 2:
                print("InitGui.py/ManualBack, called , ", G.background)

        # ENTRY
        Label(G.ManualBackFrame, text="Background value:",
              font=G.font_param, **G.lb_arg).grid(row=0, column=0, sticky="snew")
        G.tkvar.background = StringVar()
        G.tkentry.background = Entry(
            G.ManualBackFrame, width=10, textvariable=G.tkvar.background, font=G.font_param, **G.en_arg)
        G.tkentry.background.grid(row=0, column=1, sticky="nsew")  # ,sticky=W)
        G.tkentry.background.bind('<Return>', GetValue)
        G.tkvar.background.set("0.0")
        if "background" in vars(G):
            G.tkvar.background.set(str(G.background))

        ###############
        # CLOSE button
        G.bu_back_close = Button(G.ManualBackFrame, text=u'\u25b4 ' + 'Close',
                                 background=G.bu_close_color, command=ManualBackClose, **G.bu_arg)
        G.bu_back_close.grid(row=1, column=0, columnspan=2)
        if W.verbose > 3:
            print("Manual Back called")


def ManualBackClose():
    G.manual_back_bool = not G.manual_back_bool
    G.ManualBackFrame.destroy()
    G.all_frame = [x for x in G.all_frame if x !=
                   "G.ManualBackFrame"]  # remove Frame

    G.background = float(G.tkvar.background.get())


def PanedConfig(arg):
    """Change paned window canvas..."""
    for i in G.all_frame:
        if not "Paned" in i: continue
        W.log(3, "Changing", i)
        for j in arg:
            vars(G)[i[2:]][j] = arg[j]


def ManualCut():
    if G.manual_cut_bool:
        ManualCutClose()

    else:  # including no manula_cut_bool
        G.OptionFrame.toogle(see=False)
        G.OptionFrame.toogle(see=True)
        G.manual_cut_bool = not G.manual_cut_bool
        G.ManualCutFrame = Frame(G.OptionFrame, bg=G.bg[0])
        G.all_frame.append("G.ManualCutFrame")
        G.ManualCutFrame.pack(side=TOP, expand=0, fill=X)

        Label(G.ManualCutFrame, text="Cut image scale", **
              G.frame_title_arg).pack(side=TOP, anchor="w")

        G.ManualCutGridFrame = Frame(G.ManualCutFrame, bg=G.bg[0])
        G.all_frame.append("G.ManualCutGridFrame")
        G.ManualCutGridFrame.pack(side=TOP, expand=0, fill=X)

        G.ManualCutGridFrame.columnconfigure(0, weight=1)
        G.ManualCutGridFrame.columnconfigure(1, weight=1)

        def GetValue(event):
            dic = {"min_cut": float(G.entries[1].get()),
                   "max_cut": float(G.entries[0].get())}
            W.log(2, "InitGui.py/ManualCut, dic called , ", dic)
            MG.Scale(dic=dic)  # Call MyGui

        lst = [["Max cut", "max_cut"], ["Min cut", "min_cut"]]
        G.entries = []
        r = 0
        for i in lst:
            G.l = Label(G.ManualCutGridFrame,
                        text=i[0], font=G.font_param, **G.lb_arg)
            G.l.grid(row=r, column=0, sticky="snew")  # , sticky=W)
            v = StringVar()
            G.e = Entry(G.ManualCutGridFrame, width=10,
                        textvariable=v, font=G.font_param, **G.en_arg)
            G.e.grid(row=r, column=1, sticky="nsew")  # , sticky=W)
            G.e.bind('<Return>', GetValue)
            v.set("%.1f" % G.scale_dic[0][i[1]])
            G.entries.append(v)
            r += 1

        ###############
        # CLOSE button
        G.bu_close = Button(G.ManualCutGridFrame, text=u'\u25b4 ' + 'Close',
                            background=G.bu_close_color, command=ManualCutClose, **G.bu_arg)
        G.bu_close.grid(row=r, column=0, columnspan=2)
        if W.verbose > 3:
            print("Manual Cut called")


def ManualCutClose():
    """Stop Manual cut"""
    # Remove frame
    G.manual_cut_bool = not G.manual_cut_bool
    G.ManualCutFrame.destroy()
    G.all_frame = [x for x in G.all_frame if x !=
                   'G.ManualCutFrame']

    # Update scale
    G.scale_dic[0]['max_cut'] = float(G.entries[0].get())
    G.scale_dic[0]['min_cut'] = float(G.entries[1].get())
    W.log(3, 'Cut min, max:', G.scale_dic[0]['min_cut'], G.scale_dic[0]['max_cut'])
    MG.Scale()

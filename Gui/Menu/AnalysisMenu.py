import tkinter as Tk

import GuyVariables as G
import WorkVariables as W

import Pick

import MyGui as MG    # TODO must be removed
import MenuBar        # TODO must removed that too
import InitGui as IG  # TODO must be removed too

"""
             #TODO ["Ellipse"   , "ellipse" ,
             lambda: Pick.RefreshPick("ellipse") ] ,
             #TODO ["Annulus"   , "annulus" ,
             lambda: Pick.RefreshPick("annulus") ],
             #TODO ["Tight Binary", "tightbinary"  ,
             lambda: Pick.RefreshPick("tightbinary") ] ,
             #["Gaussian_hole" ,  "Gaussian_hole"   ,
             lambda: MG.FitType("Gaussian_hole" )],
             #  ["InRectangle", "in_rectangle" ] ,

"""


def AnalysisMenu(args):     # Create the Menu button and its children
    G.analysis_menu = Tk.Menubutton(G.MenuBar, **args)
    G.analysis_menu.menu = Tk.Menu(G.analysis_menu, **G.submenu_args)

    def FitType():
        fit_menu = G.analysis_menu.menu
        fit_menu.add_command(label="Fit Type", bg=None, state=Tk.DISABLED)

        G.cu_fit = Tk.StringVar()
        G.cu_fit.set(W.type["fit"].replace("2D", ""))
        lst1 = [
            ["Gaussian", "Gaussian", lambda: MG.FitType("Gaussian")],
            ["Moffat",   "Moffat", lambda: MG.FitType("Moffat")],
            ["Bessel1",  "Bessel1", lambda: MG.FitType("Bessel1")],
            ["None",     "None", lambda: MG.FitType("None")],
        ]
        for i in lst1:
            fit_menu.add_radiobutton(
                label=i[0], command=i[2],
                variable=G.cu_fit, value=i[1])  # we use same value as label

        # MORE OPTIONS
        if not G.more_bool:
            G.analysis_menu.menu.add_command(
                label=u'\u25be '+'More Options', command=MoreWidget)

        else:
            G.analysis_menu.menu.add_command(
                label=u'\u25b4 '+'Less Options',
                command=MenuBar.MoreWidget)

        G.analysis_menu.menu.add_command(columnbreak=1)
        return

    def PickType():
        pick_menu = G.analysis_menu.menu
        pick_menu.add_command(label="Pick Object(s)",
                              bg=None,
                              state=Tk.DISABLED)

        # more options
        G.cu_pick = Tk.StringVar()
        G.cu_pick.set(W.type["pick"])
        lst2 = [
            ["PickOne", "one", lambda: Pick.RefreshPick("one")],
            ["Binary Fit", "binary", lambda: Pick.RefreshPick("binary")],
            ["PickMany", "many", lambda: Pick.RefreshPick("many")],
            ["No Pick", "nopick", lambda: Pick.RefreshPick("nopick")],
        ]

        for i in lst2:
            pick_menu.add_radiobutton(
                label=i[0], command=i[2],
                variable=G.cu_pick, value=i[1])  # we use same value as label

    FitType()
    PickType()
    G.analysis_menu['menu'] = G.analysis_menu.menu
    return G.analysis_menu


def MoreWidget():       # More photometry options frame
    ""

    # Change  menu label more option -> less option
    for i in range(1, 10):
        j = G.analysis_menu.menu.entrycget(i, "label")
        if "Option" in j:
            if G.more_bool:
                G.analysis_menu.menu.entryconfig(
                    i, label=u'\u25be '+'More Option')
                break
            else:
                G.analysis_menu.menu.entryconfig(
                    i, label=u'\u25b4 '+'Less Option')
                break

    # CHANGE BOOL MAY CLOSE
    if G.more_bool == 1:  # close more frame
        MoreClose()

    else:  # CREATE
        MoreCreate()

    return


def MoreCreate():       # Create The Frame
    G.more_bool = not G.more_bool  # mean = 1
    G.OptionFrame.toogle(visible=True)

    # #########""
    # FRAME
    # create the more_staff Frame
    G.MoreFrame = Tk.Frame(G.OptionFrame, bg=G.bg[0])
    G.all_frame.append("G.MoreFrame")
    G.MoreFrame.grid(sticky='nsew')

    Tk.Label(G.MoreFrame,
             text="More Options",
             **G.frame_title_arg).pack(side=Tk.TOP, anchor="w")

    #
    G.MoreGridFrame = Tk.Frame(G.MoreFrame, bg=G.bg[0])
    G.all_frame.append("G.MoreGridFrame")
    G.MoreGridFrame.pack(side=Tk.TOP, expand=0, fill=Tk.X)
    G.MoreGridFrame.columnconfigure(0, weight=1)
    G.MoreGridFrame.columnconfigure(1, weight=1)
    ""

    def SubtractBackground(frame):
        ""
        G.bu_subtract_bg = Tk.Button(frame,
                                     text='SubstractBackground',
                                     background=G.bu_subtract_bg_color,
                                     command=MG.SubstractBackground,
                                     **G.bu_arg)
        return G.bu_subtract_bg

    def NoiseType(frame):
        ""
        G.menu_noise = Tk.Menubutton(frame,
                                     text=u'\u25be '+'Background',
                                     relief=Tk.RAISED,
                                     background=G.menu_noise_color,
                                     **G.bu_arg)
        G.menu_noise.menu = Tk.Menu(G.menu_noise)

        G.cu_noise = Tk.StringVar()
        G.cu_noise.set(W.type["noise"])

        lst = [
            ["Annulus", "elliptical_annulus"],
            ['Fit', 'fit'],
            ["8Rects", "8rects"],
            ['Manual', "manual"],
            ["None", "None"],
        ]
        for i in lst:
            if i[0] == "Manual":
                G.menu_noise.menu.add_radiobutton(
                    label=i[0], command=IG.ManualBackground,
                    variable=G.cu_noise, value=i[1])
            else:
                def set_noise(i): W.type['noise'] = i[1]
                G.menu_noise.menu.add_radiobutton(
                    label=i[0], command=set_noise,
                    variable=G.cu_noise, value=i[1])

        G.menu_noise['menu'] = G.menu_noise.menu
        return G.menu_noise

    def PhotType(frame):
        G.menu_phot = Tk.Menubutton(frame, text=u'\u25be '+'Photometry',
                                    relief=Tk.RAISED, background=G.menu_phot_color, **G.bu_arg)
        G.menu_phot.menu = Tk.Menu(G.menu_phot)

        G.cu_phot = Tk.StringVar()
        G.cu_phot.set(W.type["phot"])

        lst = [
            ['Elliptical Aperture', 'elliptical_aperture'],
            ['Fit', 'fit'],
            ['Rectangle Aperture', 'encircled_energy'],
            ['Manual', 'manual'],
        ]

        for i in lst:
            def set_phot(i): W.type['phot'] = i[1]
            G.menu_phot.menu.add_radiobutton(
                label=i[0], command=set_phot,
                variable=G.cu_phot, value=i[1])

        G.menu_phot['menu'] = G.menu_phot.menu
        return G.menu_phot

    def Check(frame):
        myargs = {"anchor": "w", "bg": G.bg[0], "fg": G.fg[0],
                  "padx": 0, "pady": 0, "highlightthickness": 0}
        ################
        # isoplanetism
        G.iso_check = Tk.Checkbutton(frame,
                                     text="Anisomorphism", variable=W.aniso_var,
                                     command=lambda: MG.FitType(W.type["fit"]), **myargs)  # by default onvalue=1

        G.same_check = Tk.Checkbutton(G.MoreGridFrame,
                                      text="Binary_same_psf", variable=W.same_psf_var,
                                      command=lambda: MG.FitType(W.type["fit"]), **myargs)

        G.same_center_check = Tk.Checkbutton(G.MoreGridFrame,
                                             text="Saturated_same_center", variable=W.same_center_var,
                                             command=lambda: MG.FitType(W.type["fit"]), **myargs)

        return G.iso_check, G.same_check, G.same_center_check

    SubtractBackground(G.MoreGridFrame).grid(row=0, column=0,
                                             columnspan=2, sticky="nswe")
    NoiseType(G.MoreGridFrame).grid(row=1, column=0, sticky="nswe")
    PhotType(G.MoreGridFrame).grid(row=1, column=1, sticky="nswe")

    row = 2
    for i in Check(G.MoreGridFrame):
        i.grid(row=row, column=0, columnspan=2, sticky="nwse")
        row += 1

    G.bu_close = Tk.Button(G.MoreGridFrame, text=u'\u25b4 '+'Close',
                           background=G.bu_close_color,
                           command=MoreClose, **G.bu_arg)
    G.bu_close.grid(row=row, column=0, columnspan=2)

    return  # From MoreCreate


def MoreClose():        # Close the Frame
    ""
    # change bool destroy
    G.more_bool = not G.more_bool
    G.MoreFrame.destroy()
    if G.in_arrow_frame == "title_more":
        G.arrtitle.destroy()
    G.in_arrow_frame = None

    # REMOVE MOREFRAME AND CHILD
    G.all_frame = [x for x in G.all_frame if x != "G.MoreFrame"]

    # Change help menu label
    for i in range(1, 10):
        j = G.analysis_menu.menu.entrycget(i, "label")
        if "Option" in j:
            G.analysis_menu.menu.entryconfig(i, label=u'\u25be '+'More Option')
            break

    return

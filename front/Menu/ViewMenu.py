"""
    Menu button view
"""

from tkinter import *
import tkinter as Tk

import WindowRoot as MG

import GuyVariables as G
import WorkVariables as W


def ViewMenu(root, parent, args):
    """Create the menu"""
    G.scale_menu = Menubutton(parent, **args)
    G.scale_menu.menu = Menu(G.scale_menu, **G.submenu_args)

    def Color():
        """Color drop"""
        if G.scale_menu_type == "cascade":
            color_menu = Menu(G.scale_menu, **G.submenu_args)
        else:
            color_menu = G.scale_menu.menu
        color_menu.add_command(label="COLOR", bg=None, state=DISABLED)
        # if we don't want cascade, we just add in the menu

        G.cu_color = StringVar()
        G.cu_color.set(G.scale_dic[0]["cmap"])  # because image not loaded yet

        # "
        # My colors
        lst = [
            ["Jet", "jet"],
            ['Black&White', 'bone'],
            ['Spectral', 'spectral'],
            ["RdYlBu", "RdYlBu"],
            ["BuPu", "BuPu"]
        ]
        for i in lst:
            color_menu.add_radiobutton(
                label=i[0], command=lambda i=i: G.ImageFrame.CutImageScale(
                    dic={"cmap": i[1]}, run="G.cu_cut.set('"+i[1] + "')"),
                variable=G.cu_color, value=i[1])  # we use same value as label

        ########
        # Contour
        color_menu.add_command(
            label='Contour', command=lambda: G.ImageFrame.CutImageScale(
                dic={"contour": 'not a bool'}))

        #################
        # more colors
        more_color_menu = Menu(color_menu, **G.submenu_args)
        num = 0
        for i in G.all_cmaps:
            num += 1
            more_color_menu.add_radiobutton(
                label=i,
                command=lambda i=i: G.ImageFrame.CutImageScale(dic={"cmap": i}),
                variable=G.cu_color, value=i)  # we use same value as label

            if num % 30 == 0:
                more_color_menu.add_radiobutton(
                    label=i,
                    command=lambda i=i: G.ImageFrame.CutImageScale(dic={"cmap": i}),
                    variable=G.cu_color, value=i, columnbreak=1)  # we use same value as label
        color_menu.add_cascade(menu=more_color_menu,
                               label="More colors", underline=0)

        if G.scale_menu_type == "cascade":
            G.scale_menu.menu.add_cascade(
                menu=color_menu, underline=0, label="Color")
        else:
            G.scale_menu.menu.add_command(columnbreak=1)

    def Scale():
        """Scale of image drop"""
        if G.scale_menu_type == "cascade":
            scale_menu = Menu(G.scale_menu, **G.submenu_args)
        else:
            scale_menu = G.scale_menu.menu
        scale_menu.add_command(label="FCT", bg=None, state=DISABLED)

        G.cu_scale = StringVar()
        G.cu_scale.set(G.scale_dic[0]["stretch"])
        lst = [["Lin", "x", "linear"], ["Sqrt", "x**0.5", "sqrt"], ["Square", "x**2",
                                                                    "square"], ["Log", "np.log(x+1)/0.69", "log"], ["Arcsinh", "", "arcsinh"]]
        for i in lst:
            scale_menu.add_radiobutton(label=i[0],
                                       command=lambda i=i: G.ImageFrame.CutImageScale(
                                           dic={"fct": i[1], "stretch": i[2]}, run="G.cu_scale.set('" + i[2] + "')"),
                                       variable=G.cu_scale, value=i[2])  # we use same value as label

        if G.scale_menu_type == "cascade":
            G.scale_menu.menu.add_cascade(
                menu=scale_menu, underline=0, label="Fct")
        else:
            G.scale_menu.menu.add_command(columnbreak=1)

    def Cut():
        """Cut min max of the iamge scale"""
        if G.scale_menu_type == "cascade":
            cut_menu = Menu(G.scale_menu, **G.submenu_args)
        else:
            cut_menu = G.scale_menu.menu
        cut_menu.add_command(label="CUTS", bg=None, state=DISABLED)

        G.cu_cut = StringVar()
        G.cu_cut.set("RMS")
        # label , scale_cut_type, key, value
        lst = [["RMS", "sigma_clip", "sigma", 3],
               ["99.95%", "percent", "percent", 99.95],
               ["99.9%", "percent", "percent", 99.9],
               ["99%", "percent", "percent", 99],
               ["90%", "percent", "percent", 90],
               ["None", "None", "truc", "truc"],
               ]
        for i in lst:
            cut_menu.add_radiobutton(label=i[0],
                                     command=lambda i=i: G.ImageFrame.CutImageScale(
                                         dic={"scale_cut_type": i[1], i[2]: i[3]}, run="G.cu_cut.set('"+i[0] + "')"),
                                     variable=G.cu_cut, value=i[0])  # we use same value as label

        cut_menu.add_radiobutton(label="Manual",
                                 command=ManualCut,
                                 variable=G.cu_cut, value="Manual")  # we use same value as label

        if G.scale_menu_type == "cascade":
            G.scale_menu.menu.add_cascade(
                menu=cut_menu, underline=0, label="Cut")
        else:
            G.scale_menu.menu.add_command(columnbreak=1)

    Color()
    Scale()
    Cut()
    G.scale_menu['menu'] = G.scale_menu.menu

    return G.scale_menu


def ManualCut():
    """Stupid switch"""
    if G.manual_cut_bool:
        ManualCutClose()
    else:
        ManualCutOpen()


def ManualCutOpen():
    # Prepare
    G.OptionFrame.toogle(visible=True)
    G.manual_cut_bool = not G.manual_cut_bool

    # Pack main
    G.ManualCutFrame = Tk.Frame(G.OptionFrame, bg=G.bg[0])
    G.all_frame.append("G.ManualCutFrame")
    G.ManualCutFrame.grid(sticky='nsew')

    # Pack lave
    Tk.Label(
        G.ManualCutFrame, text="Cut image scale", **
        G.frame_title_arg
        ).pack(side=Tk.TOP, anchor="w")

    G.ManualCutGridFrame = Tk.Frame(G.ManualCutFrame, bg=G.bg[0])
    G.all_frame.append("G.ManualCutGridFrame")
    G.ManualCutGridFrame.pack(side=Tk.TOP, expand=0, fill=Tk.X)

    G.ManualCutGridFrame.columnconfigure(0, weight=1)
    G.ManualCutGridFrame.columnconfigure(1, weight=1)

    def GetValue(event):
        dic = {"min_cut": float(G.entries[1].get()),
                "max_cut": float(G.entries[0].get())}
        W.log(2, "ManualCut, dic called , ", dic)
        G.ImageFrame.CutImageScale(dic=dic)

    lst = [["Max cut", "max_cut"], ["Min cut", "min_cut"]]
    G.entries = []
    r = 0
    for i in lst:
        G.l = Tk.Label(G.ManualCutGridFrame,
                        text=i[0], font=G.font_param, **G.lb_arg)
        G.l.grid(row=r, column=0, sticky="snew")  # , sticky=W)
        v = Tk.StringVar()
        G.e = Tk.Entry(G.ManualCutGridFrame, width=10,
                        textvariable=v, font=G.font_param, **G.en_arg)
        G.e.grid(row=r, column=1, sticky="nsew")  # , sticky=W)
        G.e.bind('<Return>', GetValue)
        v.set("%.1f" % G.scale_dic[0][i[1]])
        G.entries.append(v)
        r += 1

    ###############
    # CLOSE button
    G.bu_close = Tk.Button(
        G.ManualCutGridFrame, text=u'\u25b4 ' + 'Close',
        background=G.bu_close_color, command=ManualCutClose, **G.bu_arg)
    G.bu_close.grid(row=r, column=0, columnspan=2)
    W.log(3, "Manual Cut called")


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
    G.ImageFrame.CutImageScale()



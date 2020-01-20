"""
    Menu bar to choose the fit type
"""
import tkinter as tk

from abism.front import Pick
from abism.front.util_front import skin, TitleLabel
import abism.front.util_front as G

import abism.back.util_back as W

from abism.util import log, get_root

"""
             #TODO ["Ellipse"   , "ellipse" ,
             lambda: Pick.RefreshPick("ellipse") ] ,
             #TODO ["Annulus"   , "annulus" ,
             lambda: Pick.RefreshPick("annulus") ],
             #TODO ["Tight Binary", "tightbinary"  ,
             lambda: Pick.RefreshPick("tightbinary") ] ,
             #["Gaussian_hole" ,  "Gaussian_hole"   ,
             #  ["InRectangle", "in_rectangle" ] ,

"""


def AnalysisMenu(root, parent, args):
    """Create the Menu button and its children"""
    menu_button = tk.Menubutton(parent, **args)
    menu_button.menu = tk.Menu(menu_button, **skin().fg_and_bg)

    ##############################
    # FitType
    fit_menu = menu_button.menu
    fit_menu.add_command(label="Fit Type", bg=None, state=tk.DISABLED)

    G.cu_fit = tk.StringVar()
    G.cu_fit.set(W.type["fit"].replace("2D", ""))
    lst1 = [
        ["Gaussian", "Gaussian", lambda: SetFitType("Gaussian")],
        ["Moffat",   "Moffat", lambda: SetFitType("Moffat")],
        ["Bessel1",  "Bessel1", lambda: SetFitType("Bessel1")],
        ["None",     "None", lambda: SetFitType("None")],
    ]
    for i in lst1:
        fit_menu.add_radiobutton(
            label=i[0], command=i[2],
            variable=G.cu_fit, value=i[1])  # we use same value as label

    # MORE OPTIONS
    if not G.more_bool:
        menu_button.menu.add_command(
            label=u'\u25be '+'More Options',
            command=lambda: MoreWidget(menu_button))
    else:
        menu_button.menu.add_command(
            label=u'\u25b4 '+'Less Options',
            command=lambda: MoreWidget(menu_button))

    menu_button.menu.add_command(columnbreak=1)

    ###############################
    # Pick type
    pick_menu = menu_button.menu
    pick_menu.add_command(label="Pick Object(s)",
                            bg=None,
                            state=tk.DISABLED)

    # more options
    G.cu_pick = tk.StringVar()
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


    menu_button['menu'] = menu_button.menu

    # Caller grid me
    return menu_button


parent_more = None

def MoreWidget(parent):
    """More photometry options frame"""
    global parent_more
    parent_more = parent

    # Change  menu label more option -> less option
    for i in range(1, 10):
        j = parent.menu.entrycget(i, "label")
        if "Option" in j:
            if G.more_bool:
                parent.menu.entryconfig(
                    i, label=u'\u25be '+'More Option')
                break
            else:
                parent.menu.entryconfig(
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

    # #########""
    # FRAME
    # create the more_staff Frame
    G.MoreFrame = tk.Frame(get_root().OptionFrame, bg=skin().color.bg)
    G.all_frame.append("G.MoreFrame")
    G.MoreFrame.grid(sticky='nsew')

    label_more = TitleLabel(G.MoreFrame, text="More Options")
    label_more.pack(side=tk.TOP, anchor="w")

    #
    G.MoreGridFrame = tk.Frame(G.MoreFrame, bg=skin().color.bg)
    G.all_frame.append("G.MoreGridFrame")
    G.MoreGridFrame.pack(side=tk.TOP, expand=0, fill=tk.X)
    G.MoreGridFrame.columnconfigure(0, weight=1)
    G.MoreGridFrame.columnconfigure(1, weight=1)

    def SubtractBackground(frame):
        ""
        G.bu_subtract_bg = tk.Button(frame,
                                     text='SubstractBackground',
                                     command=SubstractBackground,
                                     **skin().button_dic)
        return G.bu_subtract_bg

    def set_noise(i):
        W.type['noise'] = i

    def set_phot(i):
        W.type['phot'] = i

    def NoiseType(frame):
        ""
        G.menu_noise = tk.Menubutton(frame,
                                     text=u'\u25be '+'Background',
                                     relief=tk.RAISED,
                                     **skin().button_dic)
        G.menu_noise.menu = tk.Menu(G.menu_noise)

        G.cu_noise = tk.StringVar()
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
                    label=i[0], command=ManualBackground,
                    variable=G.cu_noise, value=i[1])
            else:
                G.menu_noise.menu.add_radiobutton(
                    label=i[0], command=lambda : set_noise(i[1]),
                    variable=G.cu_noise, value=i[1])

        G.menu_noise['menu'] = G.menu_noise.menu
        return G.menu_noise

    def PhotType(frame):
        G.menu_phot = tk.Menubutton(frame, text=u'\u25be '+'Photometry',
                                    relief=tk.RAISED, **skin().button_dic)
        G.menu_phot.menu = tk.Menu(G.menu_phot)

        G.cu_phot = tk.StringVar()
        G.cu_phot.set(W.type["phot"])

        lst = [
            ['Elliptical Aperture', 'elliptical_aperture'],
            ['Fit', 'fit'],
            ['Rectangle Aperture', 'encircled_energy'],
            ['Manual', 'manual'],
        ]

        for i in lst:
            G.menu_phot.menu.add_radiobutton(
                label=i[0], command = lambda: set_phot(i[1]),
                variable=G.cu_phot, value=i[1])

        G.menu_phot['menu'] = G.menu_phot.menu
        return G.menu_phot

    def Check(frame):
        myargs = {"anchor": "w", "bg": skin().color.bg, "fg": skin().color.fg,
                  "padx": 0, "pady": 0, "highlightthickness": 0}
        ################
        # isoplanetism
        G.iso_check = tk.Checkbutton(frame,
                                     text="Anisomorphism", variable=W.aniso_var,
                                     command=lambda: SetFitType(W.type["fit"]), **myargs)  # by default onvalue=1

        G.same_check = tk.Checkbutton(G.MoreGridFrame,
                                      text="Binary_same_psf", variable=W.same_psf_var,
                                      command=lambda: SetFitType(W.type["fit"]), **myargs)

        G.same_center_check = tk.Checkbutton(G.MoreGridFrame,
                                             text="Saturated_same_center", variable=W.same_center_var,
                                             command=lambda: SetFitType(W.type["fit"]), **myargs)

        return G.iso_check, G.same_check, G.same_center_check

    SubtractBackground(G.MoreGridFrame).grid(row=0, column=0,
                                             columnspan=2, sticky="nswe")
    NoiseType(G.MoreGridFrame).grid(row=1, column=0, sticky="nswe")
    PhotType(G.MoreGridFrame).grid(row=1, column=1, sticky="nswe")

    row = 2
    for i in Check(G.MoreGridFrame):
        i.grid(row=row, column=0, columnspan=2, sticky="nwse")
        row += 1

    G.bu_close = tk.Button(G.MoreGridFrame, text=u'\u25b4 '+'Close',
                           command=MoreClose, **skin().button_dic)
    G.bu_close.grid(row=row, column=0, columnspan=2)

    # Redraw
    get_root().OptionFrame.init_will_toogle(visible=True, add_title=False)

    return  # From MoreCreate


def MoreClose():
    """Close the Frame"""
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
        j = parent_more.menu.entrycget(i, "label")
        if "Option" in j:
            parent_more.menu.entryconfig(i, label=u'\u25be '+'More Option')
            break


def ManualBackground():
    """Create manual background frame"""
    if G.manual_back_bool:
        ManualBackClose()
    else:
        ManualBackOpen()
    G.manual_back_bool = not G.manual_back_bool


def ManualBackOpen():
    W.type["noise"] = "manual"
    G.manual_back_bool = not G.manual_back_bool
    G.ManualBackFrame = tk.Frame(get_root().OptionFrame, bg=skin().color.bg)
    G.all_frame.append("G.ManualBackFrame")
    G.ManualBackFrame.pack(side=tk.TOP, expand=0, fill=tk.X)

    G.ManualBackFrame.columnconfigure(0, weight=1)
    G.ManualBackFrame.columnconfigure(1, weight=1)

    def GetValue(event):
        G.background = float(G.tkvar.background.get())
        log(2, "ManualBack, called , ", G.background)

    # ENTRY
    tk.Label(
        G.ManualBackFrame, text="Background value:",
        font=skin().font.param, **skin().fg_and_bg
        ).grid(row=0, column=0, sticky="snew")
    G.tkvar.background = tk.StringVar()
    G.tkentry.background = tk.Entry(
        G.ManualBackFrame, width=10,
        textvariable=G.tkvar.background,
        font=skin().font.param,
        bd=0, **skin().fg_and_bg)
    G.tkentry.background.grid(row=0, column=1, sticky="nsew")  # ,sticky=W)
    G.tkentry.background.bind('<Return>', GetValue)
    G.tkvar.background.set("0.0")
    if "background" in vars(G):
        G.tkvar.background.set(str(G.background))

    ###############
    # CLOSE button
    G.bu_back_close = tk.Button(G.ManualBackFrame, text=u'\u25b4 ' + 'Close',
                                background=G.bu_close_color, command=ManualBackClose, **skin().button_dic)
    G.bu_back_close.grid(row=1, column=0, columnspan=2)
    log(3, "Manual Back called")


def ManualBackClose():
    G.ManualBackFrame.destroy()
    G.all_frame = [x for x in G.all_frame if x !=
                   "G.ManualBackFrame"]  # remove Frame

    G.background = float(G.tkvar.background.get())


def SubstractBackground():
    """Subtract A background image
    Choose a FITS image tho subtract to the current image to get read of the sky
    value or/and the pixel response. This is a VERY basic task that is only
    subtracting 2 images.
    It could be improved but image reduction is not the goal of ABISM
    """
    from tkinter.filedialog import askopenfilename
    from astropy.io import fits

    # Ask for background
    fp_sky = askopenfilename(
        filetypes=[("fitsfiles", "*.fits"), ("allfiles", "*")])
    bg_hdulist = fits.open(fp_sky)

    # Substract and redraw
    bg0 = bg_hdulist[0].data
    if not get_root().image.im0.shape == get_root().image.im0_bg.shape:
        W.Log(0, 'ERROR : Science image and Background image should have the same shape')
        return
    else:
        get_root().image.im0 -= bg0
        G.ImageFrame.draw_image()


def SetFitType(name):  # strange but works
    """Choose Fit Type
    Different fit types: A Moffat fit is setted by default. You can change it. Gaussian, Moffat,Bessel are three parametrics psf. Gaussian hole is a fit of two Gaussians with the same center by default but you can change that in more option in file button. The Gaussian hole is made for saturated stars. It can be very useful, especially because not may other software utilize this fit.
    Why is the fit type really important? The photometry and the peak of the objects utilize the fit. For the photometry, the fit measure the aperture and the maximum is directly taken from the fit. So changing the fit type can change by 5 to 10% your result
    What should I use? For strehl <10% Gaussian, for Strehl>50% Bessel, between these, Moffat.
    Programmers: Strehl@WindowRoot.py calls SeeingPSF@ImageFunction.py which calls BasicFunction.py
    Todo : fastly analyse the situation and choose a fit type consequently
    """
    W.type["fit"] = name
    G.cu_fit.set(name.replace("2D", ""))  # to change radio but, check
    try:
        if W.aniso_var.get() == 0:
            W.type["fit"] = W.type["fit"].replace('2D', '')
        elif W.aniso_var.get() == 1 and not '2D' in W.type["fit"]:
            W.type["fit"] += '2D'
    except BaseException:
        if W.type["fit"].find('2D') == -1:
            W.type["fit"] += '2D'
    if not W.type["fit"].find('None') == -1:
        W.type["fit"] = 'None'

    # Saturated
    if "Gaussian_hole" in W.type["fit"]:
        try:
            # Global even more dirty
            if W.same_center_var.get() == 0:
                W.type["fit"] = W.type["fit"].replace('same_center', '')
                log(0, "same_center : We asssume that the saturation",
                      "is centered at the center of th object")
            elif not 'same_center' in W.type["fit"]:
                W.type["fit"] += "same_center"
                log(0, "not same_center: We asssume that the saturation",
                      "isn't centered at the center of th object")
        except BaseException:
            if not 'same_center' in W.type["fit"]:
                W.type["fit"] += "same_center"
    log(0, 'Fit Type = ' + W.type["fit"])

    # same psf
    if W.same_psf_var.get() == 0:
        W.same_psf = 0
        log(0, "same_psf : We will fit the binary with the same psf")
    elif W.same_psf_var.get() == 1:
        W.same_psf = 1
        log(0, "not same_psf : We will fit each star with independant psf")

    # change the labels
    #G.fit_type_label["text"] = W.type["fit"]

    return



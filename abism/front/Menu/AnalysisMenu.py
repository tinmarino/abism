"""
    Menu bar to choose the fit type
"""
import tkinter as tk

from abism.front import Pick
from abism.front.util_front import skin, TitleLabel, open_backgroud_and_substract
import abism.front.util_front as G

from abism.util import log, get_root, get_state


def AnalysisMenu(parent):
    """Create the Menu button and its children"""
    args = {**skin().menu_dic, 'text': u"\u25be Analysis"}
    menu_button = tk.Menubutton(parent, **args)
    menu_button.menu = tk.Menu(menu_button, **skin().fg_and_bg)
    menu_button['menu'] = menu_button.menu

    ##############################
    # FitType
    fit_menu = menu_button.menu
    fit_menu.add_command(label="Fit Type", bg=None, state=tk.DISABLED)

    G.cu_fit = tk.StringVar()
    G.cu_fit.set(get_state().fit_type.replace("2D", ""))
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
    pick_menu.add_command(
        label="Pick Object(s)", bg=None, state=tk.DISABLED)

    # more options
    G.cu_pick = tk.StringVar()
    G.cu_pick.set(get_state().pick_type)
    lst2 = [
        ["PickOne", "one", lambda: Pick.RefreshPick("one")],
        ["Binary Fit", "binary", lambda: Pick.RefreshPick("binary")],
        # ["PickMany", "many", lambda: Pick.RefreshPick("many")],
        ["No Pick", "nopick", lambda: Pick.RefreshPick("nopick")],
    ]

    for i in lst2:
        pick_menu.add_radiobutton(
            label=i[0], command=i[2],
            variable=G.cu_pick, value=i[1])  # we use same value as label

    # Caller grid me
    return menu_button




def MoreWidget(parent):
    """More photometry options frame"""

    # Change  menu label more option -> less option
    # Todo as toogle in TextFrame
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

    get_root().OptionFrame.toogle_more_analysis(parent)


def ManualBackground():
    """Create manual background frame"""
    if get_state().b_see_manual_background:
        ManualBackClose()
    else:
        ManualBackOpen()
    G.manual_back_bool = not G.manual_back_bool


def ManualBackOpen():
    get_state().noise_type = "manual"
    G.ManualBackFrame = tk.Frame(get_root().OptionFrame, bg=skin().color.bg)
    G.ManualBackFrame.grid(sticky='nsew')
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
    G.bu_back_close = tk.Button(
        G.ManualBackFrame, text=u'\u25b4 ' + 'Close',
        command=ManualBackClose, **skin().button_dic)
    G.bu_back_close.grid(row=1, column=0, columnspan=2)
    log(3, "Manual Back called")


def ManualBackClose():
    G.ManualBackFrame.destroy()
    G.background = float(G.tkvar.background.get())


def SetFitType(name):  # strange but works
    """Choose Fit Type
    Different fit types: A Moffat fit is setted by default. You can change it. Gaussian, Moffat,Bessel are three parametrics psf. Gaussian hole is a fit of two Gaussians with the same center by default but you can change that in more option in file button. The Gaussian hole is made for saturated stars. It can be very useful, especially because not may other software utilize this fit.
    Why is the fit type really important? The photometry and the peak of the objects utilize the fit. For the photometry, the fit measure the aperture and the maximum is directly taken from the fit. So changing the fit type can change by 5 to 10% your result
    What should I use? For strehl <10% Gaussian, for Strehl>50% Bessel, between these, Moffat.
    Programmers: Strehl@WindowRoot.py calls SeeingPSF@ImageFunction.py which calls fit_template_function.py
    Todo : fastly analyse the situation and choose a fit type consequently
    """
    LogFitType()

    get_state().fit_type = name
    G.cu_fit.set(name.replace("2D", ""))  # to change radio but, check
    try:
        if get_state().b_aniso and not '2D' in get_state().fit_type:
            get_state().fit_type += '2D'
        elif not get_state().b_aniso:
            get_state().fit_type = get_state().fit_type.replace('2D', '')
    except BaseException:
        if get_state().fit_type.find('2D') == -1:
            get_state().fit_type += '2D'
    if not get_state().fit_type.find('None') == -1:
        get_state().fit_type = 'None'

    # Saturated
    if "Gaussian_hole" in get_state().fit_type:
        try:
            # Global even more dirty
            if not get_state().same_center:
                get_state().fit_type = get_state().fit_type.replace('same_center', '')
            elif not 'same_center' in get_state().fit_type:
                get_state().fit_type += "same_center"
        except BaseException:
            if not 'same_center' in get_state().fit_type:
                get_state().fit_type += "same_center"
    log(0, 'Fit Type = ' + get_state().fit_type)

    # change the labels
    #G.fit_type_label["text"] = get_state().fit_type

    return

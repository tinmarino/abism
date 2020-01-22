"""
    Create Menu bar <- MenuBarMaker
"""
import re

import tkinter as tk
from abc import abstractmethod

from abism.front.util_front import system_open, about_window, \
    open_file, change_root_scheme, Scheme, skin

from abism.plugin.window_header import spawn_header_window

# For tool
from abism.plugin.DebugConsole import PythonConsole
from abism.plugin.xterm_console import jupyter_window
from abism.plugin.Histogram import Histopopo

# TODO remove
from abism.front import Pick  # to connect PickOne per defautl

from abism.util import get_root, get_state, quit_process, \
    get_colormap_list, get_stretch_list, get_cut_list


class MenuBar(tk.Frame):
    """Full Menu Bar, autopack, the only one exported"""
    def __init__(self, parent):
        """Create the menu bar (autopack top)"""
        super().__init__(parent, bg=skin().color.bg)

        # Pack at top
        self.pack(side=tk.TOP, expand=0, fill=tk.X)

        # For all menu button (tab)
        for col, callback in enumerate([
                AbismMenu,
                FileMenu,
                AnalysisMenu,
                ViewMenu,
                ToolMenu,
                ]):
            # Same weight
            self.columnconfigure(col, weight=1)
            # Create
            button = callback(self)
            # Grid it
            button.grid(row=0, column=col, sticky="nsew")


class ButtonMenu(tk.Menubutton):
    """Base class for a top menu button (with a dropdown)"""
    def __init__(self, parent):
        # Prepare argument dic
        l_args = {**skin().menu_dic, 'text': u"\u25be" + self.get_text()}

        # Init
        super().__init__(parent, **l_args)

        # Create my menu drowpdown
        self.menu = tk.Menu(self, **skin().fg_and_bg)

        # Otherwise, dropdown not working
        self['menu'] = self.menu

        # Grid me <- parent does it: I can't auto increment col
        # self.grid(row=0, sticky="nsew")

    @abstractmethod
    def get_text(self):
        return ''


class AbismMenu(ButtonMenu):
    """ABISM"""
    def __init__(self, parent):
        super().__init__(parent)
        self.menu.add_command(
            label='About',
            command=about_window)

        self.menu.add_command(
            label='Advanced Manual',
            command=lambda: system_open(path='doc/advanced_manual.pdf'))

        self.menu.add_cascade(
            label='Color Scheme',
            underline=0,
            menu=self.get_colorscheme_cascade())

        self.menu.add_command(
            label='Quit',
            command=quit_process)


    def get_text(self):
        return 'ABISM'


    def get_colorscheme_cascade(self):
        """Create the submenu"""
        menu = tk.Menu(self)

        menu.add_radiobutton(
            label='Dark Solarized',
            command=lambda: change_root_scheme(Scheme.DARK_SOLARIZED))

        menu.add_radiobutton(
            label='Light Solarized',
            command=lambda: change_root_scheme(Scheme.LIGHT_SOLARIZED))

        return menu


class FileMenu(ButtonMenu):
    """Open new file"""
    def __init__(self, parent):
        """Menu, open_image, header
            args is a dictionnary containing the arguments to make all menuENtry
            identical, logical, responsible, pratical
        """
        super().__init__(parent)

        # Open
        self.menu.add_command(
            label='Open',
            command=open_file)

        # Show header
        self.menu.add_command(
            label='Display Header',
            command=lambda: spawn_header_window(
                get_root().image.name,
                get_root().header.header.tostring(sep="\n"),
                save=get_root().saved_children,
            ))


    def get_text(self):
        return 'File'


class ViewMenu(ButtonMenu):
    """Color, cut, scale
    With a style of column or cascade
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.style = 'column'

        # Divide and conquer
        self.add_color_column()
        self.add_scale_column()
        self.add_cut_column()


    def get_text(self):
        return 'View'


    def add_color_column(self):
        """Color drop"""
        self.menu.add_command(label="COLOR", bg=None, state=tk.DISABLED)

        # Define callbacks
        def on_change_cmap(string_var):
            s_in = string_var.get()

            get_state().s_image_color_map = s_in

            get_root().ImageFrame.CutImageScale()

        def on_change_contour():
            get_state().b_image_contour = not get_state().b_image_contour
            get_root().ImageFrame.CutImageScale()

        def on_change_reverse():
            """Flip _r an end"""
            s_old = get_state().s_image_color_map
            get_state().b_image_reverse = not get_state().b_image_reverse
            if re.search(r'_r$', s_old):
                cmap = s_old[:-2]
            else:
                cmap = s_old + '_r'
            get_state().s_image_color_map = cmap
            get_root().ImageFrame.CutImageScale()

        # Create tk var
        cmap_var = tk.StringVar()
        cmap_var.set(get_state().s_image_color_map)

        # Add
        for label, value in get_colormap_list():
            self.menu.add_radiobutton(
                label=label,
                command=lambda: on_change_cmap(cmap_var),
                variable=cmap_var, value=value)

        # Contour
        self.menu.add_checkbutton(
            label='Contour',
            command=on_change_contour)

        # Reverse
        self.menu.add_checkbutton(
            label='Reverse',
            command=on_change_reverse)

        # Add column break
        self.menu.add_command(columnbreak=1)


    def add_scale_column(self):
        """Scale of image drop"""
        self.menu.add_command(label="FCT", bg=None, state=tk.DISABLED)

        # Create tk var
        string_var = tk.StringVar()
        string_var.set(get_state().s_image_stretch)

        # Define callback
        def on_change_stretch(string_var):
            """same color map callback"""
            stretch = string_var.get()
            get_state().s_image_stretch = stretch
            get_root().ImageFrame.CutImageScale()

        # Add check buttons
        for i in get_stretch_list():
            self.menu.add_radiobutton(
                label=i[0],
                command=lambda: on_change_stretch(string_var),
                variable=string_var, value=i[2])

        # Add break
        self.menu.add_command(columnbreak=1)


    def add_cut_column(self):
        """Cut min max of the iamge scale"""
        self.menu.add_command(label="CUTS", bg=None, state=tk.DISABLED)

        # Define callback
        def on_change_cut(s_in, value):
            """same color map callback"""
            get_state().s_image_cut = s_in
            get_state().i_image_cut = value
            get_root().ImageFrame.CutImageScale()

        # Add check buttons
        string_var = tk.StringVar()
        string_var.set(get_cut_list()[0][1])
        for text, s, _, i in get_cut_list():
            self.menu.add_radiobutton(
                label=text,
                command=lambda s=s, i=i: on_change_cut(s, i),
                variable=string_var, value=text)

        def on_manual():
            get_root().OptionFrame.toogle_manual_cut()

        # Add manual cut trigger
        self.menu.add_radiobutton(
            label="Manual",
            command=on_manual,
            variable=string_var, value="Manual")

        # Add break
        self.menu.add_command(columnbreak=1)


class AnalysisMenu(ButtonMenu):
    """Choose Star analysis method: fit and pick"""
    def __init__(self, parent):
        super().__init__(parent)

        self.see_more = False
        self.index_more = 0

        self.add_fit_menu()
        self.add_pick_menu()

    def add_fit_menu(self):
        self.menu.add_command(
            label="Fit Type", bg=None, state=tk.DISABLED)

        lst1 = [
            ["Gaussian", "Gaussian", lambda: SetFitType("Gaussian")],
            ["Moffat", "Moffat", lambda: SetFitType("Moffat")],
            ["Bessel1", "Bessel1", lambda: SetFitType("Bessel1")],
            ["None", "None", lambda: SetFitType("None")],
        ]

        # Add radio but
        string_var = tk.StringVar()
        string_var.set(get_state().fit_type.replace("2D", ""))
        for text, tag, callback in lst1:
            self.menu.add_radiobutton(
                label=text,
                command=callback,
                variable=string_var, value=tag)

        def on_more():
            self.toogle_more_options()
            get_root().OptionFrame.toogle_more_analysis(self)

        # Add button more options
        self.menu.add_command(
            label=u"\u25be More Options",
            command=on_more)
        self.index_more = self.menu.index(tk.END)

        self.menu.add_command(columnbreak=1)

    def add_pick_menu(self):
        self.menu.add_command(
            label="Pick Object(s)", bg=None, state=tk.DISABLED)

        lst2 = [
            ["PickOne", "one", lambda: Pick.RefreshPick("one")],
            ["Binary Fit", "binary", lambda: Pick.RefreshPick("binary")],
            # ["PickMany", "many", lambda: Pick.RefreshPick("many")],
            ["No Pick", "nopick", lambda: Pick.RefreshPick("nopick")],
        ]

        string_var = tk.StringVar()
        string_var.set(get_state().pick_type)
        for text, tag, callback in lst2:
            self.menu.add_radiobutton(
                label=text, command=callback,
                variable=string_var, value=tag)

    def get_text(self):
        return 'Analysis'

    def toogle_more_options(self):
        """More photometry options frame"""
        self.see_more = not self.see_more
        if self.see_more:
            self.menu.entryconfig(self.index_more, label=u'\u25b4 '+'Less Option')
        else:
            self.menu.entryconfig(self.index_more, label=u'\u25be '+'More Option')


class ToolMenu(ButtonMenu):
    """Generic awesome tool. Usually in plugin"""
    def __init__(self, parent):
        """Menu, open_image, header
        args is a dictionnary containing the arguments to make all menuENtry
        identical, logical, responsible, pratical
        """
        super().__init__(parent)

        lst = [
            ["Profile", lambda: Pick.RefreshPick("profile")],
            ["Stat", lambda: Pick.RefreshPick("stat")],
            ["Histogram", lambda: Histopopo(
                get_root().FitFrame.get_figure(),
                get_root().image.sort,
                skin=skin())],
            ["Legacy Console", PythonConsole],
            ["Jupyter Console", jupyter_window],
        ]
        for i in lst:
            self.menu.add_command(label=i[0], command=i[1])


    def get_text(self):
        return 'Tools'









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

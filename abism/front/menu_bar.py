"""
    Create Menu bar <- MenuBarMaker
"""

import tkinter as tk
from abc import abstractmethod

from abism.front.Menu import AnalysisMenu

from abism.front.util_front import \
    system_open, about_window, open_file, \
    change_root_scheme, Scheme, skin
import abism.front.util_front as G

from abism.plugin.window_header import spawn_header_window

from abism.util import get_root, quit_process

# For tool
from abism.plugin.DebugConsole import PythonConsole
from abism.plugin.xterm_console import jupyter_window
from abism.plugin.Histogram import Histopopo
from abism.front import Pick  # to connect PickOne per defautl


def MenuBarMaker(parent):
    """Create the menu bar (autopack top)"""

    # Pack bar at top
    menu_bar = tk.Frame(parent, bg=skin().color.bg)
    menu_bar.pack(side=tk.TOP, expand=0, fill=tk.X)

    # For all menu button (tab)
    for col, callback in enumerate([
            AbismMenu,
            FileMenu,
            AnalysisMenu.AnalysisMenu,
            ViewMenu,
            ToolMenu,
                ]):
        # Same weight
        menu_bar.columnconfigure(col, weight=1)
        # Create
        button = callback(menu_bar)
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
        if self.style == "cascade":
            color_menu = tk.Menu(self, **skin().fg_and_bg)
        else:
            color_menu = self.menu
        color_menu.add_command(label="COLOR", bg=None, state=tk.DISABLED)
        # if we don't want cascade, we just add in the menu

        G.cu_color = tk.StringVar()
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
                label=i[0], command=lambda i=i: get_root().ImageFrame.CutImageScale(
                    dic={"cmap": i[1]}, run="G.cu_cut.set('"+i[1] + "')"),
                variable=G.cu_color, value=i[1])  # we use same value as label

        ########
        # Contour
        color_menu.add_command(
            label='Contour', command=lambda: get_root().ImageFrame.CutImageScale(
                dic={"contour": 'not a bool'}))

        #################
        # more colors TODO remove that shit
        more_color_menu = tk.Menu(color_menu, **skin().fg_and_bg)
        num = 0
        import matplotlib
        all_cmaps = sorted([i for i in dir(matplotlib.cm) if hasattr(
            getattr(matplotlib.cm, i), 'N')])  # inclouding inverse
        for i in all_cmaps:
            num += 1
            more_color_menu.add_radiobutton(
                label=i,
                command=lambda i=i: get_root().ImageFrame.CutImageScale(dic={"cmap": i}),
                variable=G.cu_color, value=i)  # we use same value as label

            if num % 30 == 0:
                more_color_menu.add_radiobutton(
                    label=i,
                    command=lambda i=i: get_root().ImageFrame.CutImageScale(dic={"cmap": i}),
                    variable=G.cu_color, value=i, columnbreak=1)  # we use same value as label
        color_menu.add_cascade(menu=more_color_menu,
                            label="More colors", underline=0)

        if self.style == "cascade":
            self.menu.add_cascade(
                menu=color_menu, underline=0, label="Color")
        else:
            self.menu.add_command(columnbreak=1)


    def add_scale_column(self):
        """Scale of image drop"""
        if self == "cascade":
            scale_menu = tk.Menu(self, **skin().fg_and_bg)
        else:
            scale_menu = self.menu
        scale_menu.add_command(label="FCT", bg=None, state=tk.DISABLED)

        G.cu_scale = tk.StringVar()
        G.cu_scale.set(G.scale_dic[0]["stretch"])
        lst = [["Lin", "x", "linear"], ["Sqrt", "x**0.5", "sqrt"], ["Square", "x**2",
                                                                    "square"], ["Log", "np.log(x+1)/0.69", "log"], ["Arcsinh", "", "arcsinh"]]
        for i in lst:
            scale_menu.add_radiobutton(label=i[0],
                                    command=lambda i=i: get_root().ImageFrame.CutImageScale(
                                        dic={"fct": i[1], "stretch": i[2]}, run="G.cu_scale.set('" + i[2] + "')"),
                                    variable=G.cu_scale, value=i[2])  # we use same value as label

        if self.style == "cascade":
            self.menu.add_cascade(
                menu=scale_menu, underline=0, label="Fct")
        else:
            self.menu.add_command(columnbreak=1)


    def add_cut_column(self):
        """Cut min max of the iamge scale"""
        if self.style == "cascade":
            cut_menu = tk.Menu(self, **skin().fg_and_bg)
        else:
            cut_menu = self.menu
        cut_menu.add_command(label="CUTS", bg=None, state=tk.DISABLED)

        G.cu_cut = tk.StringVar()
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
            cut_menu.add_radiobutton(
                label=i[0],
                command=lambda i=i: get_root().ImageFrame.CutImageScale(
                dic={"scale_cut_type": i[1], i[2]: i[3]}, run="G.cu_cut.set('"+i[0] + "')"),
                variable=G.cu_cut, value=i[0])  # we use same value as label

        cut_menu.add_radiobutton(label="Manual",
                                command=ManualCut,
                                variable=G.cu_cut, value="Manual")  # we use same value as label

        if self.style == "cascade":
            self.menu.add_cascade(
                menu=cut_menu, underline=0, label="Cut")
        else:
            self.menu.add_command(columnbreak=1)


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





import tkinter as tk

from abism.front.util_front import skin, TitleLabel
import abism.front.util_front as G

from abism.util import log, get_root

def ManualCut():
    """Stupid switch"""
    if G.manual_cut_bool:
        ManualCutClose()
    else:
        ManualCutOpen()


def ManualCutOpen():
    # Prepare
    G.manual_cut_bool = not G.manual_cut_bool

    # Pack main
    G.ManualCutFrame = tk.Frame(get_root().OptionFrame, bg=skin().color.bg)
    G.all_frame.append("G.ManualCutFrame")
    G.ManualCutFrame.grid(sticky='nsew')

    # Pack lave
    lt = TitleLabel(G.ManualCutFrame, text="Cut image scale")
    lt.pack(side=tk.TOP, anchor="w")

    G.ManualCutGridFrame = tk.Frame(G.ManualCutFrame, bg=skin().color.bg)
    G.all_frame.append("G.ManualCutGridFrame")
    G.ManualCutGridFrame.pack(side=tk.TOP, expand=0, fill=tk.X)

    G.ManualCutGridFrame.columnconfigure(0, weight=1)
    G.ManualCutGridFrame.columnconfigure(1, weight=1)

    def GetValue(event):
        dic = {"min_cut": float(G.entries[1].get()),
               "max_cut": float(G.entries[0].get())}
        log(2, "ManualCut, dic called , ", dic)
        get_root().ImageFrame.CutImageScale(dic=dic)

    lst = [["Max cut", "max_cut"], ["Min cut", "min_cut"]]
    G.entries = []
    r = 0
    for i in lst:
        l = tk.Label(
            G.ManualCutGridFrame,
            text=i[0], font=skin().font.answer, **skin().fg_and_bg)
        l.grid(row=r, column=0, sticky="snew")  # , sticky=W)

        v = tk.StringVar()
        e = tk.Entry(G.ManualCutGridFrame, width=10,
                     textvariable=v, font=skin().font.answer,
                     bd=0, **skin().fg_and_bg)
        e.grid(row=r, column=1, sticky="nsew")  # , sticky=W)
        e.bind('<Return>', GetValue)
        v.set("%.1f" % G.scale_dic[0][i[1]])
        G.entries.append(v)
        r += 1

    ###############
    # CLOSE button
    bu_close = tk.Button(
        G.ManualCutGridFrame, text=u'\u25b4 ' + 'Close',
        command=ManualCutClose, **skin().button_dic)
    bu_close.grid(row=r, column=0, columnspan=2)
    log(3, "Manual Cut called")

    # Redraw
    get_root().OptionFrame.init_will_toogle(visible=True, add_title=False)


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
    log(3, 'Cut min, max:', G.scale_dic[0]['min_cut'], G.scale_dic[0]['max_cut'])
    get_root().ImageFrame.CutImageScale()

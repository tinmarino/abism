"""
    Create Menu bar <- MenuBarMaker
"""

import tkinter as tk
from abc import abstractmethod

from abism.front.Menu import AnalysisMenu

from abism.front.util_front import \
    system_open, about_window, open_file, \
    change_root_scheme, Scheme, skin

from abism.plugin.window_header import spawn_header_window

# For tool
from abism.plugin.DebugConsole import PythonConsole
from abism.plugin.xterm_console import jupyter_window
from abism.plugin.Histogram import Histopopo
from abism.front import Pick  # to connect PickOne per defautl

from abism.util import get_root, get_state, quit_process, \
    get_colormap_list, get_stretch_list, get_cut_list


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
        self.menu.add_command(label="COLOR", bg=None, state=tk.DISABLED)

        # Create tk var
        string_var = tk.StringVar()
        string_var.set(get_state().s_image_color_map)

        # Define callback
        def on_change_cmap(string_var):
            cmap = string_var.get()

            # Save
            get_state().s_image_color_map = cmap

            # Redraw
            get_root().ImageFrame.CutImageScale()

        # Add my favorite colors
        for i in get_colormap_list():
            self.menu.add_radiobutton(
                label=i[0],
                command=lambda: on_change_cmap(string_var),
                variable=string_var, value=i[1])

        # Add contour
        dic = {"contour": 'not a bool'}
        self.menu.add_command(
            label='Contour',
            command=lambda: get_root().ImageFrame.CutImageScale(dic=dic))

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

        string_var = tk.StringVar()
        string_var.set(get_state().s_image_cut)

        # Define callback
        def on_change_cut(string_var, value):
            """same color map callback"""
            cut = string_var.get()
            get_state().s_image_cut = cut
            get_state().i_image_cut = value
            get_root().ImageFrame.CutImageScale()

        # Add check buttons
        for i in get_cut_list():
            self.menu.add_radiobutton(
                label=i[0],
                command=lambda i=i: on_change_cut(string_var, i[3]),
                variable=string_var, value=i[0])

        def on_manual():
            get_root().OptionFrame.toogle_manual_cut()

        # Add manual cut trigger
        self.menu.add_radiobutton(
            label="Manual",
            command=on_manual,
            variable=string_var, value="Manual")

        # Add break
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

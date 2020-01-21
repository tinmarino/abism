"""
    Create Menu bar
Abism
File
Analisys
View
Tool

"""
import tkinter as tk
from abc import abstractmethod

from abism.front.Menu import AnalysisMenu
from abism.front.Menu import ViewMenu


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


def MenuBarMaker(root):
    """Create the menu bar (autopack top)"""

    # Pack bar at top
    menu_bar = tk.Frame(root, bg=skin().color.bg)
    menu_bar.pack(side=tk.TOP, expand=0, fill=tk.X)

    args = {"relief": tk.FLAT, "width": G.menu_button_width}
    # For all menu button (tab)
    for col, i in enumerate([
            [AbismMenu, args],
            [FileMenu, args],
            [AnalysisMenu.AnalysisMenu, {**args, "text": u'\u25be '+'Analysis'}],
            [ViewMenu.ViewMenu, {**args, "text": u'\u25be '+'View'}],
            [ToolMenu, {}],
                ]):
        # Same weight
        menu_bar.columnconfigure(col, weight=1)
        # Create
        button = i[0](menu_bar, **i[1])
        # Grid it
        button.grid(row=0, column=col, sticky="nsew")

class ButtonMenu(tk.Menubutton):
    """Base class for a top menu button (with a dropdown)"""
    def __init__(self, parent, **args):
        # Prepare argument dic
        l_args = skin().fg_and_bg.copy()
        l_args.update({'text': u"\u25be" + self.get_text()})
        l_args.update(args)

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
    def __init__(self, parent, **args):
        super().__init__(parent, **args)
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
    def __init__(self, parent, **args):
        """Menu, open_image, header
            args is a dictionnary containing the arguments to make all menuENtry
            identical, logical, responsible, pratical
        """
        super().__init__(parent, **args)

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


class ToolMenu(ButtonMenu):
    """Generic awesome tool. Usually in plugin"""
    def __init__(self, parent, **args):
        """Menu, open_image, header
            args is a dictionnary containing the arguments to make all menuENtry
            identical, logical, responsible, pratical
        """
        super().__init__(parent, **args)

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

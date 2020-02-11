"""
    Create Menu bar <- MenuBarMaker
"""
import re

import tkinter as tk
from abc import abstractmethod

# For tool
from abism.plugin.window_debug import create_debug_console
from abism.plugin.window_xterm import create_jupyter_console
from abism.plugin.histogram import histopopo

from abism.front.util_front import system_open, about_window, \
    open_file, toogle_header, toogle_manual
import abism.front.tk_extension as tk_ext

from abism.util import (
    log, get_root, get_state, quit_process, get_colormap_list,
    get_stretch_list, get_fit_list, EPick, save_state
)



class MenuBar(tk.Frame):
    """Full Menu Bar, autopack, the only one exported"""
    def __init__(self, parent):
        """Create the menu bar (autopack top)"""
        super().__init__(parent)

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
        l_args = {'text': u"\u25be" + self.get_text()}

        # Init
        super().__init__(parent, **l_args)

        # Create my menu drowpdown
        self.menu = tk.Menu(self, tearoff=False)

        # Otherwise, dropdown not working
        self['menu'] = self.menu

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
            label='Interface Manual',
            command=toogle_manual)
        get_root().bind_root("<Control-question>", lambda _: toogle_manual())
        self.menu.add_entry_info(
            "<C-?>: Open interface manual with system (.md)")

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
            command=lambda: tk_ext.change_root_scheme(tk_ext.Scheme.DARK_SOLARIZED))

        menu.add_radiobutton(
            label='Light Solarized',
            command=lambda: tk_ext.change_root_scheme(tk_ext.Scheme.LIGHT_SOLARIZED))

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
        get_root().bind_all("<Control-o>", lambda _: open_file())
        self.menu.add_entry_info(
            "<C-O>: Open file dialog\nChoose fits image path")

        # Save
        self.menu.add_command(
            label='Save',
            command=save_state)
        get_root().bind_all("<Control-s>", lambda _: save_state())
        self.menu.add_entry_info(
            "<C-S>: Save Abism previous results\n"
            "To abism-<date>.log in current directory")

        # Show header
        self.menu.add_command(
            label='Display Header',
            command=toogle_header)
        get_root().bind_root("<Control-h>", lambda _: toogle_header())
        self.menu.add_entry_info(
            "<C-H>: Open Header viewer window")


    def get_text(self):
        return 'File'


class AnalysisMenu(ButtonMenu):
    """Fit, Pick <- Choose Star analysis method"""
    def __init__(self, parent):
        super().__init__(parent)

        self.index_more = 0

        self.add_fit_menu()
        self.add_pick_menu()


    def add_fit_menu(self):
        self.menu.add_command(
            label="Fit Type", bg=None, state=tk.DISABLED)

        def on_change_fit(string_var):
            s_in = string_var.get()
            log(5, 'Change Fit to', s_in)
            get_state().s_fit_type = s_in

        # Add radio but
        string_var = tk.StringVar()
        string_var.set(get_state().s_fit_type)
        for text in get_fit_list():
            self.menu.add_radiobutton(
                label=text,
                command=lambda: on_change_fit(string_var),
                variable=string_var, value=text)

        def on_more():
            get_root().frame_option.toogle_more_analysis(parent=self)

        # Add button more options
        self.menu.add_command(
            label=u"\u25be More Options",
            command=on_more)
        self.menu.add_entry_info("<C-M>: Display additional frame for more options")
        get_root().bind_all("<Control-m>", lambda _: on_more())

        # Keep index to change label
        self.index_more = self.menu.index(tk.END)

    def add_pick_menu(self):
        self.menu.add_command(
            label="Pick Object(s)", bg=None, state=tk.DISABLED, columnbreak=1)

        lst2 = [
            ["PickOne", EPick.ONE,
             "<C-P>O: Draw a rectangle around one star\n"
             "The fit is performed in this rectangle",
             "<Control-p>o"],
            ["Binary Fit", EPick.BINARY,
             "<C-P>B: Make one click per star\n"
             "Its are the initial guess of a fit",
             "<Control-p>b"],
            ["Tight Binary", EPick.TIGHT,
             "<C-P>T: Stricter bounds",
             "<Control-p>t"],
            ["No Pick", EPick.NO,
             "<C-P>N: Disable abism click (to use matplotlib, explore the image)",
             "<Control-p>n"],
        ]

        for text, enum, info, keys in lst2:
            cmd = lambda enum=enum: refresh_pick(enum)
            self.menu.add_radiobutton(
                label=text, command=cmd,
                variable=get_state().tk_pick, value=enum)
            self.menu.add_entry_info(info)
            get_root().bind_all(keys, lambda _, cmd=cmd: cmd())
            self.menu.add_entry_info(info)


    def get_text(self):
        return 'Analysis'

    def toogle_more_options(self):
        """More photometry options frame"""
        if get_root().frame_option.is_more_analysis_visible():
            self.menu.entryconfig(self.index_more, label=u'\u25b4 '+'Less Option')
        else:
            self.menu.entryconfig(self.index_more, label=u'\u25be '+'More Option')


class ViewMenu(ButtonMenu):
    """Color, Cut, Scale <- Appearance of image"""
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

            get_root().frame_image.refresh_image()

        def on_change_contour():
            get_state().b_image_contour = not get_state().b_image_contour
            get_root().frame_image.refresh_image()

        def on_change_reverse():
            """Flip _r an end"""
            s_old = get_state().s_image_color_map
            get_state().b_image_reverse = not get_state().b_image_reverse
            if re.search(r'_r$', s_old):
                cmap = s_old[:-2]
            else:
                cmap = s_old + '_r'
            get_state().s_image_color_map = cmap
            get_root().frame_image.refresh_image()

        def on_change_bpm():
            get_state().b_image_bpm = not get_state().b_image_bpm
            get_root().frame_image.refresh_image()

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

        # BadPixel Map
        self.menu.add_checkbutton(
            label='Bad Pixels',
            command=on_change_bpm)

    def add_scale_column(self):
        """Scale of image drop"""
        self.menu.add_command(label="FCT", bg=None, state=tk.DISABLED,
                              columnbreak=1)

        # Create tk var
        string_var = tk.StringVar()
        string_var.set(get_state().s_image_stretch)

        # Define callback
        def on_change_stretch(string_var):
            """same color map callback"""
            stretch = string_var.get()
            get_state().s_image_stretch = stretch
            get_root().frame_image.refresh_image()

        # Add check buttons
        for i in get_stretch_list():
            self.menu.add_radiobutton(
                label=i[0],
                command=lambda: on_change_stretch(string_var),
                variable=string_var, value=i[2])


    def add_cut_column(self):
        """Cut min max of the iamge scale"""
        self.menu.add_command(label="CUTS", bg=None, state=tk.DISABLED,
                              columnbreak=1)

        lst = ['3σ', '99.95%', '99.9%', '99%', '90%', 'None']

        # Define callback
        def on_change_cut(string_var):
            """same color map callback"""
            s_in = string_var.get()
            get_state().s_image_cut = s_in
            i_min, i_max = get_state().image.get_cut_minmax()
            get_state().i_image_min_cut = i_min
            get_state().i_image_max_cut = i_max
            get_root().frame_image.refresh_image()

        # Add check buttons
        string_var = tk.StringVar()
        string_var.set(get_state().s_image_cut)
        for text in lst:
            self.menu.add_radiobutton(
                label=text,
                command=lambda: on_change_cut(string_var),
                variable=string_var, value=text)

        def on_manual():
            get_state().s_image_cut = 'Manual'
            get_root().frame_option.toogle_manual_cut()

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

        # Profile
        cmd = lambda: refresh_pick(EPick.PROFILE)
        self.menu.add_radiobutton(
            label='Profile', command=cmd,
            variable=get_state().tk_pick, value=EPick.PROFILE)
        get_root().bind_all("<Control-p>p", lambda _, cmd=cmd: cmd())
        self.menu.add_entry_info(
            "<C-P>P: Draw a line\nDisplay image intensity along this line")

        # Stat
        cmd = lambda: refresh_pick(EPick.STAT)
        self.menu.add_radiobutton(
            label='Stat', command=cmd,
            variable=get_state().tk_pick, value=EPick.STAT)
        get_root().bind_all("<Control-p>s", lambda _, cmd=cmd: cmd())
        self.menu.add_entry_info(
            "<C-P>S: Draw a rectangle\nDisplay image statitics in this rectangle")

        # Ellipse
        cmd = lambda: refresh_pick(EPick.ELLIPSE)
        self.menu.add_radiobutton(
            label='Ellipse', command=cmd,
            variable=get_state().tk_pick, value=EPick.ELLIPSE)
        get_root().bind_all("<Control-p>e", lambda _, cmd=cmd: cmd())
        self.menu.add_entry_info(
            "<C-P>E: Draw an ellipse where photometry is performed")

        # Histogram
        self.menu.add_radiobutton(label='Histogram', command=open_histogram)
        get_root().bind_all("<Control-t>h", lambda _: open_histogram())
        self.menu.add_entry_info(
            "<C-T>H: Display image intensity histogram")

        # Legacy console (tk)
        cmd = create_debug_console
        self.menu.add_radiobutton(label='Legacy Console', command=cmd)
        get_root().bind_all("<Control-t>d", lambda _, cmd=cmd: cmd())
        self.menu.add_entry_info(
            "<C-T>D: Open debug console window")

        # Jupyter
        cmd = create_jupyter_console
        self.menu.add_radiobutton(label='Jupyter Console', command=cmd)
        get_root().bind_all("<Control-t>j", lambda _, cmd=cmd: cmd())
        self.menu.add_entry_info(
            "<C-T>J: Open jupyter console window\n"
            "Requires: xterm, jupyter")


    def get_text(self):
        return 'Tools'


def open_histogram():
    print("Calling histogram")
    histopopo(
        get_root().frame_fit.get_figure(),
        get_state().image.sort)


def refresh_pick(enum):
    """Disconnect old pick event and connect new one"""
    import abism.front.pick as pick

    pick_dic = {
        EPick.NO: pick.PickNo,
        EPick.ONE: pick.PickOne,
        EPick.BINARY: pick.PickBinary,
        EPick.TIGHT: pick.PickTightBinary,
        EPick.STAT: pick.PickStat,
        EPick.PROFILE: pick.PickProfile,
        EPick.ELLIPSE: pick.PickEllipse,
    }

    cls = pick_dic[enum]
    log(3, 'Changing pick type to ', cls.__name__)
    get_state().tk_pick.set(enum)
    get_state().e_pick_type = enum

    # Dicconnect old
    if get_state().pick:
        get_state().pick.disconnect()

    # Connect new
    get_state().pick = cls()
    get_state().pick.connect()

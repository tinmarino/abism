"""
    Abism main GUI
"""

# Standard
from os.path import isfile

# Tkinter
import tkinter as tk

# Gui
from abism.front.menu_bar import MenuBar
from abism.front.frame_text import LeftFrame
from abism.front.frame_plot import RightFrame
from abism.front.util_front import skin, icon_path, open_file

# Variables
from abism.back.image import ImageInfo


from abism.util import log, set_root, restart, parse_argument
import abism.util as util



class WindowRoot(tk.Tk):
    """Main window app object
    May one day destroy util_front ...
    Call me like Tk:
        root_window = WindowRoot()
        root_window.mainloop()
    """
    def __init__(self):
        """Create main app"""
        super().__init__()
        self.geometry(parse_argument().gui_geometry)

        # Variables for my children
        set_root(self)

        # Save spawned children
        self.saved_children = []

        # Set icon && shortcut
        self.set_icon()
        self.set_shortcut()

        # 1 Menu: Pack
        MenuBar(self)

        # ALL What is not the menu is a paned windows :
        # I can rezie it with the mouse from left to right,
        # This (all but not the Menu) Frame is called MainPaned
        self.paned_root = tk.PanedWindow(
            self, orient=tk.HORIZONTAL, **skin().paned_dic)
        self.paned_root.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 2 Left: Add
        left = LeftFrame(self, self.paned_root)
        left_width = parse_argument().gui_sash_root
        self.paned_root.add(left, width=left_width)

        # 3 Right: Add
        root_width = int(parse_argument().gui_geometry.split('x')[0])
        right_width = root_width - left_width
        height = parse_argument().gui_sash_image
        right = RightFrame(self, self.paned_root, right_width, height)
        self.paned_root.add(right)

        # Init image
        self.set_image(util._parsed_args.image)


    def set_image(self, filepath):
        if not filepath: return

        # Craft ImageInfo
        self.image = ImageInfo.from_file(filepath)
        if not self.image:
            log(0, 'Error: Cannot read fits image from file', filepath)
            return

        # Set title
        self.set_title()

        # Alias Helper
        self.header = self.image.header

        # Draw Cube button
        self.frame_button.toogle_cube()

        # Redraw
        self.frame_image.draw_image()

        # Reset ImageParameters if open
        if self.frame_option.see_image_parameter:
            self.frame_option.close_image_parameter()
            self.frame_option.open_image_parameter()


    def set_title(self):
        """Create OS's window title, icon and Set geomrtry"""
        self.title('ABISM (' +
                   "/".join(str(self.image.name).split("/")[-3:]) + ')')


    def set_icon(self):
        """Create OS Icon from resources"""
        if isfile(icon_path()):
            bitmap = tk.PhotoImage(file=icon_path())
            self.tk.call('wm', 'iconphoto', self._w, bitmap)
        else:
            log(3, "->you have no beautiful icon "
                "because you didn't set the PATH in Abism.py")


    def set_shortcut(self):
        """Shortcuts with ctrl"""

        self.bind_all(
            "<Control-o>",
            lambda _: open_file())

        self.bind_all(
            "<Control-r>",
            lambda _: restart())
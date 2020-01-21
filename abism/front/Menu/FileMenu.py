"""
    Scrolldown on file tab
"""
from tkinter import Menu, Menubutton

from abism.front.util_front import skin, open_file

from abism.plugin.FitsHeaderWindow import DisplayHeader


def FileMenu(root, parent, args):
    """Menu, open_image, header
        args is a dictionnary containing the arguments to make all menuENtry
        identical, logical, responsible, pratical
    """
    menu_button = Menubutton(parent, **args)
    menu_button.menu = Menu(menu_button, **skin().fg_and_bg)

    # Open
    menu_button.menu.add_command(
        label='Open',
        command=open_file)

    # Show header
    menu_button.menu.add_command(
        label='Display Header',
        command=lambda: DisplayHeader(
            root.image.name,
            root.header.header.tostring(sep="\n"),
            save=root.saved_children,
        ))

    menu_button['menu'] = menu_button.menu

    # Caller grid me
    return menu_button

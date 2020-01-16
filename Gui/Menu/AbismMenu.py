"""
    Menu click on Abism tab
"""
from tkinter import Menu, Menubutton, Tk, Label

import GuyVariables as G
import WorkVariables as W

"""
    TODO : make 4, 5 good appearance profiles.
"""


def AbismMenu(args):
    """Create the menu on Abism tab click"""
    G.abism_menu = Menubutton(G.MenuBar, **args)
    G.abism_menu.menu = Menu(G.abism_menu, **G.submenu_args)

    lst = [
        ["About", About],
        ["Advanced Manual", lambda: See(pdf="advanced_manual.pdf")],
        ["Quit", G.Quit],
    ]
    for i in lst:
        if "Appearance" in i[0]:
            i[1]()
        else:
            G.abism_menu.menu.add_command(label=i[0], command=i[1])

    G.abism_menu['menu'] = G.abism_menu.menu
    return G.abism_menu


def About():
    """Pop about window"""
    tk = Tk()
    tk.title("About Abism")
    txt = ("Adaptive Background Interactive Strehl Meter\n"
           "ABISM version " + G.version + " (2013 -- 2020) \n"
           "Authors: Girard Julien, Tourneboeuf Martin\n"
           "Emails: juliengirard@gmail.com tinmarino@gmail.com\n")
    l1 = Label(tk, text=txt)
    l1.pack()
    tk.mainloop()


def See(pdf=""):
    """Call system see"""
    import subprocess
    my_pdf = W.path + "/Doc/" + pdf

    fct = None
    try:  # PARANAL acroread
        subprocess.check_call("acroread", shell=False)
        fct = "acroread"
    except BaseException:
        try:  # Linux see
            subprocess.check_call("see", shell=False)
            fct = "see"
        except BaseException:
            try:  # mac open
                from subprocess import check_call
                check_call("open   " + my_pdf, shell=False)
                fct = "open"
            except BaseException:
                pass

    if fct is not None:
        subprocess.call(fct + " " + my_pdf + " &", shell=True)  # PARANAL
    elif W.verbose > 0:
        print("ERROR pdf viewer : need to be implemented ")

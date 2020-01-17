"""
    Utilities for Abism GUI
"""

# Standard
from sys import exit as sys_exit
from os import system
from functools import lru_cache

from tkinter import PhotoImage

from util import root_path
import back.util_back as W

"""
    Read globalDefiner
"""

@lru_cache(1)
def photo_up():
    """Return path of arrow_up icon"""
    return PhotoImage(file=root_path() + "/res/arrow_up.gif")


@lru_cache(1)
def photo_down():
    """Return path of arrow_down icon"""
    return PhotoImage(file=root_path() + "/res/arrow_down.gif")


# Gui parent
parent = None


def Quit():
    """Kill process"""
    W.log(1, 'Closing Abism, Goodbye. Come back soon.' + "\n" + 100 * '_' + 3 * "\n")
    parent.destroy()
    sys_exit(1)


def Restart():
    """ TODO move me to Global Definer, WritePref and ReadPref
        Pushing this button will close ABISM and restart it the same way it was launch before.
        Programmers: this is made to reload the Software if a modification in the code were made.
    """

    #################
    # prepare arguments
    arg = W.sys_argv

    # IMAGE_NAME
    matching = [s for s in arg if ".fits" in s]
    if len(matching) > 0:
        arg[arg.index(matching[0])] = W.image_name
    else:
        arg.insert(1, W.image_name)

    # COLOR MAP
    try:
        cmap = ImageFrame.cbar.cbar.get_cmap().name
    except BaseException:
        cmap = "jet"  # if no image loaded
    if not isinstance(cmap, str):
        cmap = "jet"
    for i in [
            ["--verbose", W.verbose],
        ["--bg", bg[0]],
        ["--fg", fg[0]],

        # SCALE DIC
        ["--cmap", cmap],
        ["--scale_dic_stretch", scale_dic[0]["stretch"]],
        ["--scale_dic_scale_cut_type", scale_dic[0]["scale_cut_type"]],
        ["--scale_dic_percent", scale_dic[0]["percent"]],


        # FRAME
        ["--parent", parent.geometry()],
        ["--TextPaned", TextPaned.winfo_width()],
        ["--DrawPaned", DrawPaned.winfo_width()],
        ["--LabelFrame", LabelFrame.winfo_width()],
        ["--ResultFrame", ResultFrame.winfo_height()],
        ["--OptionFrame", OptionFrame.winfo_height()],
        ["--ImageFrame", ImageFrame.winfo_height()],
        ["--RightBottomPaned", RightBottomPaned.winfo_height()],
        ["--FitFrame", FitFrame.winfo_width()],
        ["--AnswerFrame", AnswerFrame.winfo_width()],
        ["--ImageName", W.image_name],
    ]:
        if not i[0] in arg:
            arg.append(i[0])
            arg.append('"' + str(i[1]) + '"')
        else:
            arg[arg.index(i[0]) + 1] = '"' + str(i[1]) + '"'

    ###########
    # PREPARE STG command line args
    stg = "python "
    for i in arg:
        stg += " " + i
    stg += " &"  # To keep the control of the terminal
    W.log(0, "\n\n\n" + 80 * "_" + "\n",
          "Restarting ABISM with command:\n" + stg + "\nplease wait")

    ##########
    # DESTROY AND LAUNCH
    parent.destroy()  # I destroy Window,
    system(stg)         # I call an other instance
    sys_exit(1)         # I exit the current process.
    # As the loop is now opened, this may not be necessary but anyway it is safer



# TODO remove this
class VoidClass:
    """Helper container"""

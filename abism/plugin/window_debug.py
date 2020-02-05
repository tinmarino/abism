"""
    Helper console to run python code in the loop
    For devloppers now (maybe one day embed jupyter kernel in main window)
"""
import tkinter as tk

import abism.front.tk_extension as tk_ext

# pylint: disable = unused-wildcard-import, wildcard-import, unused-import
from abism.util import *
import abism.util as util

def create_debug_console():
    # pylint: disable = too-many-locals
    # Create root
    root = tk.Tk()
    root.title('Python console in tk')

    # Pack text
    # frame = tk.Frame(root)
    # frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    text_user = tk.Text(root)
    text_user.insert(tk.INSERT, "print(sm)")
    text_user.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    text_user.focus_force()


    # Append run
    def on_run():
        # pylint: disable=exec-used
        # Read
        cmd = text_user.get("1.0", tk.END)
        # Eval
        if cmd == "help":
            cmd = "quit() # to disable interative shell "
            cmd += "\nimport sys ; sys.exit() # to kill Abism "
            log(0, cmd)
        else:
            # Some helpers
            sm = get_state()  # pylint: disable = possibly-unused-variable
            exec(cmd, globals(), locals())

    # Pack button frame && Init configure
    bu_frame = tk.Frame(root)
    bu_frame.pack(side=tk.BOTTOM, expand=False, fill=tk.X)
    but_list = []

    # Append Run
    button = tk.Button(
        bu_frame, text="Run", command=on_run, bg=tk_ext.scheme.solarized_blue)
    but_list.append(button)

    # Append clear
    def on_clear():
        text_user.delete('1.0', tk.END)

    button = tk.Button(bu_frame, text="Clear", command=on_clear)
    but_list.append(button)

    # Append quit
    button = tk.Button(
        bu_frame, text='QUIT', command=root.destroy, bg=tk_ext.scheme.solarized_red)
    but_list.append(button)

    # Pack all
    for bu in but_list:
        bu.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    # Go
    root.mainloop()

    return root

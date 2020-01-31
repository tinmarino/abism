"""
    Helper console to run python code in the loop
    For devloppers now (maybe one day embed jupyter kernel in main window)
"""
import tkinter as tk

from abism.front.util_front import skin

# pylint: disable = unused-wildcard-import, wildcard-import, unused-import
import abism.util as util
from abism.util import *

def debug_console():
    # Create root
    root = tk.Tk()
    root.title('Python console in tk')

    # Pack text
    frame = tk.Frame(root)
    frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    text_user = tk.Text(frame, bg=skin().color.bg, fg=skin().color.fg)
    text_user.insert(tk.INSERT, "print(get_state())")
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
            exec(cmd, globals())

    # Pack button frame && Init configure
    bu_frame = tk.Frame(root)
    bu_frame.pack(side=tk.BOTTOM, expand=0, fill=tk.X)
    but_list = []

    # Prepare button list
    opts = {}
    opts.update({'background': 'DeepSkyBlue'})

    # Append Run
    button = tk.Button(
        bu_frame, text="Run", **opts,
        command=on_run)
    but_list.append(button)

    # Append clear
    def on_clear():
        text_user.delete('1.0', tk.END)

    button = tk.Button(
        bu_frame, text="Clear", **skin().fg_and_bg,
        command=on_clear)
    but_list.append(button)

    # Append quit
    opts.update({'background': 'red'})
    button = tk.Button(
        bu_frame, text='QUIT',
        command=root.destroy, **opts)
    but_list.append(button)

    # Pack all
    for bu in but_list:
        bu.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)

    # Go
    root.mainloop()

    return root

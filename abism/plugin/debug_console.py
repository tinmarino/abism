"""
    Helper console to run python code in the loop
    For devloppers now (maybe one day embed jupyter kernel in main window)
"""
import tkinter as tk

from abism.util import log
from abism.front.util_front import skin


def debug_console():
    # Create root
    root = tk.Tk()
    root.title('Python console in tk')

    # Pack text
    frame = tk.Frame(root)
    frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    text_user = tk.Text(frame, bg=skin().color.bg, fg=skin().color.fg)
    text_user.insert(tk.INSERT, "")
    text_user.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    text_user.focus_force()

    # Pack button frame && Init configure
    bu_frame = tk.Frame(root, bg="purple")
    bu_frame.pack(side=tk.BOTTOM, expand=0, fill=tk.X)
    but_list = []
    opts = skin().button_dic.copy()
    opts.update({'background': 'DeepSkyBlue'})

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

    button = tk.Button(
        bu_frame, text="Run", **opts,
        command=on_run)
    but_list.append(button)

    # Append clear
    def on_clear():
        text_user.pack_forget()

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
        bu.pack(side=tk.LEFT, expand=1, fill=tk.X)

    # Go
    root.mainloop()

    return root

"""
-l  log
-lc unicode
-lf +file descriptor: to log to file
-sb scrollback ability on
-c  +command: send command (just spawn, no exec like -e)
"""
import tkinter as tk
import subprocess as sp
from re import match
from threading import Thread
from queue import Queue

from abism.util import log


def create_console_window():
    # Init
    root = tk.Tk()
    queue = Queue()

    # Pack main frame
    termf = tk.Frame(root, width=800, height=800)
    termf.pack(fill=tk.BOTH, expand=tk.YES, padx=0, pady=0)
    wid = termf.winfo_id()

    # Allow window resize
    sp.Popen("""echo '*VT100.allowWindowOps: true' | xrdb -merge""", shell=True)

    # Craft command
    cmd = (
        # Create into me
        f'xterm -into {wid} -geometry 100x50 '
        # Log to stdout
        r'-sb -l -lc -lf /dev/stdout '
        # Launch `ps` command: output, tty, = for remove header
        """-e /bin/bash -c "ps -o tt=;bash" """
        r'| tee'
    )
    log(2,'Launching:', cmd)

    # Spawn Xterm
    process = sp.Popen(
        cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    log(2,'Xterm pid:', process.pid)

    # Get pts
    thread = Thread(target=lambda: get_xterm_pts(termf, process, queue))
    thread.start()

    # Set resize callback
    termf.bind("<Configure>", lambda event: on_resize(event, queue))

    # Start
    root.mainloop()


def on_resize(event, queue):
    """On resize: send escape sequence to pts"""
    # Magic && Check
    magic_x, magic_y = 6.1, 13
    log(2,'Resize (w, h):', event.width, event.height)
    if not queue.queue: return

    # Calculate
    width = int(event.width / magic_x)
    height = int(event.height / magic_y)
    log(2,'To (lin,col):', height, width)
    ctl = f"\u001b[8;{height};{width}t"

    # Send to pts
    with open(queue.queue[0], 'w') as f:
        f.write(ctl)


def get_xterm_pts(parent, process, queue):
    """Retrieve pts(`process`) -> `queue`"""
    while True:
        out = process.stdout.readline().decode()
        log(2,'Xterm out' + out)

        match_pts = match(r'pts/\d+', out)
        if match_pts:
            pts = '/dev/' + match_pts.group(0)
            log(2,'-----------> pts:', pts)
            queue.put(pts)
            break

        if out == b'' and process.poll() is not None:
            break

    # Resize now
    fake_event = tk.Event()
    fake_event.width = parent.winfo_width()
    fake_event.height = parent.winfo_height()
    on_resize(fake_event, queue)


def launch_kernel():
    """Launch a kernel (ipy, jupyter)
    The kernel is in a other thread
    that is why we need (200 lines) background-zmd-ipython
    """
    # Import
    try:
        from background_zmq_ipython import init_ipython_kernel
    except ImportError(e):
        log(0, "Error: cannot import background_zmq_ipython,\n"
            "install: background_zmq_ipython and xterm\n"
            "and try again", e)
        return

    def kernel_thread():
        init_ipython_kernel(user_ns=globals())

    thread = Thread(target=kernel_thread)
    thread.start()


def jupyter_window():
    launch_kernel()
    create_console_window()


if __name__ == '__main__':
    create_console_window()
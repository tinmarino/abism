"""
    Create:
        1. Jupyter kernel <- in current state
        2. Xterm console <- in new tk window
        3. Jupyter clien <- in xterm

    Xterm arguments:
        -l  log
        -lc unicode
        -lf +file descriptor: to log to file
        -sb scrollback ability on
        -c  +command: send command (just spawn, no exec like -e)
"""
import tkinter as tk
import subprocess as sp
import re
from threading import Thread
from queue import Queue
from io import StringIO

# pylint: disable = unused-wildcard-import, wildcard-import, unused-import
import abism.util as util
from abism.util import *


def create_tk_console():
    # Init
    root = tk.Tk()
    queue = Queue()
    root.title('Python console in xterm')

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
    log(3, 'Launching:', cmd)

    # Spawn Xterm
    process = sp.Popen(
        cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    log(3, 'Xterm pid:', process.pid)

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
    log(3, 'Resize (w, h):', event.width, event.height)
    if not queue.queue: return

    # Calculate
    width = int(event.width / magic_x)
    height = int(event.height / magic_y)
    log(3, 'To (lin,col):', height, width)
    ctl = f"\u001b[8;{height};{width}t"

    # Send to pts
    with open(queue.queue[0], 'w') as f:
        f.write(ctl)


def get_xterm_pts(parent, process, queue):
    """Retrieve pts(`process`) -> `queue`"""
    while True:
        out = process.stdout.readline().decode()
        log(3, 'Xterm out' + out)

        match_pts = re.match(r'pts/\d+', out)
        if match_pts:
            pts = '/dev/' + match_pts.group(0)
            log(3, '-----------> pts:', pts)
            queue.put(pts)
            break

        if out == b'' and process.poll() is not None:
            break

    # Resize now
    fake_event = tk.Event()
    fake_event.width = parent.winfo_width()
    fake_event.height = parent.winfo_height()
    on_resize(fake_event, queue)


def get_banner():
    return """Hello from ABISM background kernel Tread
print(sm)
print(root)
"""


def create_gnome_console(s_cmd):
    """Gnome terminal"""

    cmd = f"""gnome-terminal -e 'sh -c "{s_cmd}"'"""
    log(3, 'Launching ', cmd)
    sp.Popen(
        cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)


def launch_kernel():
    """Launch a kernel (ipy, jupyter)
    The kernel is in a other thread
    that is why we need (200 lines) background-zmd-ipython
    """
    # pylint: disable = possibly-unused-variable
    # Import
    try:
        from background_zmq_ipython import init_ipython_kernel
    except ImportError as e:
        log(0, "Error: cannot import background_zmq_ipython,\n"
            "install: background_zmq_ipython and xterm\n"
            "and try again", e)
        return False
    from time import sleep
    import logging
    t_cmd = "jupyter console --existing {}"

    sio = StringIO()
    logger = logging.Logger("ABISM kernel", level=logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sio))

    # Prepare namespacte()
    sm = get_state()
    root = get_root()

    # Init kernel
    init_ipython_kernel(
        user_ns={**globals(), **locals()}, redirect_stdio=True, banner=get_banner(),
        logger=logger
    )

    # Read output
    while True:
        out = sio.getvalue()
        sio.readline()
        log(3, 'Kernel out' + out)

        match_cfile = re.search(r'--existing (\S*)', out)
        if match_cfile:
            cfile = match_cfile.group(1)
            log(3, '-----------> cfile:', cfile)
            s_cmd = t_cmd.format(cfile)
            create_gnome_console(s_cmd)
            break
        sleep(0.1)


def create_jupyter_console():
    thread = Thread(target=launch_kernel)
    thread.start()
    #create_tk_console()


if __name__ == '__main__':
    create_jupyter_console()

"""
    Run abism code sync or async
"""
import threading

def run_sync():
    """Never returns"""
    run_helper(Namespace())


def run_async():
    """Returns: SthrelMeter, a cool object
    """
    abism_async = AbismAsync()
    print('Now we can continue running code while mainloop runs!')
    return abism_async


def run_helper(obj):
    """Returns: fill obj with some cool members"""
    # Parse arguments
    from abism.util import parse_argument
    parse_argument()

    # Create gui
    from abism.front.window_root import WindowRoot
    obj.root = WindowRoot()

    # Start gui loop
    obj.root.mainloop()


class AbismAsync(threading.Thread):
    """Asynchronous launch"""
    def __init__(self):
        self.root = None

        # Start thread
        threading.Thread.__init__(self)
        self.start()

        # Give info to caller
        import abism.util
        self.util = abism.util

        self.state = self.util.get_state()
        self.answers = self.state.answers

    def quit(self):
        self.root.quit()

    def run(self):
        run_helper(self)



class Namespace:
    """Cheat"""

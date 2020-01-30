"""
    Run abism code sync or async

functions: run_sync, run_async
"""
from abism.util import parse_argument

def _run_helper(obj):
    """Returns: fill obj with some cool members"""
    # Create gui
    from abism.front.window_root import WindowRoot
    obj.root = WindowRoot()

    # Start gui loop
    obj.root.mainloop()


def run_sync():
    """Never returns"""
    class Namespace:
        """Cheat"""
    parse_argument()
    print('Parsed initially:', parse_argument())

    _run_helper(Namespace())
    print('Bye')


def run_async(*argument):
    """Returns: SthrelMeter, a cool object
    """
    from threading import Thread
    import sys
    from abism.util import str_pretty
    class StrehlMeter:
        """StrehlMeter: object interface to Abism
        state   <- abism state frontend is sharing with backend
        root    <- root tk widget (i.e. gui window)
        util    <- function you could need
        answers <- the last answer list from backend (belongs to state)
        """
        __repr__ = str_pretty

    class AbismAsync(Thread):
        """Asynchronous launch"""
        def __init__(self):
            self.sm = StrehlMeter()
            self.sm.root = None

            # Start thread
            # with super -> AssertionError: group argument must be None for now
            Thread.__init__(self)
            self.start()

            # Give info to caller
            import abism.util
            self.sm.util = abism.util
            import abism.front.util_front
            self.sm.front_util = abism.front.util_front

            self.sm.state = self.sm.util.get_state()
            self.sm.answers = self.sm.state.answers

        def quit(self):
            self.sm.root.quit()

        def run(self):
            _run_helper(self.sm)

    def clear_all_cache():
        # pylint: disable = protected-access
        import functools
        import gc

        gc.collect()
        wrappers = [
            a for a in gc.get_objects()
            if isinstance(a, functools._lru_cache_wrapper)]

        for wrapper in wrappers:
            wrapper.cache_clear()
    # Hi
    print('---> Abism GUI called async')

    # Clear all cache (for tk photo)
    clear_all_cache()

    # Fake sys.args
    sys.argv = ['ipy'] + list(argument)
    parse_argument()

    # Launch Thread
    abism_async = AbismAsync()

    # Bye
    print('<--- Abism GUI is running')

    # Return to caller
    return abism_async.sm

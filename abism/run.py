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
    _run_helper(Namespace())
    print('Bye')


def run_async(*argument):
    """Returns: SthrelMeter, a cool object
    """
    from threading import Thread
    import sys
    class AbismAsync(Thread):
        """Asynchronous launch"""
        def __init__(self):
            self.root = None

            # Start thread
            # with super -> AssertionError: group argument must be None for now
            Thread.__init__(self)
            self.start()

            # Give info to caller
            import abism.util
            self.util = abism.util
            import abism.front.util_front
            self.front_util = abism.front.util_front

            self.state = self.util.get_state()
            self.answers = self.state.answers

        def quit(self):
            self.root.quit()

        def run(self):
            _run_helper(self)

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
    return abism_async

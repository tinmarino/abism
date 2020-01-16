"""
    So funny, there is nothing in this file and even thought, it is the most important to import.
    It is made in order to share the variables, you may want to read GlobalDefiner.
"""

from sys import stdout
import logging

# Exported
verbose = 0


# Logger
logging.basicConfig(stream=stdout, level=logging.DEBUG)
logger = logging.getLogger('abism')
logger.setLevel(logging.DEBUG)


def log(i, *args):
    """Log utility
    @brief: this is a log accroding to the verbose
            very simple function, very large comment
    @param: i is the verbose,
    @param: **args are the strings to print,
    @return: print in the stdout, means the calling terminal
        nickname py  me
        CRITICAL 50  -3
        ERROR    40  -2
        WARNING  30  -1
        INFO     20  1
        DEBUG    10  2
        NOTSET    0  3
    """
    _ = [logger.info(stg) for stg in args if verbose >= i]

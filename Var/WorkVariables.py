"""
    So funny, there is nothing in this file and even thought, it is the most important to import.
    It is made in order to share the variables, you may want to read GlobalDefiner.
"""

import logging

# Exported
verbose = 0


# Logger
logFormatter = logging.Formatter(
    'ABISM: %(asctime)-8s: %(message)s',
    '%H:%M:%S')

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(logFormatter)

logger = logging.getLogger('ABISM')
logger.setLevel(logging.INFO)
logger.handlers = [consoleHandler]


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
    if verbose < i: return

    message = str(i) + ': ' + ' '.join([str(arg) for arg in args])
    logger.info(message)

"""
    So funny, there is nothing in this file and even thought, it is the most important to import.
    It is made in order to share the variables, you may want to read GlobalDefiner.
"""


verbose = 0


def log(i, **args):
    """
    @brief: this is a log accroding to the verbose
            very simple function, very large comment
    @param: i is the verbose,
    @param: **args are the strings to print,
    @return: print(in the stdout, means the calling terminal)
    """
    if verbose >= i:
        print((args))
    return

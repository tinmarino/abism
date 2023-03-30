#!/usr/bin/env python3

"""
Get a list of all abysm file docstring
"""

import sys
from os.path import dirname

import pathlib
import importlib.util

def get_file_doc(fil):
    """ Get docstring from file
    From: https://stackoverflow.com/questions/67631
    -- how-can-i-import-a-module-dynamically-given-the-full-path
    """
    # Clause, some should not be imported
    if fil.name in (
            'abism.py',
            'setup.py',
            'get_file_docstring.py',
            '__main__.py',
            '__init__.py'
            ):
        return ""
    if '.ropeproject' in f'{fil}':
        return ""

    spec = importlib.util.spec_from_file_location("module.name", fil)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = module
    spec.loader.exec_module(module)
    res = module.__doc__.strip("\n").split("\n\n")[0]
    res = "\\n".join(res.split("\n"))
    return res


def get_file_docstring():
    """ Main """
    root_dir = dirname(dirname(__file__))
    sys.path.insert(0, root_dir)
    root_lib = pathlib.Path(root_dir)

    a_files = root_lib.glob('abism/**/*.py')

    # Pre
    print('my %file_doc = (')

    for fil in a_files:
        doc = get_file_doc(fil)
        name = fil.name.split(".")[0]
        print(name, " => '", doc, "',", sep="")

    # Post
    print(');')


if __name__ == '__main__':
    get_file_docstring()

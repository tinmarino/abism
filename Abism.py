#!/usr/bin/python
"""
    Adaptative Background Interactive Strehl Meter,
            A Software made by
    Julien Girard and Martin Tourneboeuf
"""

# Parse arguments
from util import parse_argument
parse_argument()


# Go
from front.WindowRoot import RootWindow
root_window = RootWindow()
root_window.mainloop()

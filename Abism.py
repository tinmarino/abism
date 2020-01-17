#!/usr/bin/python
"""
    Adaptative Background Interactive Strehl Meter,
            A Software made by
    Julien Girard and Martin Tourneboeuf
"""
# Standard
import sys
import os

#  Extend current path
path = os.path.dirname(os.path.abspath(__file__))
for root, _, _ in os.walk(path):
    sys.path.append(root)

# Local imports
from front.WindowRoot import RootWindow

# Go
root_window = RootWindow()
root_window.mainloop()

#!/usr/bin/python
"""
    Adaptative Background Interactive Strehl Meter,
            A Software made by
    Julien Girard and Martin Tourneboeuf
"""
# Standard
import sys
import os

# Get current path
path = os.path.dirname(os.path.abspath(__file__))

#  Extend current path
for root, _, _ in os.walk(path):
    sys.path.append(root)

# Local imports
from front.WindowRoot import RootWindow

# Go
root_window = RootWindow(root_path=path)
root_window.mainloop()

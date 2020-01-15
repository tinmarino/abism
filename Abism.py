#!/usr/bin/python
"""
    Adaptative Background Interactive Strehl Meter,
            A Software made by
    Julien Girard and Martin Tourneboeuf
"""
# Module imports
import WorkVariables as W
import MyGui as MG
import sys
import os

# matplotlib
# pyfits
# scipy.ndimage


# Add current folders to the python path
path = os.path.dirname(os.path.abspath(__file__))
for root, dirnames, filenames in os.walk(path):
    sys.path.append(root)

# Local imports


W.path = path
MG.MyWindow()                                           # Let's start

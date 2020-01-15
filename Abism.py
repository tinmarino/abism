#!/usr/bin/python
"""
    Adaptative Background Interactive Strehl Meter,
            A Software made by
    Julien Girard and Martin Tourneboeuf
"""
# Standard
import sys
import os

# Add current folders to the python path
path = os.path.dirname(os.path.abspath(__file__))
for root, dirnames, filenames in os.walk(path):
    sys.path.append(root)

# Local imports
import WorkVariables as W
import MyGui as MG

# Go
W.path = path
MG.MyWindow()

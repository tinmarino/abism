#!/usr/bin/python
"""
    Adaptative Background Interactive Strehl Meter,
            A Software made by
    Julien Girard and Martin Tourneboeuf
"""
# Module imports
import sys
import os

#matplotlib
#pyfits
#scipy.ndimage



# Add current folders to the python path
path = os.path.dirname( os.path.abspath(__file__)  )
for root, dirnames, filenames in os.walk(path):
    sys.path.append(root)

# Local imports
import MyGui as MG
import WorkVariables as W


W.path = path
MG.MyWindow()                                           # Let's start



"""

        In this script, I test all necessary imports, to see if ABISM can run
        without troubles. I report If I find an error.


Fit/leastsqbound.py:330:            from numpy.linalg import LinAlgError

Gui/DraggableColorbar.py:8:from scipy.ndimage import gaussian_filter
from scipy.optimize.minpack import _check_func

Gui/MyGui.py:8:from tkFileDialog import askopenfilename

    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
import WorkVariables

from threading import Thread
import multiprocessing
import os
import pdb
import popen
import re
import select
import settings
import signal
import sleep
import subprocess
import sys
import system
import threading
import time
import timeout
import traceback
import ttk
import warnings
import wraps

"""


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


def testAbismImports():
    importList = [
        'tkinter',      # A module wrapper to Tcl/Tk to build graphical interface
        'matplotlib',   # For graph, image display, here it is nested in Tk
        'Image',        # Librarie for Gaussian convolution
        'scipy',        # For the least square fit
        'numpy',        # For many functions and array type
        'astropy',      # Replace p.y.w.c.s and p.y.f.i.t.s
    ]

    for i in importList:
        if (!module_exists(i)):
            print("Warning : module " + i + " cannot be imported")

    # To nest matplotlib in Tkinter

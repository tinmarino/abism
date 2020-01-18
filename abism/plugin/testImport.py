"""

        In this script, I test all necessary imports, to see if ABISM can run
        without troubles. I report If I find an error.
To nest matplotlib in Tkinter


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

tkinter: apt install python3-tk

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


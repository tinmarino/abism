""" This is a modificable file to run with iteractive python console for debuggingi,
    it will be called by exec (import ToRun) """

import matplotlib
import pyfits
import numpy as np

from tkinter import *
from tkinter.filedialog import askopenfilename
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas

# Gui
import InitGui as IG  # draw the GUI
import Pick
import DraggableColorbar
import mynormalize
import AnswerReturn as AR

# ArrayFunction
import Scale
import Stat
import ImageFunction as IF  # Function on images
import BasicFunction as BF  # 2D psf functions

# Variables
import GuyVariables as G
import WorkVariables as W

# Plugin
import ReadHeader as RH


G.ax1.annotate("",
               xy=(0.2, 0.3), xycoords='axes fraction',
               xytext=(0.5, 0.5), textcoords='axes fraction',
               arrowprops=dict(arrowstyle="->", facecolor="purple", edgecolor="purple",
                               connectionstyle="arc3"),
               )

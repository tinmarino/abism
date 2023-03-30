#!/usr/bin/env python3

"""
Collection of matplotlib artists.
For drawing on the plots.
With ellipse, annulus, square.

ABISM artist collection for drawing figures in matplotlib
Classes ar Cicle Annulus, Square, etc and they inherit from my custom Artist

Note that all x,y are given for an array, in the image display, x and y must be switched
IDEA: refactor: mutualize more code
"""

# pylint: disable=broad-except
# pylint: disable=too-many-instance-attributes

from abc import ABC, abstractmethod

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from abism.util import log
from abism.front.util_front import is_toolbar_active


class Artist(ABC):
    """ Default artist, generic drawer """

    def __init__(self, figure, axe, array=None, callback=None):
        """array is the array called by imshow"""
        self.fig = figure
        self.axe = axe
        self.array = array
        self.callback = callback

        # A center always
        self.x0 = self.y0 = 0

    @abstractmethod
    def connect(self):
        """ Create """

    @abstractmethod
    def disconnect(self):
        """ Destroy """


class Annulus(Artist):
    """ This is actually the Annulus even, but it could be a "ellipse" event or
    whatever can fit in the canvas class (rectangle, polygon...) , actually I
    deleted the ellispe event, which can be usefull because not every body want
    the annulus for the background, but maybe make a super fast photometry,
    like knowing the instrument, you know the PSF FWHM and can auto create the
    aperture, you play with that and then, if its works well, you can auto
    detect stars and make a completely automatic ABism (ie, without opening
    image)  , see in Abism 0.5, 0.6
    Note 2020: Well in your dream !
    """

    def __init__(self, figure, axe, array=None, callback=None):
        super().__init__(figure, axe, array=array, callback=callback)
        self.fig = figure
        self.axe = axe

        self.artist_list = []  # Filled in InitAnnulus and modified in event_motion
        # number of key operation to make like if you press 5r,
        # the r operation is done 5 times we put 0 to concatenate
        self.num_key = ""

        if array is not None:
            self.array = array

        self.param_definer()  # initial parameters, at the end of this file
        self.init(None)
        self.connect()
        plt.show()  # otherwise, nothing

    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.cid_motion)
        self.fig.canvas.mpl_disconnect(self.cid_key_press)
        self.fig.canvas.mpl_disconnect(self.cid_button_press)
        self.fig.canvas.mpl_disconnect(self.cid_zoom)

    def connect(self):
        """ matplotlib connections, the connections are "self"
        because we need to disconnect it (replace connect by disconnect)
        """
        # Motion
        self.cid_motion = self.fig.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

        # Key
        self.cid_key_press = self.fig.canvas.mpl_connect(
            'key_press_event', self.on_press)

        # Click
        self.cid_button_press = self.fig.canvas.mpl_connect(
            'button_press_event', self.on_click)

        # Zoom
        self.cid_zoom = self.fig.canvas.mpl_connect(
            'draw_event', self.init)

        ###################
        # EVENTS
        ##################

    def on_motion(self, event):
        """ Event: on motion => move """
        log(9, "annulus detect motion")
        if not event.inaxes:
            return
        self.y0, self.x0 = event.xdata, event.ydata
        self.draw()
        return

    def on_click(self, event):
        """ Event: on motion => work """
        if not event.inaxes:
            return
        self.y0, self.x0 = event.xdata, event.ydata
        self.callback(self)

    def on_press(self, event):
        """ Event: on motion => redraw """
        if not event.inaxes:
            return
        try:
            try:
                self.num_key = int(self.num_key + event.key)
            except BaseException:
                self.num_key = int(str(self.num_key) + event.key)
        except BaseException:
            if self.num_key == "":
                self.num_key = 1
            for _ in range(self.num_key):
                self.modify(event.key)
            self.num_key = ""
        self.draw()
        return

    def modify(self, string):
        """ To modify self parameters, called by AnnulusOnpress """
        # pylint: disable = too-many-branches

        # radius_u
        if string == "r":    # radius_u
            self.radius_u -= 1
            self.inner_u -= 1
            self.outer_u -= 1
        elif string == "R":   # radius_u
            self.radius_u += 1
            self.inner_u += 1
            self.outer_u += 1

        # radius_v
        elif string == "e":    # radius_u
            self.rapport /= 1.11
        elif string == "E":    # radius_u
            self.rapport /= 0.9

        # OUTER
        elif string == "o":    # radius_u
            self.outer_u -= 1
        elif string == "O":    # radius_u
            self.outer_u += 1

        # INNER
        elif string == "i":    # radius_u
            self.inner_u -= 1
        elif string == "I":    # radius_u
            self.inner_u += 1

        # THETA ANGLE
        elif string == ("t" or "a"):
            self.theta += 0.174  # 10 degree in rad
        elif string == ("T" or "A"):
            self.theta -= 0.174

        # POSITION
        elif string == "up":
            self.x0 -= 1
        elif string == "down":
            self.x0 += 1
        elif string == "left":
            self.y0 -= 1
        elif string == "right":
            self.y0 += 1

    def remove_artist(self, draw=True):
        """ Clear """
        for i in self.artist_list:
            i.remove()
            # try : i.remove()
            # except : pass
        self.artist_list = []
        if draw:
            self.fig.canvas.draw()

    def draw_artist(self):
        """ Draw figure """
        self.fig.canvas.restore_region(self.bg)  # create backup
        for i in self.artist_list:
            self.axe.draw_artist(i)  # create artist
            # try : self.axe.add_patch(i)
            # except : pass
        self.fig.canvas.blit(self.axe.bbox)  # blit both

    def init(self, _):
        """Unused event (bad design)"""
        self.remove_artist(draw=False)  # Important not to draw
        # self.fig.canvas.draw()
        self.bg = self.fig.canvas.copy_from_bbox(self.axe.bbox)

        # facecolor, edgecolor,linestyle,alpha    for out, in , phot
        for i in [
                ["None", "black", "dashed", 1],
                ["None", "black", "dashed", 1],
                ["black", "black", "solid", 0.3]]:
            # OUT
            ell = matplotlib.patches.Ellipse(
                xy=(0, 0), width=1, height=1,
                facecolor=i[0], edgecolor=i[1], linestyle=i[2], alpha=i[3])
            self.axe.add_patch(ell)
            self.artist_list.append(ell)

    def draw(self):  # All the ellipses
        """ Draw inner outer and photometry ellipse """
        # self.remove_artist(draw=False)

        # theta is the same, just, x and y direction where change by width and
        # height
        theta = 180 * self.theta / np.pi

        def draw_out(ell):
            """ Helper: outer range """
            ell.width = 2 * self.outer_u * self.rapport   # array to image invert
            ell.height = 2 * self.outer_u
            ell.center = (self.y0, self.x0)
            ell.angle = theta
            # 'solid' | 'dashed' | 'dashdot' | 'dotted'

        def draw_in(ell):
            """ Helper: inner range """
            ell.width = 2 * self.inner_u * self.rapport   # array to image invert
            ell.height = 2 * self.inner_u
            ell.center = (self.y0, self.x0)
            ell.angle = theta

        def draw_ell(ell):
            """ Helper: Ellipse """
            ell.width = 2 * self.radius_u * self.rapport   # array to image invert
            ell.height = 2 * self.radius_u
            ell.center = (self.y0, self.x0)
            ell.angle = theta

        draw_out(self.artist_list[0])
        draw_in(self.artist_list[1])
        draw_ell(self.artist_list[2])

        self.draw_artist()

    # called first, all params possible should be here., even if it is just
    # None

    def param_definer(self):
        """ Set parameters at start (hardcode) """

        # SPHERE
        self.radius = 10

        # ELLIPSE
        self.radius_u = 10          # called r (radius)
        self.rapport = 1     # called by e (eccentricity)
        # self.radius_v = self.radius_u *self.rapport # stille used by ellipse
        self.theta = 0         # called t or a (theta, angle)

        # Annnulus
        self.inner_u = 10  # called i
        self.outer_u = 20  # called o


class Ellipse(Artist):
    """ Draw an ellipse """

    def __init__(self, figure, axe, array=None, callback=None):
        """array is the array called by imshow"""
        super().__init__(figure, axe, array=array, callback=callback)

        self.artist = ""
        # number of key operation to make like if you press
        # 5r, the r operation is done 5 times we put 0 to concatenate
        self.num_key = ""
        self.zoom_bool = False
        self.bg = None

        self.param_definer()  # initial parameters, at the end of this file
        self.draw_artist()
        self.connect()
        plt.show()
        # self.fig.canvas.show()  # otherwise, nothing
        # self.fig.canvas.show()  # otherwise, nothing

    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.cid_motion)
        self.fig.canvas.mpl_disconnect(self.cid_key_press)
        self.fig.canvas.mpl_disconnect(self.cid_button_press)

    def connect(self):
        """matplotlib connections, the connections are "self" because
        we need to disconnect it (replace connect by disconnect) """
        log(9, "Ellipse connecting")

        # Motion
        self.cid_motion = self.fig.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

        # Key
        self.cid_key_press = self.fig.canvas.mpl_connect(
            'key_press_event', self.on_press)

        # Click
        self.cid_button_press = self.fig.canvas.mpl_connect(
            'button_press_event', self.on_click)

        # Zoom
        self.cid_zoom = self.fig.canvas.mpl_connect(
            'draw_event', self.on_zoom)

    def on_motion(self, event):
        """ Event: move mouse -> set and redraw ellipse """
        if not event.inaxes:
            return
        self.y0, self.x0 = event.xdata, event.ydata
        self.draw()
        return

    def on_click(self, event):  # mouse click
        """ Event: click mouse -> work """
        if not event.inaxes:
            return
        self.y0, self.x0 = event.xdata, event.ydata
        self.callback()

    def on_press(self, event):
        """ Event: press mouse -> start pane and zoom """
        # pylint: disable = too-many-locals
        log(5, 'Ellipse receive:', event)
        self.zoom_bool = True

        def a_inc():
            self.radius_u += 1
            self.radius_v += 1

        def a_dec():
            self.radius_u -= 1
            self.radius_v -= 1

        def u_inc():
            self.radius_u += 1

        def u_dec():
            self.radius_u -= 1

        def v_inc():
            self.radius_v += 1

        def v_dec():
            self.radius_v -= 1

        def r_inc():
            self.theta -= 0.174  # 10 degree in rad

        def r_dec():
            self.theta += 0.174  # 10 degree in rad

        def pane_up():
            self.x0 -= 1

        def pane_down():
            self.x0 += 1

        def pane_left():
            self.y0 -= 1

        def pane_right():
            self.y0 += 1

        def prt():
            log(0, vars(self))

        press_dic = {
            # eXpand
            "X": a_inc,
            "x": a_dec,

            # U axe
            "U": u_inc,
            "u": u_dec,

            # V axe
            "V": v_inc,
            "v": v_dec,

            # ROtate
            "R": r_inc,
            "O": r_inc,
            "r": r_dec,
            "o": r_dec,

            # position
            "up": pane_up,
            "k": pane_up,
            "J": pane_up,

            "down": pane_down,
            "j": pane_down,
            "K": pane_down,

            "left": pane_left,
            "h": pane_left,
            "L": pane_left,

            "right": pane_right,
            "l": pane_right,
            "H": pane_right,

            # Print, like Photon, it is its own anti-command
            "p": prt,
            "P": prt,
        }

        if event.key in press_dic:
            press_dic[event.key]()

        self.draw()
        self.zoom_bool = False

        return press_dic

    def on_zoom(self, _):
        """ Event: zoom """
        if self.zoom_bool:
            return

        self.remove_artist(draw=False)  # Important not to draw if zoom
        self.bg = self.fig.canvas.copy_from_bbox(self.axe.bbox)

    def remove_artist(self, draw=True):
        """ Destroy helper """
        try:
            self.artist.remove()
        except BaseException:
            log(3, "I cannot remove artist Ellispe")
        if draw:
            self.fig.canvas.draw()

    def draw_artist(self):
        """ Draw helper """
        self.fig.canvas.restore_region(self.bg)  # create backup
        if self.zoom_bool:
            self.remove_artist()
            self.axe.add_patch(self.artist)  # needed !!
        self.axe.draw_artist(self.artist)  # create artist
        self.fig.canvas.blit(self.axe.bbox)  # s blit both

    def draw(self):
        """ Malplotlib binding to draw """
        self.artist.center = (self.y0, self.x0)
        self.artist.width = 2 * self.radius_v   # array to image invert
        self.artist.height = 2 * self.radius_u
        # theta is the same, just, x and y direction where change by width and
        # height
        self.artist.angle = 180 * self.theta / np.pi
        self.draw_artist()

    # called first, all params possible should be here., even if it is just
    # None
    def param_definer(self):
        """ Init param """

        # ELLIPSE
        self.radius_u = 20          # called r (radius)
        self.radius_v = 20          # called by e (eccentricity)
        self.theta = 0         # called t or a (theta, angle)

        # facecolor, edgecolor,linestyle,alpha    for out, in , phot
        i = ["green", "blue", "dashed", 0.8]
        self.artist = matplotlib.patches.Ellipse(
            xy=(200, 200), width=100, height=100,
            facecolor=i[0], edgecolor=i[1], linestyle=i[2], alpha=i[3])
        self.remove_artist(draw=False)  # Important not to draw if zoom
        self.bg = self.fig.canvas.copy_from_bbox(self.axe.bbox)
        self.axe.add_patch(self.artist)  # it works like this so why to ask

        ##############
        # PROFILE
        #############


class Profile(Artist):
    """ Alias Line
    Callback : recevese self (point1 and point2)
    """

    def __init__(self, fig, axe, callback=None):
        super().__init__(fig, axe, array=None, callback=callback)

        self.point1 = None
        self.point2 = None
        self.line = None
        self.bg = None

        self.connect()

    def connect(self):
        """ Start """
        self.cid_press_event = self.fig.canvas.mpl_connect(
            "button_press_event", self.on_press)
        self.cid_motion_event = self.fig.canvas.mpl_connect(
            "motion_notify_event", self.on_motion)
        self.cid_release_event = self.fig.canvas.mpl_connect(
            "button_release_event", self.on_release)

    def disconnect(self):
        """ End """
        try:
            self.fig.canvas.mpl_disconnect(self.cid_press_event)
        except BaseException:
            log(3, "artist.profile cannot deisconnect press ")
        try:
            self.fig.canvas.mpl_disconnect(self.cid_motion_event)
        except BaseException:
            log(3, "artist.profile cannot disconnect motion ")
        try:
            self.fig.canvas.mpl_disconnect(self.cid_release_event)
        except BaseException:
            log(3, "artist.profile cannot disconnect release  ")

    def on_press(self, event):
        """ Event: press -> start line """
        # Clause: want axes and not active toolbar
        if not event.inaxes:
            return
        toolbar = event.inaxes.figure.canvas.toolbar
        if is_toolbar_active(toolbar):
            log(3, "WARNING: Zoom or Pan actif, "
                   "please unselect its before picking your object")
            return

        self.remove_artist(draw=True)  # Important not to draw
        self.point1 = [event.ydata, event.xdata]
        self.bg = self.fig.canvas.copy_from_bbox(self.axe.bbox)

        self.line = matplotlib.lines.Line2D(xdata=(0, 0), ydata=(
            0, 0), linewidth=2, color='red', alpha=1)
        self.draw_artist()

        return

    def on_motion(self, event):
        """ Event: move mouse -> set and redraw artist """
        if self.point1 is None:
            return
        self.point2 = [event.ydata, event.xdata]
        # here we invert because matplotlib take x y and we work in row column
        self.line.set_data([[self.point1[1], self.point2[1]],
                         [self.point1[0], self.point2[0]]])
        self.draw_artist()

    def on_release(self, _):
        """ Event: release -> work """
        self.callback(self)
        self.point1 = None

    def remove_artist(self, draw=True):
        """ Remove line and binding """
        if self.line is not None:
            try:
                self.axe.lines.pop(0)
            except BaseException:
                pass
            try:
                self.line.remove()  # in case we have no l yet
            except BaseException:
                pass
        self.line = None
        if draw:
            self.fig.canvas.draw()

    def draw_artist(self):
        """ Draw line """
        self.fig.canvas.restore_region(self.bg)  # create backup
        self.axe.add_line(self.line)
        self.axe.draw_artist(self.line)  # create artist
        self.line.remove()
        self.fig.canvas.blit(self.axe.bbox)  # blit both
        # self.fig.canvas.draw_idle()

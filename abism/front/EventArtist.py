""" Note that all x,y are given for an array, in the image display, x and y must be switched """
import numpy as np
import matplotlib.pyplot as plt
import matplotlib



from abism.util import log


class Annulus:
    """This is actually the Annulus even, but it could be a "ellipse" event or
    whatever can fit in the canvas class (rectangle, polygone...) , actually I
    deleted the ellispe event, which can be usefull because not every body want
    the annulus for the background, but maybe make a super fast photometry,
    like knowing the instrument, you know the PSF FWHM and can auto create the
    aperture, you play with that and then, if its works well, you can auto
    detect stars and make a completely automatic ABism (ie, without opening
    image)  , see in Abism
    0.5, 0.6"""
    def __init__(self, figure, ax, array=None):  # array is the array called by imshow
        self.fig = figure
        self.ax = ax
        self.type = type  # ellipse or annulus
        self.artist_list = []  # Filled in InitAnnulus and modified in event_motion
        # number of key operation to make like if you press 5r,
        # the r operation is done 5 times we put 0 to concatenate
        self.num_key = ""

        if array != None:
            self.array = array

        self.ParamDefiner()  # initial parameters, at the end of this file
        self.Init(None)
        self.Connect()
        plt.show()  # otherwise, nothing

        # CONNECTION

    def Disconnect(self):
        self.fig.canvas.mpl_disconnect(self.cid_motion)
        self.fig.canvas.mpl_disconnect(self.cid_key_press)
        self.fig.canvas.mpl_disconnect(self.cid_button_press)
        self.fig.canvas.mpl_disconnect(self.cid_zoom)

    def Connect(self):
        """matplotlib connections, the connections are "self" because we need to disconnect it (replace connect by disconnect) """
        # MOTION
        self.cid_motion = self.fig.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)
        # KEY
        self.cid_key_press = self.fig.canvas.mpl_connect(
            'key_press_event', self.on_press)
        # CLICK
        self.cid_button_press = self.fig.canvas.mpl_connect(
            'button_press_event', self.on_click)
        # ZOOM
        self.cid_zoom = self.fig.canvas.mpl_connect(
            'draw_event', self.Init)

        ###################
        # EVENTS
        ##################

    def on_motion(self, event):
        log(9, "annulus detect motion")
        if not event.inaxes:
            return
        self.y0, self.x0 = event.xdata, event.ydata
        self.Draw()
        return

    def on_click(self, event):  # mouse click
        if not event.inaxes:
            return
        self.y0, self.x0 = event.xdata, event.ydata
        self.callback(self)

    def on_press(self, event):
        if not event.inaxes:
            return
        try:
            try:
                self.num_key = int(self.num_key + event.key)
            except:
                self.num_key = int(str(self.num_key) + event.key)
        except:
            if self.num_key == "":
                self.num_key = 1
            for i in range(self.num_key):
                self.Modify(event.key)
            self.num_key = ""
        self.Draw()
        return

    def Modify(self, string):  # modify self.params
        """To modify self parameters, called by AnnulusOnpress"""

        # rU
        if string == "r":    # ru
            self.ru -= 1
            self.inner_u -= 1
            self.outter_u -= 1
        elif string == "R":   # ru
            self.ru += 1
            self.inner_u += 1
            self.outter_u += 1

        # RV
        elif string == "e":    # ru
            self.rapport /= 1.11
        elif string == "E":    # ru
            self.rapport /= 0.9

        # OUTER
        elif string == "o":    # ru
            self.outter_u -= 1
        elif string == "O":    # ru
            self.outter_u += 1

        # INNER
        elif string == "i":    # ru
            self.inner_u -= 1
        elif string == "I":    # ru
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

        # KNOW
        elif string == "p":  # print( )
            def PD(dic):  # Write dictionary for RunCommand
                for k in dic.keys():
                    print('%.20s    %.20s' % (k, dic[k]))

        # OVER
        return

        #################
        # DRAW
        ###############

    def RemoveArtist(self, draw=True):
        for i in self.artist_list:
            i.remove()
            # try : i.remove()
            # except : pass
        self.artist_list = []
        if draw:
            self.fig.canvas.draw()

    def DrawArtist(self):
        self.fig.canvas.restore_region(self.bg)  # create backup
        for i in self.artist_list:
            self.ax.draw_artist(i)  # create artist
            # try : self.ax.add_patch(i)
            # except : pass
        self.fig.canvas.blit(self.ax.bbox)  # blit both

    def Init(self, event):
        self.RemoveArtist(draw=False)  # Important not to draw
        # self.fig.canvas.draw()
        self.bg = self.fig.canvas.copy_from_bbox(self.ax.bbox)

        # facecolor, edgecolor,linestyle,alpha    for out, in , phot
        for i in [["None", "black", "dashed", 1],    ["None", "black", "dashed", 1],    ["black", "black", "solid", 0.3]]:
            # OUT
            ell = matplotlib.patches.Ellipse(xy=(0, 0), width=1, height=1,
                                             facecolor=i[0], edgecolor=i[1], linestyle=i[2], alpha=i[3])
            self.ax.add_patch(ell)
            self.artist_list.append(ell)

    def Draw(self):  # All the ellipses
        """ Draw inner outer and photometry ellipse """
        # self.RemoveArtist(draw=False)

        # theta is the same, just, x and y direction where change by width and height
        theta = 180 * self.theta / np.pi

        def Out(ell):
            ell.width = 2*self.outter_u * self.rapport   # array to image invert
            ell.height = 2 * self.outter_u
            ell.center = (self.y0, self.x0)
            ell.angle = theta
            #'solid' | 'dashed' | 'dashdot' | 'dotted'

        def In(ell):
            ell.width = 2*self.inner_u * self.rapport   # array to image invert
            ell.height = 2 * self.inner_u
            ell.center = (self.y0, self.x0)
            ell.angle = theta

        def Ell(ell):
            ell.width = 2*self.ru * self.rapport   # array to image invert
            ell.height = 2 * self.ru
            ell.center = (self.y0, self.x0)
            ell.angle = theta

        Out(self.artist_list[0])
        In(self.artist_list[1])
        Ell(self.artist_list[2])

        self.DrawArtist()
        return

        ########
        # PARAMS

    # called first, all params possible should be here., even if it is just None
    def ParamDefiner(self):

        # SPHERE
        self.radius = 10

        # ELLIPSE
        self.ru = 10          # called r (radius)
        self.rapport = 1     # called by e (eccentricity)
        # self.rv = self.ru *self.rapport # stille used by ellipse
        self.theta = 0         # called t or a (theta, angle)

        # Annnulus
        self.inner_u = 10  # called i
        self.outter_u = 20  # called o

        return

        #############
        # ELLIPSE
        #############


class Ellipse:
    def __init__(self, figure, ax, array=None, callback=None):
        """array is the array called by imshow"""
        self.fig = figure
        self.ax = ax
        self.array = array
        self.callback = callback

        self.artist = ""
        self.num_key = ""    # number of key operation to make like if you press   5r, the r operation is done 5 times we put 0 to concatenate
        self.zoom_bool = False

        self.ParamDefiner()  # initial parameters, at the end of this file
        self.DrawArtist()
        self.Connect()
        plt.show()
        # self.fig.canvas.show()  # otherwise, nothing
        # self.fig.canvas.show()  # otherwise, nothing

    def Disconnect(self):
        self.fig.canvas.mpl_disconnect(self.cid_motion)
        self.fig.canvas.mpl_disconnect(self.cid_key_press)
        self.fig.canvas.mpl_disconnect(self.cid_button_press)

    def Connect(self):
        """m atplotlib connections, the connections are "self" because we need to disconnect it (replace connect by disconnect) """

        # MOTION
        self.cid_motion = self.fig.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)
        # KEY
        self.cid_key_press = self.fig.canvas.mpl_connect(
            'key_press_event', self.on_press)
        # CLICK
        self.cid_button_press = self.fig.canvas.mpl_connect(
            'button_press_event', self.on_click)
        # ZOOM
        self.cid_zoom = self.fig.canvas.mpl_connect(
            'draw_event', self.on_zoom)

    def on_motion(self, event):
        if not event.inaxes:
            return
        self.y0, self.x0 = event.xdata, event.ydata
        self.Draw()
        return

    def on_click(self, event):  # mouse click
        if not event.inaxes:
            return
        self.y0, self.x0 = event.xdata, event.ydata
        self.callback()

    def on_press(self, event):  # key
        self.zoom_bool = True

        if event.key == "R":
            self.ru += 1
            self.rv += 1
            self.Draw()
        elif event.key == "r":
            self.ru -= 1
            self.rv -= 1
            self.Draw()

        elif event.key == "U":
            self.ru += 1
            self.Draw()
        elif event.key == "u":
            self.ru -= 1
            self.Draw()

        elif event.key == "V":
            self.rv += 1
            self.Draw()
        elif event.key == "v":
            self.rv -= 1
            self.Draw()

        # THETA ANGLE
        elif event.key == ("t" or "a"):
            self.theta += 0.174  # 10 degree in rad
            self.Draw()
        elif event.key == ("T" or "A"):
            self.theta -= 0.174
            self.Draw()

        # POSITION
        elif event.key == "up":
            self.x0 -= 1
            self.Draw()
        elif event.key == "down":
            self.x0 += 1
            self.Draw()
        elif event.key == "left":
            self.y0 -= 1
            self.Draw()
        elif event.key == "right":
            self.y0 += 1
            self.Draw()

        # KNOW
        elif event.key == "p":
            log(0, vars(self))
            self.Draw()

        self.zoom_bool = False
        return

    def on_zoom(self, event):
        if self.zoom_bool:
            return
        self.RemoveArtist(draw=False)  # Important not to draw if zoom
        self.bg = self.fig.canvas.copy_from_bbox(self.ax.bbox)

    def RemoveArtist(self, draw=True):
        try:
            self.artist.remove()
        except:
            log(3, "I cannot remove artist Ellispe")
        if draw:
            self.fig.canvas.draw()

    def DrawArtist(self):
        self.fig.canvas.restore_region(self.bg)  # create backup
        if self.zoom_bool:
            self.RemoveArtist()
            self.ax.add_patch(self.artist)  # needed !!
        self.ax.draw_artist(self.artist)  # create artist
        self.fig.canvas.blit(self.ax.bbox)  # s blit both

    def Draw(self):
        self.artist.center = (self.y0, self.x0)
        self.artist.width = 2*self.rv   # array to image invert
        self.artist.height = 2 * self.ru
        # theta is the same, just, x and y direction where change by width and height
        self.artist.angle = 180 * self.theta / np.pi
        self.DrawArtist()
        return

    # called first, all params possible should be here., even if it is just None
    def ParamDefiner(self):

        # ELLIPSE
        self.ru = 20          # called r (radius)
        self.rv = 20          # called by e (eccentricity)
        self.theta = 0         # called t or a (theta, angle)

        # facecolor, edgecolor,linestyle,alpha    for out, in , phot
        i = ["green", "blue", "dashed", 0.8]
        self.artist = matplotlib.patches.Ellipse(xy=(200, 200), width=100, height=100,
                                                 facecolor=i[0], edgecolor=i[1], linestyle=i[2], alpha=i[3])
        self.RemoveArtist(draw=False)  # Important not to draw if zoom
        self.bg = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.add_patch(self.artist)  # it works like this so why to ask

        ##############
        # PROFILE
        #############


class Profile:
    """Alias Line
    Callback : recevese self (point1 and point2)
    """
    def __init__(self, fig, ax, callback=None):
        self.point1 = None  # to know if we cicked yet
        self.l = None
        self.fig = fig
        self.ax = ax
        self.callback=callback

        # self.InitProfile(None) # argument in case we are in a zoom  and need to change background
        self.Connect()

    def Connect(self):
        self.cid_press_event = self.fig.canvas.mpl_connect(
            "button_press_event", self.on_press)
        self.cid_motion_event = self.fig.canvas.mpl_connect(
            "motion_notify_event", self.on_motion)
        self.cid_release_event = self.fig.canvas.mpl_connect(
            "button_release_event", self.on_release)

    def Disconnect(self):
        try:
            self.fig.canvas.mpl_disconnect(self.cid_press_event)
        except:
            log(3, "EventArtist.profile cannot deisconnect press ")
        try:
            self.fig.canvas.mpl_disconnect(self.cid_motion_event)
        except:
            log(3, "EventArtist.profile cannot disconnect motion ")
        try:
            self.fig.canvas.mpl_disconnect(self.cid_release_event)
        except:
            log(3, "EventArtist.profile cannot disconnect release  ")

    def on_press(self, event):
        if not event.inaxes:
            return
        toolbar = event.inaxes.figure.canvas.toolbar
        if toolbar._active in ('PAN', 'ZOOM'):
            log(3, "WARNING: Zoom or Pan actif, "
                "please unselect its before picking your object")
            return
        self.RemoveArtist(draw=True)  # Important not to draw
        self.point1 = [event.ydata, event.xdata]
        self.bg = self.fig.canvas.copy_from_bbox(self.ax.bbox)

        self.l = matplotlib.lines.Line2D(xdata=(0, 0), ydata=(
            0, 0), linewidth=2, color='red', alpha=1)
        self.DrawArtist()

        return

    def on_motion(self, event):
        if self.point1 is None:
            return
        self.point2 = [event.ydata, event.xdata]
        # here we invert because matplotlib take x y and we work in row column
        self.l.set_data([[self.point1[1], self.point2[1]],
                         [self.point1[0], self.point2[0]]])
        self.DrawArtist()

    def on_release(self, event):
        self.callback(self)
        self.point1 = None

        # self.my_point2 = [event.ydata,event.xdata] # invert
        #self.my_point1 = [self.my_point1[1],self.my_point1[0]]
        # self.RemoveArtist()
        #import AnswerReturn as AR
        # AR.ProfileAnswer()

        ####
        # DRAW
        ##########

    def RemoveArtist(self, draw=True):
        if self.l != None:
            try:
                self.ax.lines.pop(0)
            except:
                pass
            try:
                self.l.remove()  # in case we have no l yet
            except:
                pass
        self.l = None
        self.my_point1 = None
        if draw:
            self.fig.canvas.draw()

    def DrawArtist(self):
        self.fig.canvas.restore_region(self.bg)  # create backup
        self.ax.add_line(self.l)
        self.ax.draw_artist(self.l)  # create artist
        self.l.remove()
        self.fig.canvas.blit(self.ax.bbox)  # blit both
        # self.fig.canvas.draw_idle()

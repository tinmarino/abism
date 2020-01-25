"""
    Pick star and call back
"""
from abc import ABC, abstractmethod

import matplotlib
import numpy as np

from abism.front import artist
from abism.front.matplotlib_extension import center_handler
from abism.front import AnswerReturn as AR

from abism.back import Strehl
import abism.back.util_back as W

from abism.util import log, get_root, get_state

# TODO remove
from abism.back import ImageFunction as IF
from abism.front import util_front as G



# TODO rewrite totally at end of refactoring
def RefreshPick(label):
    """The exported routine
    In function of the name of G.connect_var, we call the good one.
    Disconnect old pick event and connect the new one """
    lst = np.array([
        ["PickOne", "one", PickOne],  # 0 OK
        ["Binary Fit", "binary", PickBinary],  # 1
        # ["Tight Binary", "tightbinary", TightBinary],  # 2 # TODO ?
        ["Profile", "profile", PickProfile],  # 3
        ["Stat", "stat", PickStat],  # 4
        ["Annulus", "annulus", PickAnnulus],  # 5
        ["Ellipse", "ellipse", PickEllipse],  # 6 OK
        ["No Pick", "nopick", NoPick],  # 7 OK
    ])

    get_state().pick_old = get_state().pick_type
    index = list(lst[:, 1]).index(label)   # or G.connect_var.get()
    get_state().pick_type = label
    # because they are in tools, and it disable the connection,
    # I don't know why


    # TODO di I break something,
    # <-- yes the string_var aut
    # if label != "stat" or label != "profile":
    #     G.cu_pick.set(label)

    # Dicconnect old
    pick_old = get_state().pick
    if pick_old:
        pick_old.disconnect()

    # Connect new
    pick = lst[index, 2]()
    pick.connect()
    get_state().pick = pick


class Pick(ABC):
    """Class for a connection:
    image event -> operation (then result display)
    Note: disconnection is not generic:
        sometime a matplotlit callback_id
        sometime a cutom artist
    """
    def __init__(self):
        self.canvas = get_root().frame_image.get_canvas()
        self.figure = get_root().frame_image.get_figure()
        self.ax = self.figure.axes[0]

    @abstractmethod
    def connect(self): pass

    @abstractmethod
    def disconnect(self): pass

    @abstractmethod
    def work(self, obj): pass

class PickOne(Pick):
    """Pick One Star
    This button should be green and the zoom button of the image toolbar
    unpressed. If it is pressed, clik again on it. You then have to draw a
    rectangle aroung the star to mesure the strehl ratio around this star.  A
    first fit will be computed in the rectangle you've just drawn. Then the
    photometry of the star will be computed according to the photometry and
    background measurement type you chose in 'MoreOption' in the file menu. By
    default, the photometry is processed in a 99% flux rectangle.  And the
    background, in 8 little rectangles around the star.
    The fit is necessary to get the maximum, the peak of the psf that will be
    compared to the diffraction pattern. You can set to assess the photometry
    of the object with the fit.  A Moffat fit type is chosen by default. but
    you can change it with the button FitType. I recommend you to use a
    Gaussian for Strehl <5%, A Moffat for intermediate Strehl and a Bessel for
    strehl>60%."
    """
    def __init__(self):
        super().__init__()
        self.rectangle_selector = None

        # The id of connection (alias callback), to be disabled
        self.id_callback = None

    def connect(self):
        log(0, "\n\n\n________________________________\n|Pick One|:\n"
            "    1/Draw a rectangle around your star with left button\n"
            "    2/Click on star 'center' with right button")
        self.rectangle_selector = matplotlib.widgets.RectangleSelector(
            self.ax,
            RectangleClick, drawtype='box',
            rectprops=dict(facecolor='green', edgecolor='black',
                           alpha=0.5, fill=True),
            button=[1],  # 1/left, 2/center , 3/right
        )
        self.id_callback = self.canvas.mpl_connect(
            'button_press_event', self.work)

    def disconnect(self):
        log(3, 'PickOne disconnect')
        if self.rectangle_selector:
            self.rectangle_selector.set_active(False)
            self.rectangle_selector = None
        if self.id_callback:
            self.canvas.mpl_disconnect(self.id_callback)
            self.id_callback = None

    def work(self, obj):
        """obj is a matplotlib event"""
        PickEvent(obj)


class NoPick(Pick):
    """Void class to do nothing"""
    def connect(self): pass
    def disconnect(self): pass
    def work(self, obj): pass



class PickEllipse(Pick):
    """Not used"""
    def __init__(self):
        super().__init__()
        self.artist_ellipse = None

    def connect(self):
        self.artist_ellipse = artist.Ellipse(
            self.figure,
            self.ax,
            array=get_root().image.im0,
            callback=self.work
        )

    def disconnect(self):
        if self.artist_ellipse:
            self.artist_ellipse.Disconnect()
            self.artist_ellipse.RemoveArtist()
            self.artist_ellipse = None

    def work(self, _):
        MultiprocessCaller()


class PickAnnulus(Pick):
    """Not used"""
    def __init__(self):
        super().__init__()
        self.artist_annulus = None

    def connect(self):
        self.artist_annulus = artist.Annulus(
            self.figure,
            self.ax,
            array=get_root().image.im0,
            callback=self.work
        )

    def disconnect(self):
        if self.artist_annulus:
            self.artist_annulus.Disconnect()
            self.artist_annulus.RemoveArtist()
            self.artist_annulus = None

    def work(self, obj):
        IF.AnnulusEventPhot(obj)


class PickProfile(Pick):
    """Linear Profile, cutted shape of a source
    Draw a line on the image. Some basic statistics on the pixels cutted by
    your line will be displayed in the 'star frame'. And a Curve will be
    displayed on the 'fit frame'. A pixel is included if the distance of its
    center is 0.5 pixel away from the line. This is made to prevent to many
    pixels stacking at the same place of the line\n\n." Programmers, an
    'improvement' can be made including pixels more distant and making a mean
    of the stacked pixels for each position on the line."
    """
    def __init__(self):
        super().__init__()
        self.artist_profile = None

    def connect(self):
        self.artist_profile = artist.Profile(
            get_root().frame_image.get_figure(),
            get_root().frame_image.get_figure().axes[0],
            callback=AR.ProfileEvent
        )
    def disconnect(self):
        if self.artist_profile:
            self.artist_profile.Disconnect()
            self.artist_profile.RemoveArtist()
            self.artist_profile = None

    def work(self, obj):
        IF.AnnulusEventPhot(obj)


class PickStat(Pick):
    """Draw a rectangle"""
    def __init__(self):
        super().__init__()
        self.rectangle_selector = None

    def disconnect(self):
        if self.rectangle_selector:
            self.rectangle_selector.set_active(False)
            self.rectangle_selector = None

    def connect(self):
        log(0, "\n\n\n________________________________\n"
            "|Pick Stat| : draw a rectangle around a region and ABISM "
            "will give you some statistical information "
            "computed in the region-------------------")
        self.rectangle_selector = matplotlib.widgets.RectangleSelector(
            self.ax,
            RectangleClick, drawtype='box',
            rectprops=dict(facecolor='red', edgecolor='black', alpha=0.5, fill=True))

    def work(self, obj):
        IF.AnnulusEventPhot(obj)


class PickBinary(Pick):
    """Binary System
    If Binary button is green, make two click on a binary system : one on each
    star. A Binary fit will be processed. This is still in implementation.
    """
    def __init__(self):
        super().__init__()
        self.id_callback = None
        self.star1 = self.star2 = None

    def connect(self):
        log(0, "\n\n\n______________________________________\n"
            "|Binary| : Make 2 clicks, one per star-------------------")
        self.id_callback = get_root().frame_image.get_canvas().mpl_connect(
            'button_press_event', self.connect_second)
        self.canvas.get_tk_widget()["cursor"] = "target"


    def disconnect(self):
        try:
            self.canvas.mpl_disconnect(self.id_callback)
        except:
            pass
        self.canvas.get_tk_widget()["cursor"] = ""


    def connect_second(self, event):
        """Second callback"""
        # Check in: click in image
        if not event.inaxes: return
        log(0, "1st point : ", event.xdata, event.ydata)

        # Save first click
        self.star1 = [event.ydata, event.xdata]

        # Disconnect first click
        self.canvas.mpl_disconnect(self.id_callback)

        # Connect second click
        self.id_callback = self.canvas.mpl_connect(
            'button_press_event', self.connect_third)


    def connect_third(self, event):
        """After second click (final), do real work"""
        if not event.inaxes: return
        log(0, "2nd point : ", event.xdata, event.ydata)

        # Save second click
        self.star2 = [event.ydata, event.xdata]

        # Disconnect second click & Restore cursor
        self.canvas.mpl_disconnect(self.id_callback)
        self.canvas.get_tk_widget()["cursor"] = ""

        # Work
        self.work(None)

        # Prepare next
        self.star1 = self.star2 = None
        self.connect()


    def work(self, obj):
        Strehl.BinaryStrehl(self.star1, self.star2)
        AR.show_answer()
        AR.PlotStar2()
        AR.PlotStar()



def PickEvent(event):
    """For  mouse click PickOne"""
    # Left click -> avoid shadowing rectangle selection
    if not event.inaxes or event.button == 1:
        return

    # Right click -> center
    if event.button == 3:
        log(5, 'Centering <- right click:', event)
        center_handler(
            event,
            get_root().frame_image.get_figure().axes[0],
            callback=get_root().frame_image.get_canvas().draw)
        return

    if get_root().frame_image.is_toolbar_active():
        log(0, 'WARNING: Zoom or Pan actif, '
            'please unselect its before picking your object')
        return

    # Save bounds <- click +/- 15
    W.r = [event.ydata - 15, event.ydata + 15,
           event.xdata - 15, event.xdata + 15]

    MultiprocessCaller()


def TightBinary(disconnect=False):
    # DISCONNECT
    if disconnect and get_state().pick_old == 'tightbinary':
        try:
            get_root().frame_image.get_canvas().mpl_disconnect(G.pt1)
        except:
            pass
        try:
            get_root().frame_image.get_canvas().mpl_disconnect(G.pt2)
        except:
            pass
        get_root().frame_image.get_canvas().get_tk_widget()["cursor"] = ""
        return

    # CONNECT
    if get_state().pick_type == "tightbinary":
        log(0, "\n\n\n______________________________________\n"
            "|TightBinary| : Make 2 clicks, one per star, be precise, "
            "the parameters will be more constrained-------------------")
        G.pt1 = get_root().frame_image.get_canvas().mpl_connect('button_press_event', TightBinary2)
        get_root().frame_image.get_canvas().get_tk_widget()["cursor"] = "target"

        get_state().aniso = False
        get_state().same_psf_var = True
        # TODO Check if I broke something
        # SetFitType(get_state().fit_type)
    return


def TightBinary2(event):
    if not event.inaxes:
        return
    log(0, "1st point : ", event.xdata, event.ydata)
    G.star1 = [event.ydata, event.xdata]
    # we need to inverse, always the same issue ..
    get_root().frame_image.get_canvas().mpl_disconnect(G.pt1)
    G.pt2 = get_root().frame_image.get_canvas().mpl_connect('button_press_event', TightBinary3)
    return


def TightBinary3(event):  # Here we call the math
    if not event.inaxes:
        return
    log(0, "2nd point : ", event.xdata, event.ydata)
    G.star2 = [event.ydata, event.xdata]
    get_root().frame_image.get_canvas().mpl_disconnect(G.pt2)

    get_root().frame_image.get_canvas().get_tk_widget()["cursor"] = ""
    MultiprocessCaller()
    TightBinary()



# TODO move me in base class
def RectangleClick(eclick, erelease):
    """return the extreme coord of the human drawn rectangle  And call StrehlMeter"""
    log(3, 'rectangle click_________________')
    get_root().image.click = eclick.xdata, eclick.ydata
    get_root().image.release = erelease.xdata, erelease.ydata
    if get_root().image.click == get_root().image.release:
        log(0, "Rectangle phot aborded: you clicked and released ont the same point")
        return
    log(3, get_root().image.click, get_root().image.release)
    W.r = (int(get_root().image.click[1]), int(get_root().image.release[1]),
           int(get_root().image.click[0]), int(get_root().image.release[0]))

    MultiprocessCaller()
    return


#############################
## MULTIPROCESSING TOOLS    #
#############################


def MultiprocessCaller():
    if get_state().pick_type == "tightbinary":
        log(3, "I call binary math")
        Strehl.TightBinaryStrehl()
        AR.show_answer()
        AR.PlotStar2()
        AR.PlotStar()
        return
    if get_state().pick_type == "stat":
        AR.PlotStat()
        return
    if get_state().pick_type == "ellipse":
        Strehl.EllipseEventStrehl()
        AR.show_answer()
        return

    if get_state().pick_type == "one":
        Strehl.StrehlMeter()
        AR.show_answer()
        # we transport star center, because if it is bad, it is good to know,
        # this star center was det by iterative grav center  the fit image
        # is a W.psf_fit[0][3]
        AR.PlotStar()
        return

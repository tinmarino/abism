"""
    Pick star and call back
"""
import matplotlib
import numpy as np
from abc import ABC, abstractmethod

from abism.front import artist
from abism.front.matplotlib_extension import center_handler
from abism.front import AnswerReturn as AR

from abism.back import Strehl
import abism.back.util_back as W

from abism.util import log, get_root, get_state

# TODO remove
from abism.back import ImageFunction as IF
from abism.front import util_front as G


pick = None

# TODO rewrite totally at end of refactoring
def RefreshPick(label):
    global pick
    """The exported routine"""
    """In function of the name of G.connect_var, we call the good one.
    Disconnect old pick event and connect the new one """
    lst = np.array([
        ["PickOne", "one", PickOne],
        ["Binary Fit", "binary", Binary],
        ["Tight Binary", "tightbinary", TightBinary],
        ["Profile", "profile", Profile],
        ["Stat", "stat", StatPick],
        ["Annulus", "annulus", PickAnnulus],
        ["Ellipse", "ellipse", PickEllipse],
        ["No Pick", "nopick", NoPick],
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

    pretty = [0]

    # Dicconnect old
    index_old = list(lst[:, 1]).index(
        get_state().pick_old)   # or G.connect_var.get()
    if index_old in pretty:
        lst[index_old, 2]().disconnect()
    else:
        # This staff with disconnect is to avoid twice a call,
        # in case pick_old = pick  it is not necessary but more pretty
        # WTF !!!, hacky way to call a dict ,-)
        lst[index_old, 2](disconnect=True)

    # Connect new
    if index in pretty:
        # Do not grabage me
        pick = lst[index, 2]()
        pick.connect()
    else:
        lst[index, 2]()


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
            'button_press_event', PickEvent)

    def disconnect(self):
        log(3, 'PickOne disconnect')
        if self.rectangle_selector:
            self.rectangle_selector.set_active(False)
        if self.id_callback:
            self.canvas.mpl_disconnect(self.id_callback)




def NoPick(disconnect=False):
    # pylint: disable=unused-argument
    return


def PickEllipse(disconnect=False):
    # DISCONNECT
    if disconnect and get_state().pick_old == 'ellipse':
        try:
            G.ellipse.Disconnect()
            G.ellipse.RemoveArtist()
            del G.ellipse
        except:
            pass
        return
    # CONNECT
    if get_state().pick_type == "ellipse":
        G.ellipse = artist.Ellipse(
            get_root().frame_image.get_figure(),
            get_root().frame_image.get_figure().axes[0],
            array=get_root().image.im0,
            callback=MultiprocessCaller

        )


def PickAnnulus(disconnect=False):
    # DISCONNECT
    if disconnect and get_state().pick_old == 'annulus':
        try:
            G.annulus.Disconnect()
            G.annulus.RemoveArtist()
            del G.annulus
        except:
            pass
        return
    # CONNECT
    if get_state().pick_type == "annulus":
        G.annulus = artist.Annulus(
            get_root().frame_image.get_figure(),
            get_root().frame_image.get_figure().axes[0],
            array=get_root().image.im0,
            callback=IF.AnnulusEventPhot
        )


def Profile(disconnect=False):
    """Linear Profile, cutted shape of a source
    Draw a line on the image. Some basic statistics on the pixels cutted by
    your line will be displayed in the 'star frame'. And a Curve will be
    displayed on the 'fit frame'. A pixel is included if the distance of its
    center is 0.5 pixel away from the line. This is made to prevent to many
    pixels stacking at the same place of the line\n\n." Programmers, an
    'improvement' can be made including pixels more distant and making a mean
    of the stacked pixels for each position on the line."
    """
    # DISCONNECT
    if disconnect and get_state().pick_old == 'profile':
        try:
            G.my_profile.Disconnect()
        except:
            log(3, "Pick.Profile , cannot disconnect profile ")
        try:
            G.my_profile.RemoveArtist()
            # del G.my_profile # maybe not
        except:
            log(3, "Pick.Profile , cannot remove artist profile ")
        return
        # if get_state().pick_type == "profile" : return # in order not to cal twice at the begining
    # CONNECT
    if get_state().pick_type == "profile":
        G.my_profile = artist.Profile(
            get_root().frame_image.get_figure(),
            get_root().frame_image.get_figure().axes[0],
            callback=AR.ProfileEvent
        )


def PickEvent(event):
    """For  mouse click"""
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


def Binary(disconnect=False):
    """Binary System
    If Binary button is green, make two click on a binary system : one on each
    star. A Binary fit will be processed. This is still in implementation.
    """

    # DISCONNECT
    if disconnect and get_state().pick_old == 'binary':
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
    if get_state().pick_type == "binary":
        log(0, "\n\n\n______________________________________\n"
            "|Binary| : Make 2 clicks, one per star-------------------")
        G.pt1 = get_root().frame_image.get_canvas().mpl_connect('button_press_event', Binary2)
        get_root().frame_image.get_canvas().get_tk_widget()["cursor"] = "target"
        return
    return


def Binary2(event):
    # Check in: click in image
    if not event.inaxes: return
    log(0, "1st point : ", event.xdata, event.ydata)

    # Save first click
    get_state().star1 = [event.ydata, event.xdata]

    # Disconnect first click
    get_root().frame_image.get_canvas().mpl_disconnect(G.pt1)

    # Connect second click
    G.pt2 = get_root().frame_image.get_canvas().mpl_connect(
        'button_press_event', Binary3)


def Binary3(event):
    """Final click: here the math will be called"""
    if not event.inaxes: return
    log(0, "2nd point : ", event.xdata, event.ydata)

    # Save second click
    get_state().star2 = [event.ydata, event.xdata]

    # Disconnect second click & Restore cursor
    get_root().frame_image.get_canvas().mpl_disconnect(G.pt2)
    get_root().frame_image.get_canvas().get_tk_widget()["cursor"] = ""

    MultiprocessCaller()
    Binary()


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
    G.pt2 = get_root().frame_image.get_canvas().mpl_connect('button_press_event', Binary3)
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


def StatPick(disconnect=False):
    """Draw a rectangle
    """
    # DISCONNECT
    if disconnect and get_state().pick_old == 'stat':
        try:
            G.rs_stat.set_active(False)  # rs rectangle selector
        except:
            pass
        return

    # CONNECT
    if get_state().pick_type == "stat":
        log(0, "\n\n\n________________________________\n"
            "|Pick Stat| : draw a rectangle around a region and ABISM "
            "will give you some statistical informationcomputed in the region-------------------")
        get_state().pick_type = 'stat'
        G.rs_stat = matplotlib.widgets.RectangleSelector(
            get_root().frame_image.get_figure().axes[0], RectangleClick, drawtype='box',
            rectprops=dict(facecolor='red', edgecolor='black', alpha=0.5, fill=True))


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
    """ This is made in order to call and stop it if we spend to much time
    now I putted 10 sec but a G.time_spent should be implemented. todo"""
    PickWorker()


#from timeout import timeout
# @timeout(15)
def PickWorker():
    import time
    start = time.time()
    if get_state().pick_type == "binary":
        log(3, "I call binary math")
        Strehl.BinaryStrehl()
        AR.show_answer()
        AR.PlotStar2()
        AR.PlotStar()
        return
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
        # we transport star center, because if it is bad, it is good to know, this star center was det by iterative grav center  the fit image is a W.psf_fit[0][3]
        AR.PlotStar()
        return

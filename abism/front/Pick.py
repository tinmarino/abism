"""
    Pick star and call back
"""
import matplotlib
import numpy as np  # for a readind lst like an array

from abism.front import EventArtist  # draw an ellipse
from abism.front import AnswerReturn as AR
# Warnign circular dep
import abism.front.Menu.AnalysisMenu as AnalysisMenu
from abism.front.matplotlib_extension import center_handler
from abism.front import util_front as G

from abism.back import Strehl
from abism.back import ImageFunction as IF
import abism.back.util_back as W

from abism.util import log, get_root


def RefreshPick(label):  # This is the only callled routine
    # if label != "" : G.connect_menu["text"] = u'\u25be ' +   label # remove the little arrow
    """in function of the name of G.connect_var, we call the good one. Disconnect old pick event and connect the new one """
    lst = np.array([
        ["PickOne", "one", "PickOne"],
        ["PickMany", "many", "PickMany"],
        ["Binary Fit", "binary", "Binary"],
        ["Tight Binary", "tightbinary", "TightBinary"],
        ["Profile", "profile", "Profile"],
        ["Stat", "stat", "StatPick"],
        ["Annulus", "annulus", "PickAnnulus"],
        ["Ellipse", "ellipse", "PickEllipse"],
        ["No Pick", "nopick", "NoPick"],
    ])  # Label@Menu , W.type["pick"], fct to call

    try:
        W.type["pick_old"] = W.type["pick"]
    except:
        pass
    index = list(lst[:, 1]).index(label)   # or G.connect_var.get()
    W.type["pick"] = label
    # because they are in tools, and it disable the connection, I don't know why
    if label != "stat" or label != "profile":
        G.cu_pick.set(label)

      # THE dicconnect
    if 'pick_old' in W.type:
        if type(W.type["pick_old"]) is list:  # for pick many
            index_old = list(lst[:, 1]).index(
                W.type["pick_old"][0])   # or G.connect_var.get()
        else:
            index_old = list(lst[:, 1]).index(
                W.type["pick_old"])   # or G.connect_var.get()
        # This staff with disconnect is to avoid twice a call, in case pick_old = pick  it is not necessary but more pretty
        globals()[lst[index_old, 2]](disconnect=True)

      # THE CALLL
    globals()[lst[index, 2]]()


def NoPick(disconnect=False):  # to check if all pick types are disconnect
    return


def PickEllipse(disconnect=False):
    # DISCONNECT
    if disconnect and W.type.get('pick_old', '') == 'ellipse':
        try:
            G.ellipse.Disconnect()
            G.ellipse.RemoveArtist()
            del G.ellipse
        except:
            pass
        return
    # CONNECT
    if W.type["pick"] == "ellipse":
        G.ellipse = EventArtist.Ellipse(G.fig, G.ax1, array=get_root().image.im0)


def PickAnnulus(disconnect=False):
    # DISCONNECT
    if disconnect and W.type.get('pick_old', '') == 'annulus':
        try:
            G.annulus.Disconnect()
            G.annulus.RemoveArtist()
            del G.annulus
        except:
            pass
        return
    # CONNECT
    if W.type["pick"] == "annulus":
        G.annulus = EventArtist.Annulus(G.fig, G.ax1, array=get_root().image.im0)


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
    if disconnect and W.type.get('pick_old', '') == 'profile':
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
        # if W.type["pick"] == "profile" : return # in order not to cal twice at the begining
    # CONNECT
    if W.type["pick"] == "profile":
        G.my_profile = EventArtist.Profile(G.fig, G.ax1)


def PickOne(disconnect=False):
    """Pick One Star
    This button should be green and the zoom button of th eimage toolbar
    unpressed. If it is pressed, clik again on it. You then hav eto draw a
    rectangle aroung the star to mesure the strehl ratio around this star.  A
    first fit will be computed in the rectangle you 've just drawn. Then the
    photometry of the star will be computed according to the photometry and
    background measurement type you chose in 'MoreOption' in the file menu. By
    default, the photometry is processed in a 99% flux rectangle.  And the
    backgorund, in 8 littel rectangels around the star.
    The fit is necessary to get the maximum, the peak of the psf that will be
    compared to the diffraction pattern. You can set to assess the photometry
    of the object with the fit.  A Moffat fit type is chosen by default. but
    you can change it with the button FitType. I recommend you to use a
    Gaussian for Strehl <5%, A Moffat for intermediate Strehl and a Bessel for
    strehl>60%."
    """

    # DISCONNECT
    if disconnect and W.type.get('pick_old', '') == 'one':
        if "rs_one" in vars(G):
            G.rs_one.set_active(False)
        if "cid_left" in vars(G):
            G.fig.canvas.mpl_disconnect(G.cid_left)
        return

    # CONNECT
    if W.type["pick"] == "one":
        log(0, " \n\n\n________________________________\n|Pick One|:\n"
            "    1/Draw a rectangle around your star with left button\n"
            "    2/Click on star 'center' with right button")
        G.rs_one = matplotlib.widgets.RectangleSelector(
            G.ax1, RectangleClick, drawtype='box',
            rectprops=dict(facecolor='green', edgecolor='black',
                           alpha=0.5, fill=True),
            button=[1],  # 1/left, 2/center , 3/right
        )
        G.cid_left = G.fig.canvas.mpl_connect('button_press_event', PickEvent)


def PickEvent(event):
    """For  mouse click"""
    # Left click -> avoid shadowing rectangle selection
    if not event.inaxes or event.button == 1:
        return

    # Right click -> center
    if event.button == 3:
        log(5, 'Centering <- right click:' , event)
        center_handler(
            event,
            G.fig.axes[0],
            callback=get_root().ImageFrame.get_canvas().draw)
        return

    if G.toolbar._active == 'PAN' or G.toolbar._active == 'ZOOM':
        log(0 ,
                'WARNING: Zoom or Pan actif, please unselect its before picking your object')
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
    if disconnect and W.type.get('pick_old', '') == 'binary':
        try:
            G.fig.canvas.mpl_disconnect(G.pt1)
        except:
            pass
        try:
            G.fig.canvas.mpl_disconnect(G.pt2)
        except:
            pass
        G.ImageCanvas.get_tk_widget()["cursor"] = ""
        return

    # CONNECT
    if W.type["pick"] == "binary":
        log(0, "\n\n\n______________________________________\n"
            "|Binary| : Make 2 clicks, one per star-------------------")
        G.pt1 = G.fig.canvas.mpl_connect('button_press_event', Binary2)
        G.ImageCanvas.get_tk_widget()["cursor"] = "target"
        return
    return


def Binary2(event):
    if not event.inaxes:
        return
    log(0, "1st point : ", event.xdata, event.ydata)
    G.star1 = [event.ydata, event.xdata]
    # we need to inverse, always the same issue ..
    G.fig.canvas.mpl_disconnect(G.pt1)
    G.pt2 = G.fig.canvas.mpl_connect('button_press_event', Binary3)
    return


def Binary3(event):  # Here we call the math
    if not event.inaxes:
        return
    log(0, "2nd point : ", event.xdata, event.ydata)
    G.star2 = [event.ydata, event.xdata]
    G.fig.canvas.mpl_disconnect(G.pt2)

    G.ImageCanvas.get_tk_widget()["cursor"] = ""
    MultiprocessCaller()
    Binary()


def TightBinary(disconnect=False):
    # DISCONNECT
    if disconnect and W.type.get('pick_old', '') == 'tightbinary':
        try:
            G.fig.canvas.mpl_disconnect(G.pt1)
        except:
            pass
        try:
            G.fig.canvas.mpl_disconnect(G.pt2)
        except:
            pass
        G.ImageCanvas.get_tk_widget()["cursor"] = ""
        return

    # CONNECT
    if W.type["pick"] == "tightbinary":
        log(0, "\n\n\n______________________________________\n"
            "|TightBinary| : Make 2 clicks, one per star, be precise, "
            "the parameters will be more constrained-------------------")
        G.pt1 = G.fig.canvas.mpl_connect('button_press_event', TightBinary2)
        G.ImageCanvas.get_tk_widget()["cursor"] = "target"
        #  CLick on same psf and no aniso
        W.aniso_var.set(False)
        W.same_psf_var.set(True)
        AnalysisMenu.SetFitType(W.type["fit"])
    return


def TightBinary2(event):
    if not event.inaxes:
        return
    log(0, "1st point : ", event.xdata, event.ydata)
    G.star1 = [event.ydata, event.xdata]
    # we need to inverse, always the same issue ..
    G.fig.canvas.mpl_disconnect(G.pt1)
    G.pt2 = G.fig.canvas.mpl_connect('button_press_event', Binary3)
    return


def TightBinary3(event):  # Here we call the math
    if not event.inaxes:
        return
    log(0, "2nd point : ", event.xdata, event.ydata)
    G.star2 = [event.ydata, event.xdata]
    G.fig.canvas.mpl_disconnect(G.pt2)

    G.ImageCanvas.get_tk_widget()["cursor"] = ""
    MultiprocessCaller()
    TightBinary()


def PickMany(disconnect=False):
    """Pick Many Stars
    As for PickOne, you have to draw a rectangle around a star. But this time
    the output is shorten. After the Strehl measurment of the star you picked,
    you can pick an other star
    """
    # DISCONNECT
    if disconnect and W.type.get('pick_old', '') == 'many':
        try:
            G.rs_many.set_active(False)
        except:
            pass  # in case rs_many is not called yet
        return

    # CONNECT
    if W.type["pick"] == "many":
        G.arrows, G.answer_saved = [], {}
        log(0, "\n\n\n______________________________\n"
            "|Pick Many| : draw rectangles around your stars-----------------------")
        # G.pick count the index of the picked star
        W.type["pick"] = ['many', 1]
        log(9, 'pick,G.pick', W.type["pick"])
        G.rs_many = matplotlib.widgets.RectangleSelector(
            G.ax1, RectangleClick, drawtype='box',
            rectprops=dict(facecolor='blue', edgecolor='black', alpha=0.5, fill=True))
        return


def StatPick(disconnect=False):
    """Draw a rectangle
    The Stats are defined in Arrayfunction/Stat.py
    """
    # DISCONNECT
    if disconnect and W.type.get('pick_old', '') == 'stat':
        try:
            G.rs_stat.set_active(False)  # rs rectangle selector
        except:
            pass
        return

    # CONNECT
    if W.type["pick"] == "stat":
        log(0, "\n\n\n________________________________\n"
            "|Pick Stat| : draw a rectangle around a region and ABISM "
            "will give you some statistical informationcomputed in the region-------------------")
        W.type["pick"] = 'stat'
        G.rs_stat = matplotlib.widgets.RectangleSelector(
            G.ax1, RectangleClick, drawtype='box',
            rectprops=dict(facecolor='red', edgecolor='black', alpha=0.5, fill=True))


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


def ManualRectangle(eclick, erelease):
    image_click = eclick.xdata, eclick.ydata
    image_release = erelease.xdata, erelease.ydata
    # we inverse to get x,y like row,column
    r = image_click[1], image_release[1], image_click[0], image_release[0]
    r = IF.Order4(r)
    if G.rect_phot_bool:
        log(0, IF.RectanglePhot(get_root().image.im0, r))
    log(9, '----> WindowRoot.py, ManualRectangle', r)
    if G.bu_noise_manual['background'] == 'green':
        G.r = r
    elif G.bu_noise_manual['background'] == 'blue':
        G.remember_r.append(r)
    G.rect_phot_bool = 0
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
    if W.type["pick"] == "binary":
        log(3, "I call binary math")
        Strehl.BinaryStrehl()
        AR.PlotAnswer()
        AR.PlotStar2()
        AR.PlotStar()
    if W.type["pick"] == "tightbinary":
        log(3, "I call binary math")
        Strehl.TightBinaryStrehl()
        AR.PlotAnswer()
        AR.PlotStar2()
        AR.PlotStar()
    elif W.type["pick"] == "stat":
        AR.PlotStat()
    elif W.type["pick"] == "ellipse":
        Strehl.EllipseEventStrehl()
        AR.PlotAnswer()

    elif W.type["pick"] == "one" or W.type["pick"] == "many":  # including "one" or "many"
        Strehl.StrehlMeter()
        AR.PlotAnswer()
        # we transport star center, because if it is bad, it is good to know, this star center was det by iterative grav center  the fit image is a W.psf_fit[0][3]
        AR.PlotStar()

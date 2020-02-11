"""
    Pick star and call back
    Used by menu_bar.py
"""
from abc import ABC, abstractmethod

import matplotlib

from abism.front import artist
from abism.front import AnswerReturn as AR

from abism.back import Strehl

from abism.plugin.stat_rectangle import show_statistic
from abism.plugin.profile_line import show_profile

from abism.util import log, get_root, get_state, AsyncWorker


class Pick(ABC):
    """Class for a connection:
    image event -> operation (then result display)
    Note: disconnection is not generic:
        sometime a matplotlit callback_id
        sometime a cutom artist
    """
    def __init__(self):
        log(3, 'Pick: creating a', self.__class__.__name__, 'instance')
        self.canvas = get_root().frame_image.get_canvas()
        self.figure = get_root().frame_image.get_figure()
        self.ax = self.figure.axes[0]
        self.rectangle = None
        # Boolean: is work over
        self.done = False  # Value('done', False)

    @abstractmethod
    def connect(self):
        """Canvas may have changed"""
        log(3, 'Pick: connecting a', self.__class__.__name__, 'instance')
        self.canvas = get_root().frame_image.get_canvas()
        self.figure = get_root().frame_image.get_figure()
        self.ax = self.figure.axes[0]

    @abstractmethod
    def disconnect(self): pass

    @abstractmethod
    def work(self, obj):
        """Work in the backend (can ba async)
        :param obj: <- event (usually)
        """

    @abstractmethod
    def on_done(self):
        """Return result to frontend (in tk main loop)"""

    def launch_worker(self, obj):
        """Launch worker async"""
        get_state().reset_answers()
        AsyncWorker(lambda: self.work(obj), self.on_done, timeout=0.5).run()

    def on_rectangle(self, eclick, erelease):
        """Param: the extreme coord of the human drawn rectangle"""
        # Log && Save
        click = eclick.xdata, eclick.ydata
        release = erelease.xdata, erelease.ydata
        get_state().l_click = [click, release]

        # Log
        log(3, "Rectangle click_________________\n"
            'between:', click, 'and', release)

        # If null rectangle -> make middle click
        if (click[0] - release[0]) * (click[1] - release[1]) < 9:
            log(3, 'Rectangle incomplete, crafting a fake middle click here')
            x, y = click
            event = matplotlib.backend_bases.MouseEvent(
                'button_press_event', get_root().frame_image.get_canvas(),
                x, y, button=2)
            event.xdata, event.ydata = x, y
            event.inaxes = True
            self.pick_event(event)
            return

        self.rectangle = (
            int(click[1]), int(release[1]),
            int(click[0]), int(release[0])
        )

        # Work
        self.launch_worker(None)


    def pick_event(self, event):
        """For mouse click PickOne or rectangle"""
        # Left click -> avoid shadowing rectangle selection
        if not event.inaxes or event.button == 1:
            return

        if get_root().frame_image.is_toolbar_active():
            log(0, 'WARNING: Zoom or Pan actif, '
                'please unselect its before picking your object')
            return

        if event.button == 2:
            # Reamining button 2 -> Save bounds <- click +/- 15
            log(1, 'Making a selection 30 pixels around', event)
            self.rectangle = (
                event.ydata - 20, event.ydata + 20,
                event.xdata - 20, event.xdata + 20)

            self.launch_worker(None)


class PickNo(Pick):
    """Void class to do nothing"""
    def connect(self): pass
    def disconnect(self): pass
    def work(self, obj): pass
    def on_done(self): pass


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
        self.done = False

    def connect(self):
        super().connect()
        log(0, "\n\n\n________________________________\n|Pick One|:\n"
            "    1/Draw a rectangle around your star with left button\n"
            "    2/Click on star 'center' with right button")
        self.rectangle_selector = matplotlib.widgets.RectangleSelector(
            self.ax,
            self.on_rectangle, drawtype='box',
            rectprops=dict(facecolor='green', edgecolor='black',
                           alpha=0.5, fill=True),
            button=[1],  # 1/left, 2/center , 3/right
        )
        self.canvas.mpl_connect(
            'button_press_event', self.pick_event)

    def disconnect(self):
        log(3, 'PickOne disconnect')
        if self.rectangle_selector:
            self.rectangle_selector.set_active(False)
            self.rectangle_selector = None
        if self.id_callback:
            self.canvas.mpl_disconnect(self.id_callback)
            self.id_callback = None

    def work(self, obj):
        """obj is None"""
        Strehl.strehl_one(self.rectangle)

    def on_done(self):
        AR.show_answer()


class PickBinary(Pick):
    """Binary System
    If Binary button is green, make two click on a binary system : one on each
    star. A Binary fit will be processed. This is still in implementation.
    """
    def __init__(self):
        super().__init__()
        self.id_callback = None
        self.star1 = self.star2 = None
        self.is_parent = False

    def connect(self):
        super().connect()
        if not self.is_parent:
            log(0, "\n\n\n______________________________________\n"
                "|Binary| : Make 2 clicks, one per star-------------------")
        self.id_callback = self.canvas.mpl_connect(
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
        if not event.inaxes or not event.button == 1:
            return
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

        # Save to state
        get_state().l_click = [self.star1, self.star2]

        # Work
        self.launch_worker(None)

        # Prepare next
        self.star1 = self.star2 = None
        self.connect()


    def work(self, obj):
        Strehl.BinaryStrehl(self.star1, self.star2)

    def on_done(self):
        AR.show_answer()


class PickTightBinary(PickBinary):
    """Binary that are close so the fit is harder"""
    def __init__(self):
        super().__init__()
        self.is_parent = True

    def connect(self):
        log(0, "\n\n\n______________________________________\n"
            "|TightBinary| : Make 2 clicks, one per star, be precise, "
            "the parameters will be more constrained-------------------")
        super().connect()
        get_state().aniso = False
        get_state().same_psf_var = True


    def work(self, obj):
        Strehl.TightBinaryStrehl(self.star1, self.star2)


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
        super().connect()
        log(0, "\n\n\n________________________________\n"
            "|Pick Stat| : draw a rectangle around a region and ABISM "
            "will give you some statistical information "
            "computed in the region-------------------")
        self.rectangle_selector = matplotlib.widgets.RectangleSelector(
            self.ax,
            self.on_rectangle, drawtype='box',
            rectprops=dict(facecolor='red', edgecolor='black', alpha=0.5, fill=True))

    def work(self, obj): pass

    def on_done(self):
        show_statistic(self.rectangle)


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
        self.point1 = self.point2 = (0, 0)

    def connect(self):
        super().connect()
        self.artist_profile = artist.Profile(
            get_root().frame_image.get_figure(),
            get_root().frame_image.get_figure().axes[0],
            callback=self.launch_worker
        )

    def disconnect(self):
        if self.artist_profile:
            self.artist_profile.Disconnect()
            self.artist_profile.RemoveArtist()
            self.artist_profile = None

    def work(self, obj):
        self.point1 = [obj.point1[0], obj.point1[1]]
        self.point2 = [obj.point2[0], obj.point2[1]]

    def on_done(self):
        get_state().l_click = [self.point1, self.point2]
        show_profile(self.point1, self.point2)


class PickEllipse(Pick):
    """Not used"""
    def __init__(self):
        super().__init__()
        self.artist_ellipse = None

        self.bind_enter_id = None


    def connect(self):
        super().connect()
        log(0, "\n\n\n________________________________\n"
            "|Pick Ellipse| : draw an ellipse around isolated object\n"
            "ABISM will perform the photometry in this ellipse\n"
            "Bind: eXpand, rOtate, changeU, changeV (minor a major axes)\n"
            "      left, down, up, right or h, j, k, l\n"
            "      Upper case to increase, lower to decrease")

        self.artist_ellipse = artist.Ellipse(
            self.figure,
            self.ax,
            array=get_state().image.im0,
            callback=lambda: self.launch_worker(None)
        )

        # Bind mouse enter -> focus (for key)
        tk_fig = self.canvas.get_tk_widget()
        self.bind_enter_id = tk_fig.bind('<Enter>', lambda _: tk_fig.focus_set())


    def disconnect(self):
        # Undraw
        if self.artist_ellipse:
            self.artist_ellipse.Disconnect()
            self.artist_ellipse.RemoveArtist()
            self.artist_ellipse = None

        # Unbind
        if self.bind_enter_id:
            tk_fig = self.canvas.get_tk_widget()
            tk_fig.unbind('<Enter>', self.bind_enter_id)


    def work(self, _):
        Strehl.EllipseEventStrehl(self.artist_ellipse)

    def on_done(self):
        AR.show_answer()

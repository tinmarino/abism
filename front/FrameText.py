"""
    The Tkinter Frame For text / butto ninterface (left)

    Label
    Option
    Answer
"""

from tkinter import Frame, PanedWindow, Label, Button, StringVar, Entry, \
    PhotoImage, \
    VERTICAL, TOP, X, LEFT, RIGHT, BOTH, CENTER


from util import log
from front.util_front import photo_up, photo_down, quit_process
import front.util_front as G
import back.util_back as W


class TextFrame(Frame):
    """TextScrollable frame
    parent <- must be vertical pane
    children <- are grided
    """
    def __init__(self, parent, label_text='Frame'):
        super().__init__(parent, **G.fr_arg)

        # Prepare grid attributes
        self.columnconfigure(0, weight=1)

        # Add to parent paned
        parent.add(self, **G.sub_paned_arg)

        self._parent = parent  # for sash positioning
        self._arrow = None  # Button
        # TODO can I impoorve that trick ?
        self._last = None  # To get the normal size
        self._see_me = True  # Bool do you see me
        self._label_text = label_text

    def init_after(self):
        """Place a last widget"""
        # Place button to resize
        self._arrow = Button(
            self, command=self.toogle, image=photo_up(), **G.bu_arg)
        self._arrow.place(relx=1., rely=0., anchor="ne")

        # Place a label for the eye
        Label(self, text=self._label_text, **G.frame_title_arg).place(x=0, y=0)

        # Last widget
        self._last = Label(self, height=0, width=0)
        self._last.grid()

    def toogle(self, visible=None):
        """Toggle visibility: Hide and show"""
        self._see_me = visible if visible is not None else not self._see_me

        # Toogle sash
        if self._see_me:
            self._parent.sash_place(0, 0, 22)
            self._arrow.configure(image=photo_down())
        else:
            G.TextPaned.sash_place(0, 0, self._last.winfo_y())
            self._arrow.configure(image=photo_up())

    def clear(self):
        """Destroy all children, take care !"""
        log(3, 'Clearing ' + self._label_text)
        # Destroy children
        children = self.grid_slaves()
        for child in children:
            child.destroy()

        # Restore default
        self.init_after()


class LabelFrame(TextFrame):
    """Some conf"""
    def __init__(self, parent):
        super().__init__(parent, label_text='Info')

    def update(self):
        """Called later, display what I retrived from header
        warning: expand not working well
        ESO /  not ESO
        NAco/vlt
        Reduced/raw
        Nx x Ny x Nz
        WCS detected or not
        """
        import re

        # Declare list of label (text, properties)
        text_and_props = []

        # Get company
        company = 'ESO' if W.head.company == "ESO" else 'NOT ESO'

        # Get instrument
        if W.head.instrument == "NAOS+CONICA":
            instrument = "NaCo"
        else:
            instrument = W.head.instrument
        telescope = re.sub("-U.", "",
                           W.head.telescope.replace("ESO-", ""))
        text_and_props.append((company + " / " + telescope + " / " + instrument, {}))

        # Get is_reduced
        if "reduced_type" in vars(W.head):
            lbl = W.head.reduced_type + ': '
        else:
            lbl = ''

        # Get Size : Nx * Ny * Nz
        shape = list(W.Im0.shape[::-1])  # reverse, inverse, list order
        if "NAXIS3" in W.head.header.keys():
            shape.append(W.head.header["NAXIS3"])
            lbl += "%i x %i x %i" % (shape[0], shape[1], shape[2])
        else:
            lbl += "%i x %i " % (shape[0], shape[1])
        text_and_props.append((lbl, {}))

        # WCS
        if W.head.wcs is not None:
            lbl = "WCS detected"
        else:
            lbl = "WCS NOT detected"
        text_and_props.append((lbl, {}))

        # Header reads Strehl variables ?
        bolt = (W.head.diameter == 99. or W.head.wavelength == 99.)
        bolt = bolt or (W.head.obstruction == 99. or W.head.pixel_scale == 99.)
        if bolt:
            lbl = "WARNING: some parameters not found"
            text_and_props.append((lbl, {"fg": "red"}))
        else:
            lbl = "Parameters read from header"
            text_and_props.append((lbl, {"fg": "blue"}))

        # UNDERSAMPLED
        bol1 = W.head.wavelength * 1e-6
        bol1 /= W.head.diameter * (W.head.pixel_scale / 206265)
        bol1 = bol1 < 2
        bol2 = "sinf_pixel_scale" in vars(W.head)
        # if bol2 sinf_pixel_scane is not in W.head, we dont call the next line
        bol3 = bol2 and W.head.sinf_pixel_scale == 0.025
        bol3 = bol3 or (bol2 and (W.head.sinf_pixel_scale == 0.01))

        bolt = bol1 or bol2
        if bolt:
            lbl = "!!! SPATIALLY UNDERSAMPLED !!!"
            text_and_props.append((lbl, {"fg": "red"}))

        # Grid labels
        row = 0
        for i in text_and_props:
            arg = G.lb_arg.copy()
            arg.update({"justify": CENTER})
            if isinstance(i, (list, tuple)):
                arg.update(i[1])
            i = i[0]
            Label(self, text=i, **arg).grid(
                row=row, column=0, sticky="nsew")
            row += 1

        # Create what it takes
        self.init_after()

    def set_image_parameters(self, event, destroy=True):
        """Set imageparameter, labels"""
        # Parse
        for i in G.image_parameter_list:
            vars(W.head)[i[1]] = float(vars(G.tkentry)[i[1]].get())
            # COLOR
            if vars(W.head)[i[1]] == i[2]:
                vars(G.tkentry)[i[1]]["bg"] = "#ff9090"
            else:
                vars(G.tkentry)[i[1]]["bg"] = "#ffffff"

        # Show
        self.update()


class OptionFrame(TextFrame):
    """Some conf"""
    def __init__(self, parent):
        super().__init__(parent, label_text='Option')
        self.init_after()

    def ask_image_parameters(self):
        """Create Image Parameters Frame
        Warning do not confound with Label one
        To measure the Strehl ratio I really need :\n"
        -> Diameter of the telescope [in meters]\n"
        -> Obstruction of the telescope [ in % of the area obstructed ]\n"
        -> Wavelenght [ in micro meter ], the central wavelength of the band\n"
        -> Pixel_scale [ in arcsec per pixel ]\n"
        All the above parameters are used to get the diffraction pattern of the telescope
            because the peak of the PSF will be divided by the maximum of the diffraction
            patter WITH the same photometry to get the strehl.\n\n"
        Put the corresponding values in the entry widgets.
        Then, to save the values, press enter i, ONE of the entry widget
        or click on ImageParamter button again.\n"
        Note that these parameters should be readden from your image header.
        If it is not the case, you can send me an email or modify ReadHeader.py module."
        """
        # Label, variable , default value
        G.image_parameter_list = [
            ["Wavelength" + "*" + " [" + u'\u03BC' + "m]:", "wavelength", 99.],
            ["Pixel scale" + "*" + " [''/pix]: ", "pixel_scale", 99.],
            ["Diameter" + "*" + " [m]:", "diameter", 99.],
            ["Obstruction (d2/d1)*" + " [%]:", "obstruction", 99.],
            ["Zero point [mag]: ", "zpt", 0.],
            ["Exposure time [sec]: ", "exptime", 1.],
            ]

        ##########
        # INITIATE THE FRAME, change button color
        if G.bu_manual["background"] == G.bu_manual_color:
            # Grid new frame
            G.ManualFrame = Frame(self, bg=G.bg[0])
            G.ManualFrame.grid(sticky='nsew')

            # TITEL
            Label(G.ManualFrame, text="Parameters",
                  **G.frame_title_arg).pack(side=TOP, anchor="w")
            G.ManualGridFrame = Frame(G.ManualFrame)
            G.ManualGridFrame.pack(expand=0, fill=BOTH, side=TOP)
            G.ManualGridFrame.columnconfigure(0, weight=1)
            G.ManualGridFrame.columnconfigure(1, weight=1)

            ###################
            # THE ENTRIES (it is before the main dish )
            row = 0
            for i in G.image_parameter_list:
                l = Label(G.ManualGridFrame, text=i[0], font=G.font_param,
                          justify=LEFT, anchor="nw", **G.lb_arg)
                l.grid(row=row, column=0, sticky="NSEW")
                vars(G.tkvar)[i[1]] = StringVar()
                vars(G.tkentry)[i[1]] = Entry(G.ManualGridFrame, width=10, textvariable=vars(
                    G.tkvar)[i[1]], font=G.font_param, **G.en_arg)
                if vars(W.head)[i[1]] == i[2]:
                    vars(G.tkentry)[i[1]]["bg"] = "#ff9090"
                vars(G.tkentry)[i[1]].grid(row=row, column=1, sticky="NSEW")
                vars(G.tkentry)[i[1]].bind('<Return>', G.LabelFrame.set_image_parameters)
                if len(str(vars(W.head)[i[1]])) > 6:  # not to long for display
                    vars(G.tkvar)[i[1]].set("%.5f" % float(vars(W.head)[i[1]]))
                else:
                    vars(G.tkvar)[i[1]].set(vars(W.head)[i[1]])
                row += 1

            G.bu_manual["background"] = 'green'
            G.bu_manual["text"] = u'\u25b4 ' + 'ImageParameters'

            # EXPAND
            self.toogle(visible=True)

        elif G.bu_manual["background"] == 'green':  # destroy manualFrame  and save datas

            G.ManualFrame.destroy()
            del G.ManualFrame
            if G.in_arrow_frame == "param_title":
                G.arrtitle.destroy()
                G.in_arrow_frame = None
            # Remove MoreFrame
            G.all_frame = [x for x in G.all_frame if x != "G.ManualFrame"]
            G.bu_manual["background"] = G.bu_manual_color
            G.bu_manual["text"] = u'\u25be ' + 'ImageParameters'


class AnswerFrame(TextFrame):
    """Some conf"""
    def __init__(self, parent):
        super().__init__(parent, label_text='Result')

        self.init_after()

    def init_after(self):
        """Add fit type label"""
        self._fit_type_label = Label(self, text=W.type["fit"], justify=CENTER, **G.lb_arg)
        self._fit_type_label.grid(sticky='nsew')
        # Add also standard above
        super().init_after()

    def set_fit_type_text(self, s_text):
        """Change fit type label text"""
        self._fit_type_label.configure(text=s_text)



class ButtonFrame(Frame):
    """Frame 1 with quit, restart"""
    def __init__(self, parent):
        super().__init__(parent)

        # Create Quit
        G.bu_quit = Button(
            self, text='QUIT',
            background=G.bu_quit_color,
            command=quit_process, **G.bu_arg)

        # Create Restart
        G.bu_restart = Button(
            self, text='RESTART',
            background=G.bu_restart_color,
            command=G.Restart, **G.bu_arg)

        # Create Expand Image Parameter
        G.bu_manual = Button(
            self, text=u'\u25be ' + 'ImageParameters',
            background=G.bu_manual_color,
            command=G.OptionFrame.ask_image_parameters, **G.bu_arg)

        # Grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        G.bu_quit.grid(row=0, column=0, sticky="nsew")
        G.bu_restart.grid(row=0, column=1, sticky="nsew")
        G.bu_manual.grid(row=1, column=0, columnspan=2, sticky="nsew")


class LeftFrame(Frame):
    """Full Container"""
    def __init__(self, parent):
        # Append self -> parent
        super().__init__(parent, **G.fr_arg)
        parent.add(self)

        # Create Paned
        G.TextPaned = PanedWindow(self, orient=VERTICAL, **G.paned_dic)

        # Add LabelFrame
        G.LabelFrame = LabelFrame(G.TextPaned)

        # Add LabelFrame
        G.OptionFrame = OptionFrame(G.TextPaned)

        # Add AnswerFrame
        G.AnswerFrame = AnswerFrame(G.TextPaned)

        # Create Buttons with callback to preceding
        button_frame = ButtonFrame(self)

        # Pack buttons and pane
        button_frame.pack(side=TOP, expand=0, fill=X)
        G.TextPaned.pack(side=TOP, expand=1, fill=BOTH)

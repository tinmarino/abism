"""
    The Tkinter Frame For text / butto ninterface (left)

    Label
    Option
    Answer

"""
import re

from tkinter import Frame, PanedWindow, Label, Button, StringVar, Entry, \
    PhotoImage, \
    VERTICAL, TOP, X, LEFT, RIGHT, BOTH, CENTER

from abism.front.util_front import photo_up, photo_down, skin, \
    TitleLabel

from abism.util import log, get_root, quit_process, restart, get_state

import abism.front.util_front as G
import abism.back.util_back as W


class TextFrame(Frame):
    """TextScrollable frame
    parent <- must be vertical pane
    children <- are grided
    """
    def __init__(self, parent, label_text='Frame', index=0):
        super().__init__(parent, skin().frame_dic)

        # Prepare grid attributes
        self.columnconfigure(0, weight=1)

        # Add to parent paned
        parent.add(self, minsize=22, pady=0, sticky='nsew')

        self._parent = parent  # for sash positioning
        self._arrow = None  # Button
        # TODO can I impoorve that trick ?
        self._last = None  # To get the normal size
        self._see_me = True  # Bool do you see me
        self._label_text = label_text
        self._index = index  # for sash

    def init_after(self, add_title=True):
        """Place a last widget"""
        # Place button to resize
        self._arrow = Button(
            self, command=self.toogle, image=photo_up(), **skin().button_dic)
        self._arrow.place(relx=1., rely=0., anchor="ne")

        # Place a label for the eye
        if add_title:
            TitleLabel(self, text=self._label_text).place(x=0, y=0)

        # Last widget
        if self._last is not None:
            self._last.destroy()
        self._last = Label(self, height=0, width=0, **skin().frame_dic)
        self._last.grid()

    def toogle(self, visible=None):
        """Toggle visibility: Hide and show"""
        # Check: not work if last
        if self._index is None:
            log(3, 'Warning: cannot hide last sash')
            return

        if visible is not None:
            self._see_me = visible
        else:
            self._see_me = not self._see_me

        # Log before move
        log(3, 'Toggle sash: nb=', self._index,
            ',visible=', self._see_me,
            ',base_y=', self.winfo_y(),
            ',son=', self._last.winfo_y(),
            ',more=', self._last.winfo_y() - self._last.winfo_height()
            )

        # Toogle sash
        i_height = self.winfo_y() + 22
        if self._see_me:
            self._arrow.configure(image=photo_up())
            i_height += max(0, self._last.winfo_y() - self._last.winfo_height())
        else:
            self._arrow.configure(image=photo_down())
        self._parent.sash_place(self._index, 0, i_height)

        # Log after
        log(3, 'New sash pos: height=', i_height)

    def init_will_toogle(self, visible=True, add_title=True):
        """Place last and togfle later.
        Usually called to set visible when some widget added
        This trick is due to the fact widget will be updated at next tk loop
        """
        self.init_after(add_title=add_title)
        def will_refresh():
            self.update()
            self.toogle(visible=visible)
        self.after_idle(will_refresh)

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
    def __init__(self, parent, **args):
        super().__init__(parent, **args)

    def update_label(self):
        """Called later, display what I retrived from header
        warning: expand not working well
        ESO /  not ESO
        NAco/vlt
        Reduced/raw
        Nx x Ny x Nz
        WCS detected or not
        """

        # Image parameters
        if "ManualFrame" in vars(G):
            for i in G.image_parameter_list:
                vars(G.tkvar)[i[1]].set(vars(get_root().image.header)[i[1]])
            # to restore the values in the unclosed ImageParameters Frame
            self.set_image_parameters("", destroy=False)

        # Declare list of label (text, properties)
        text_and_props = []

        # Get company
        company = 'ESO' if get_root().header.company == "ESO" else 'NOT ESO'

        # Get instrument
        if get_root().header.instrument == "NAOS+CONICA":
            instrument = "NaCo"
        else:
            instrument = get_root().header.instrument
        telescope = re.sub("-U.", "",
                           get_root().header.telescope.replace("ESO-", ""))
        text_and_props.append((company + " / " + telescope + " / " + instrument, {}))

        # Get is_reduced
        if "reduced_type" in vars(get_root().header):
            lbl = get_root().header.reduced_type + ': '
        else:
            lbl = ''

        # Get Size : Nx * Ny * Nz
        shape = list(get_root().image.im0.shape[::-1])  # reverse, inverse, list order
        if "NAXIS3" in get_root().header.header.keys():
            shape.append(get_root().header.header["NAXIS3"])
            lbl += "%i x %i x %i" % (shape[0], shape[1], shape[2])
        else:
            lbl += "%i x %i " % (shape[0], shape[1])
        text_and_props.append((lbl, {}))

        # WCS
        if get_root().header.wcs is not None:
            lbl = "WCS detected"
        else:
            lbl = "WCS NOT detected"
        text_and_props.append((lbl, {}))

        # Header reads Strehl variables ?
        bolt = (get_root().header.diameter == 99. or get_root().header.wavelength == 99.)
        bolt = bolt or (get_root().header.obstruction == 99. or get_root().header.pixel_scale == 99.)
        if bolt:
            lbl = "WARNING: some parameters not found"
            text_and_props.append((lbl, {"fg": "red"}))
        else:
            lbl = "Parameters read from header"
            text_and_props.append((lbl, {"fg": "blue"}))

        # UNDERSAMPLED
        bol1 = get_root().header.wavelength * 1e-6
        bol1 /= get_root().header.diameter * (get_root().header.pixel_scale / 206265)
        bol1 = bol1 < 2
        bol2 = "sinf_pixel_scale" in vars(get_root().header)
        # if bol2 sinf_pixel_scane is not in get_root().header, we dont call the next line
        bol3 = bol2 and get_root().header.sinf_pixel_scale == 0.025
        bol3 = bol3 or (bol2 and (get_root().header.sinf_pixel_scale == 0.01))

        bolt = bol1 or bol2
        if bolt:
            lbl = "!!! SPATIALLY UNDERSAMPLED !!!"
            text_and_props.append((lbl, {"fg": "red"}))

        # Grid labels
        row = 0
        for i in text_and_props:
            arg = skin().fg_and_bg.copy()
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
            vars(get_root().header)[i[1]] = float(vars(G.tkentry)[i[1]].get())
            # COLOR
            if vars(get_root().header)[i[1]] == i[2]:
                vars(G.tkentry)[i[1]]["bg"] = "#ff9090"
            else:
                vars(G.tkentry)[i[1]]["bg"] = "#ffffff"

        # Show
        self.update_label()


class OptionFrame(TextFrame):
    """Some conf"""
    def __init__(self, parent, **args):
        super().__init__(parent, **args)
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
            ["Wavelength" + "*" + " [" + u'\u03BC' + "m]:", "wavelength", float('nan')],
            ["Pixel scale" + "*" + " [''/pix]: ", "pixel_scale", float('nan')],
            ["Diameter" + "*" + " [m]:", "diameter", float('nan')],
            ["Obstruction (d2/d1)*" + " [%]:", "obstruction", float('nan')],
            ["Zero point [mag]: ", "zpt", float('nan')],
            ["Exposure time [sec]: ", "exptime", float('nan')],
            ]

        ##########
        # INITIATE THE FRAME, change button color
        # TODO old trick to check for color, change it
        if G.bu_manual['background'] == skin().color.parameter1:
            # Grid new frame
            G.ManualFrame = Frame(self, **skin().frame_dic)
            G.ManualFrame.grid(sticky='nsew')

            # TITEL
            tl = TitleLabel(G.ManualFrame, text='Parameters')
            tl.pack(side=TOP, anchor="w")
            G.ManualGridFrame = Frame(G.ManualFrame)
            G.ManualGridFrame.pack(expand=0, fill=BOTH, side=TOP)
            G.ManualGridFrame.columnconfigure(0, weight=1)
            G.ManualGridFrame.columnconfigure(1, weight=1)

            ###################
            # THE ENTRIES (it is before the main dish )
            row = 0
            for i in G.image_parameter_list:
                l = Label(G.ManualGridFrame, text=i[0], font=skin().font.answer,
                          justify=LEFT, anchor="nw", **skin().fg_and_bg)
                l.grid(row=row, column=0, sticky="NSEW")
                vars(G.tkvar)[i[1]] = StringVar()
                vars(G.tkentry)[i[1]] = Entry(G.ManualGridFrame, width=10, textvariable=vars(
                    G.tkvar)[i[1]], font=skin().font.answer,
                    bd=0, **skin().fg_and_bg)
                if vars(get_root().header)[i[1]] == i[2]:
                    vars(G.tkentry)[i[1]]["bg"] = "#ff9090"
                vars(G.tkentry)[i[1]].grid(row=row, column=1, sticky="NSEW")
                vars(G.tkentry)[i[1]].bind('<Return>', get_root().LabelFrame.set_image_parameters)
                if len(str(vars(get_root().header)[i[1]])) > 6:  # not to long for display
                    vars(G.tkvar)[i[1]].set("%.5f" % float(vars(get_root().header)[i[1]]))
                else:
                    vars(G.tkvar)[i[1]].set(vars(get_root().header)[i[1]])
                row += 1

            # EXPAND
            G.bu_manual['background'] =  skin().color.parameter2
            G.bu_manual['text'] = u'\u25b4 ' + 'ImageParameters'

            self.init_will_toogle(visible=True, add_title=False)

        elif G.bu_manual['background'] == skin().color.parameter2:  # destroy manualFrame  and save datas

            G.ManualFrame.destroy()
            del G.ManualFrame
            if G.in_arrow_frame == "param_title":
                G.arrtitle.destroy()
                G.in_arrow_frame = None
            # Remove MoreFrame
            G.all_frame = [x for x in G.all_frame if x != "G.ManualFrame"]
            G.bu_manual["background"] =  skin().color.parameter1
            G.bu_manual["text"] = u'\u25be ' + 'ImageParameters'
            self.toogle(visible=False)


class AnswerFrame(TextFrame):
    """Some conf"""
    def __init__(self, parent, **args):
        super().__init__(parent, **args)

        self.init_after()

    def init_after(self):
        """Add fit type label"""
        self._fit_type_label = Label(self, text=get_state().fit_type, justify=CENTER, **skin().fg_and_bg)
        self._fit_type_label.grid(sticky='nsew')
        # Add also standard above
        super().init_after()

    def set_fit_type_text(self, s_text):
        """Change fit type label text"""
        self._fit_type_label.configure(text=s_text)


class ButtonFrame(Frame):
    """Frame 1 with quit, restart"""
    def __init__(self, parent, **args):
        super().__init__(parent, **args)

        # Define button option
        opts = skin().button_dic.copy()

        # Create Quit
        opts.update({'background':skin().color.quit})
        bu_quit = Button(
            self, text='QUIT',
            command=quit_process, **opts)

        # Create Restart
        opts.update({'background':skin().color.restart})
        bu_restart = Button(
            self, text='RESTART',
            command=restart, **opts)

        # Create Expand Image Parameter
        opts.update({'background':skin().color.parameter1})
        G.bu_manual = Button(
            self, text=u'\u25be ' + 'ImageParameters',
            command=get_root().OptionFrame.ask_image_parameters, **opts)

        # Grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        bu_quit.grid(row=0, column=0, sticky="nsew")
        bu_restart.grid(row=0, column=1, sticky="nsew")
        G.bu_manual.grid(row=1, column=0, columnspan=2, sticky="nsew")


class LeftFrame(Frame):
    """Full Container"""
    def __init__(self, root, parent):
        # Append self -> parent
        super().__init__(parent, **skin().frame_dic)
        parent.add(self)

        # Create Paned
        text_paned = PanedWindow(self, orient=VERTICAL, **skin().paned_dic)

        # Add LabelFrame
        root.LabelFrame = LabelFrame(text_paned, index=0, label_text='Info')

        # Add LabelFrame
        root.OptionFrame = OptionFrame(text_paned, index=1, label_text='Option')

        # Add AnswerFrame
        root.AnswerFrame = AnswerFrame(text_paned, label_text='Result')
        # Create Buttons with callback to preceding
        button_frame = ButtonFrame(self)

        # Pack buttons and pane
        button_frame.pack(side=TOP, expand=0, fill=X)
        text_paned.pack(side=TOP, expand=1, fill=BOTH)

"""
    The Tkinter Frame For text / butto ninterface (left)

    Label
    Top
    Result
"""

import re
import os


from tkinter import Frame, PanedWindow, Label, Button, StringVar, Entry, \
    PhotoImage, \
    VERTICAL, TOP, X, LEFT, RIGHT, BOTH, CENTER

import GuyVariables as G
import WorkVariables as W


class TextFrame(Frame):
    """TextScrollable frame
    parent must be vertical pane
    """
    def __init__(self, parent, **args):
        super_args = G.fr_arg
        super_args.update(args)
        super().__init__(parent, **super_args)

        # Add to parent paned
        parent.add(self, **G.sub_paned_arg)

        self._parent = parent  # for sash positioning
        self._arrow = None  # Button
        self._see_me = True

    def toogle(self):
        """Toggle visibility: Hide and show"""
        self._see_me = not self._see_me
        W.log(3, 'Resizing see_me: ', self._see_me)

        if self._see_me:
            self._parent.sash_place(0, 0, 22)
            self._arrow.configure(image=G.photo_down)

        else:
            G.TextPaned.sash_place(
                0, 0, G.last_label.winfo_y() + G.last_label.winfo_height())
            self._arrow.configure(image=G.photo_up)


class LabelFrame(TextFrame):
    """Some conf"""
    def __init__(self, parent):
        super().__init__(parent)

    def update(self, expand=False):
        """Called later, display what I retrived from header
        warning: expand not working well
        ESO /  not ESO
        NAco/vlt
        Reduced/raw
        Nx x Ny x Nz
        WCS detected or not
        """
        # Old name: def ResetLabel(expand=False):

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
        if W.head.wcs_bool:
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
        self.columnconfigure(0, weight=1)
        for i in text_and_props:
            arg = G.lb_arg.copy()
            arg.update({"justify": CENTER})
            if isinstance(i, (list, tuple)):
                arg.update(i[1])
            i = i[0]
            Label(self, text=i, **arg).grid(
                row=row, column=0, sticky="nsew")
            row += 1

        self._arrow = Button(
            self, command=self.toogle, image=G.photo_up, **G.bu_arg)
        self._arrow.place(relx=1., rely=0., anchor="ne")

        # place frame_title_label
        Label(self, text="Labels", **G.frame_title_arg).place(x=0, y=0)

        # Button to resize
        # TODO remove after mutualize
        arg = G.bu_arg.copy()
        arg.update({"text": "OK",
                    "command": self.update,
                    "padx": 3,
                    "width": 20
                    })
        G.last_label = Button(self, **arg)
        G.last_label.grid(row=row, column=0, sticky="nswe")
        row += 1

        if expand:
            G.label_bool = 0
            self.update()


    def set_image_parameters(self, event, destroy=True):
        """Set imageparameter"""
        # Parse
        for i in G.image_parameter_list:
            vars(W.head)[i[1]] = float(vars(G.tkentry)[i[1]].get())
            # COLOR
            if vars(W.head)[i[1]] == i[2]:
                vars(G.tkentry)[i[1]]["bg"] = "#ff9090"
            else:
                vars(G.tkentry)[i[1]]["bg"] = "#ffffff"

        # Show
        self.update(expand=False)


class OptionFrame(TextFrame):
    """Some conf"""
    def __init__(self, parent):
        super().__init__(parent)


class ResultFrame(TextFrame):
    """Some conf"""
    def __init__(self, parent):
        super().__init__(parent)

        # Pack Result Label
        Label(
            self, text="Results",
            **G.frame_title_arg).pack(side=LEFT)
        G.fit_type_label = Label(
            self, text=W.type["fit"],
            justify=CENTER, **G.lb_arg)
        G.fit_type_label.pack(fill=X)

        # Pack Answer frame
        G.AnswerFrame = Frame(G.TextPaned, bg=G.bg[0])
        G.all_frame.append("G.AnswerFrame")
        G.AnswerFrame.pack(expand=0, fill=BOTH)

        # ARROW in RESULT LABEL
        # if G.result_bool :  # label is big
        photo_down = PhotoImage(file=W.path + "/Icon/arrow_down.gif")

        G.result_frame_arrow = Button(
            self, command=ResultResize, image=photo_down, **G.bu_arg)
        G.result_frame_arrow.image = photo_down  # keep a reference
        G.result_frame_arrow.place(relx=1., rely=0., anchor="ne")


class ButtonFrame(Frame):
    """Frame 1 with quit, restart"""
    def __init__(self, parent):
        super().__init__(parent)

        # Quit
        G.bu_quit = Button(
            self, text='QUIT',
            background=G.bu_quit_color,
            command=G.Quit, **G.bu_arg)

        # Restart
        G.bu_restart = Button(
            self, text='RESTART',
            background=G.bu_restart_color,
            command=G.Restart, **G.bu_arg)

        # Expand Image Parameter
        G.bu_manual = Button(
            self, text=u'\u25be ' + 'ImageParameters',
            background=G.bu_manual_color,
            command=ImageParameter, **G.bu_arg)  # MANUAL M

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

        # Pack some buttons
        button_frame = ButtonFrame(self)
        button_frame.pack(side=TOP, expand=0, fill=X)

        # Pack paned 3 frames
        G.TextPaned = PanedWindow(self, orient=VERTICAL, **G.paned_dic)
        G.TextPaned.pack(side=TOP, expand=1, fill=BOTH)

        # LabelFrame
        G.LabelFrame = LabelFrame(G.TextPaned)

        # LabelFrame
        G.OptionFrame = LabelFrame(G.TextPaned)
        LeftTopArrow()

        # ResultFrame
        G.ResultLabelFrame = G.LeftBottomFrame = ResultFrame(G.TextPaned)


def ImageParameter():
    """Image Parameters
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
    G.image_parameter_list = [["Wavelength" + "*" + " [" + u'\u03BC' + "m]:", "wavelength", 99.],
                              ["Pixel scale" + "*" + " [''/pix]: ",
                               "pixel_scale", 99.],
                              ["Diameter" + "*" + " [m]:", "diameter", 99.],
                              ["Obstruction (d2/d1)*" + " [%]:",
                               "obstruction", 99.],
                              ["Zero point [mag]: ", "zpt", 0.],
                              ["Exposure time [sec]: ", "exptime", 1.],
                              ]  # Label, variable , default value

    ##########
    # INITIATE THE FRAME, change button color
    if G.bu_manual["background"] == G.bu_manual_color:
        G.ManualFrame = Frame(G.OptionFrame, bg=G.bg[0])
        G.all_frame.append("G.ManualFrame")
        # to keep other guys upside
        G.ManualFrame.pack(expand=0, fill=BOTH, side=TOP)
        # TITEL
        Label(G.ManualFrame, text="Parameters", **
              G.frame_title_arg).pack(side=TOP, anchor="w")
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
            vars(G.tkentry)[i[1]].bind('<Return>', GetValueIP)
            if len(str(vars(W.head)[i[1]])) > 6:  # not to long for display
                vars(G.tkvar)[i[1]].set("%.5f" % float(vars(W.head)[i[1]]))
            else:
                vars(G.tkvar)[i[1]].set(vars(W.head)[i[1]])
            row += 1

        G.bu_manual["background"] = 'green'
        G.bu_manual["text"] = u'\u25b4 ' + 'ImageParameters'

        # EXPAND
        G.top_bool = 0
        TopResize()

    elif G.bu_manual["background"] == 'green':  # destroy manualFrame  and save datas
        GetValueIP("")  # because receive event
        G.ManualFrame.destroy()
        del G.ManualFrame
        if G.in_arrow_frame == "param_title":
            G.arrtitle.destroy()
            G.in_arrow_frame = None
        G.all_frame = [x for x in G.all_frame if x !=
                       "G.ManualFrame"]  # remove MoreFrame
        G.bu_manual["background"] = G.bu_manual_color
        G.bu_manual["text"] = u'\u25be ' + 'ImageParameters'



def TopResize():        # called  later when clicking on toparrow
    if G.top_bool:
        photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")
        base = G.TextPaned.sash_coord(0)[1]  # jus height of the previous sash
        G.TextPaned.sash_place(1, 0, base + 22 + 2 * G.paned_dic["sashwidth"])
    else:
        photo = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
        place = G.parent.winfo_height() - G.TextPaned.winfo_rooty() - 200
        G.TextPaned.sash_place(1, 0, place)

    G.top_bool = not G.top_bool
    G.top_frame_arrow['image'] = photo
    G.top_frame_arrow.image = photo  # keep a reference

    return


###
# TEXT ARROWS
####
def LeftTopArrow():  # jsut draw the arrow, see after
    # TODO mutualize
    """ this do not need to be on a function but if you want to place
        the arrow it will vanish when packing other frame. SO I packed the
        arrow, otherwhise you need to redraw it all the time
    """
    # PACK TEH FRAME
    G.LeftTopArrowFrame = Frame(G.OptionFrame, **G.fr_arg)
    G.LeftTopArrowFrame.pack(side=TOP, expand=0, fill=X)

    # Load ARROW IMAGE
    if G.top_bool:  # label is big
        photo = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
    else:
        photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")

    # Pach Arrow image as button
    G.top_frame_arrow = Button(
        G.LeftTopArrowFrame, command=TopResize, image=photo, **G.bu_arg)
    G.top_frame_arrow.image = photo  # keep a reference
    G.top_frame_arrow.pack(side=RIGHT, anchor="ne", expand=0)


def ResultResize(how="max"):  # called  later
    # if not G.result_bool : # this is to expand
    if how == "max":  # resize max
        base = G.TextPaned.sash_coord(0)[1]  # jus height of the previous sash
        G.TextPaned.sash_place(1, 0, base + 22 + 2 * G.paned_dic["sashwidth"])
        if W.verbose > 3:
            print("REsize result: ", 22)

    elif how == "full":  # see everything but not more
        def Pos():  # calculate position of the sash
            # to expand the widget, and estimate their size, no number is interpreted ad infinity
            G.TextPaned.sash_place(1, 0, )
            corner2 = max([i.winfo_rooty() for j in G.LeftBottomFrame.winfo_children(
            ) for i in j.winfo_children()])  # the max size
            base = G.LeftBottomFrame.winfo_rooty()  # top of the left bottom Frame
            size = corner2 - base                   # size fo the left Botttom Frame
            base_sash1 = G.OptionFrame.winfo_rooty()
            pos = G.parent.winfo_height() - size - base_sash1

            return max(pos, 22)  # minimum 22 pixels

        pos = Pos()
        G.TextPaned.sash_place(1, 0, pos)
        if W.verbose > 3:
            print("REsize Top: ", pos)

    return


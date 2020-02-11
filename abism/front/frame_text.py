"""
    The Tkinter Frame For text / butto ninterface (left)

    Label
    Option
    Answer

"""
import re

import tkinter as tk

from abism.front.util_front import photo_up, photo_down, \
    open_backgroud_and_substract
import abism.front.tk_extension as tk_ext

from abism.util import log, get_root, quit_process, restart, get_state, \
    EPhot, ESky



class LeftFrame(tk.Frame):
    """Full Container"""
    def __init__(self, root, parent):
        # Append self -> parent
        super().__init__(parent)

        # Create Paned && Save
        text_paned = tk.PanedWindow(self, orient=tk.VERTICAL)
        root.paned_text = text_paned

        # Add LabelFrame
        root.frame_label = LabelFrame(text_paned, index=0, label_text='Info')

        # Add LabelFrame
        root.frame_option = OptionFrame(text_paned, index=1, label_text='Option')

        # Add AnswerFrame
        root.frame_answer = AnswerFrame(text_paned, label_text='Result')

        # Create Buttons with callback to preceding
        root.frame_button = ButtonFrame(self)

        # Pack buttons and pane
        root.frame_button.pack(side=tk.TOP, expand=0, fill=tk.X)
        text_paned.pack(side=tk.TOP, expand=1, fill=tk.BOTH)


class TextFrame(tk.Frame):
    """TextScrollable frame
    parent <- must be vertical pane
    children <- are grided
    """
    def __init__(self, parent, label_text='Frame', index=None):
        super().__init__(parent)

        # Prepare grid attributes
        self.columnconfigure(0, weight=1)

        # Add to parent paned
        parent.add(self, minsize=22, pady=0, sticky='nsew')

        self._parent = parent  # for sash positioning
        self._arrow = None  # Button
        self._last = None  # To get the normal size
        self._see_me = True  # Bool do you see me
        self._label_text = label_text
        self._index = index  # for sash

    def init_after(self, add_title=True):
        """Place Button, Label and last widget"""
        # Place button to resize
        if self._index is not None:
            self._arrow = tk.Button(
                self, command=self.toogle, image=photo_up())
            self._arrow.place(relx=1., rely=0., anchor="ne")

        # Place a label for the eye
        if add_title:
            tk_ext.TitleLabel(self, text=self._label_text).place(x=0, y=0)

        # Place last widget
        self.update_last_widget()

    def update_last_widget(self):
        """Put last widget at end"""
        # Last widget
        if self._last is not None:
            self._last.destroy()
        self._last = tk.Label(self, height=0, width=0)
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

        self.update_sash()

    def update_sash(self):
        """Update sash position"""
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
            i_height += 5 + max(0, self._last.winfo_y() - self._last.winfo_height())
        else:
            self._arrow.configure(image=photo_down())
        self._parent.sash_place(self._index, 0, i_height)

        # Log after
        log(3, 'New sash pos: height=', i_height)

    def init_will_toogle(self, visible=True, add_title=True):
        """Best way to showme: Place last and togfle later
        Usually called to set visible when some widget added
        This trick is due to the fact widget will be updated at next tk loop
        """
        self.init_after(add_title=add_title)
        def will_refresh():
            self.update()
            self.toogle(visible=visible)
        self.after_idle(will_refresh)

    def will_update_sash(self):
        """The Reformat when added or deleted"""
        def will_refresh():
            self.update_last_widget()
            self.update()
            self.update_sash()
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
        # pylint: disable = too-many-statements, too-many-branches

        # Reset info, to avoid appending
        self.clear()

        # Declare list of label (text, properties)
        text_n_props = []

        # Get company
        company = 'ESO' if get_root().header.company == "ESO" else 'NOT ESO'

        # Get instrument
        if get_root().header.instrument == "NAOS+CONICA":
            instrument = "NaCo"
        else:
            instrument = get_root().header.instrument
        telescope = re.sub("-U.", "",
                           get_root().header.telescope.replace("ESO-", ""))
        text_n_props.append((company + " / " + telescope + " / " + instrument, {}))

        # Get is_reduced
        if "reduced_type" in vars(get_root().header):
            lbl = get_root().header.reduced_type + ': '
        else:
            lbl = ''

        # Get Size : Nx * Ny * Nz
        shape = list(get_state().image.im0.shape[::-1])
        if "NAXIS3" in get_root().header.header.keys():
            shape.append(get_root().header.header["NAXIS3"])
            lbl += "%i x %i x %i" % (shape[0], shape[1], shape[2])
        else:
            lbl += "%i x %i " % (shape[0], shape[1])
        text_n_props.append((lbl, {}))

        # WCS
        if get_root().header.wcs is not None:
            lbl = "WCS detected"
        else:
            lbl = "WCS NOT detected"
        text_n_props.append((lbl, {}))

        # Header reads Strehl variables ?
        from math import isnan
        bolt = isnan(get_root().header.diameter)
        bolt = bolt or isnan(get_root().header.wavelength)
        bolt = bolt or isnan(get_root().header.obstruction)
        bolt = bolt or isnan(get_root().header.pixel_scale)
        if bolt:
            lbl = "WARNING: some parameters not found"
            text_n_props.append((lbl, {"fg": "red"}))
            get_root().frame_option.toogle_image_parameter()
        else:
            lbl = "Parameters read from header"
            text_n_props.append((lbl, {"fg": "blue"}))

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
            text_n_props.append((lbl, {"fg": "red"}))

        # Grid labels
        for text, props in text_n_props:
            label = tk.Label(self, text=text, justify=tk.CENTER, **props)
            label.grid(column=0, sticky="nsew")

        # Show me
        self.init_will_toogle()


class OptionFrame(TextFrame):
    """Some conf"""
    def __init__(self, parent, **args):
        super().__init__(parent, **args)
        # Image parameter
        self.see_image_parameter = False
        self.frame_image_parameter = None
        self.image_parameter_entry_dic = {}
        self.image_parameter_tkvar_dic = {}

        # Manual cut image
        self.see_manual_cut = False
        self.frame_manual_cut = None

        # More analysis
        self.see_more_analysis = False
        self.frame_more_analysis = None
        self.parent_more_analysis = None

        # Manual Bacground
        self.see_manual_background = False
        self.frame_manual_background = None

        self.init_after()


    # Image Parameters
    #############################################################

    def toogle_image_parameter(self):
        self.see_image_parameter = not self.see_image_parameter
        if self.see_image_parameter:
            self.open_image_parameter()
            get_root().frame_button.config_button_image_less()
        else:
            self.close_image_parameter()
            get_root().frame_button.config_button_image_more()

    @staticmethod
    def get_image_parameter_list():
        return [
            [u'Wavelength* [\u03BCm]:', 'wavelength', float('nan')],
            ["Pixel scale* [''/pix]: ", 'pixel_scale', float('nan')],
            ["Diameter* [m]:", 'diameter', float('nan')],
            ["Obstruction (d2/d1)* [%]:", 'obstruction', float('nan')],
            ["Zero point [mag]: ", 'zpt', float('nan')],
            ["Exposure time [sec]: ", 'exptime', float('nan')],
            ]

    def set_image_parameter(self):
        """Set imageparameter, labels"""
        log(0, "New image parameters:")
        for label, key, badvalue in self.get_image_parameter_list():
            value = float(self.image_parameter_entry_dic[key].get())
            # Change header field
            vars(get_root().header)[key] = value

            # Log (this is important)
            log(0, f'{value:10.4f}  <-  {label}')
            # COLOR
            if vars(get_root().header)[key] == badvalue:
                self.image_parameter_entry_dic[key]["bg"] = "#ff9090"
            else:
                self.image_parameter_entry_dic[key]["bg"] = "#ffffff"

        # Show
        get_root().frame_label.update_label()

    def open_image_parameter(self):
        # Grid new frame
        self.frame_image_parameter = tk.Frame(self)
        self.frame_image_parameter.grid(sticky='nsew')

        # Pack title
        tl = tk_ext.TitleLabel(self.frame_image_parameter, text='Parameters')
        tl.pack(side=tk.TOP, anchor="w")

        # Pack grid frame
        frame_manual_grid = tk.Frame(self.frame_image_parameter)
        frame_manual_grid.pack(expand=0, fill=tk.BOTH, side=tk.TOP)
        frame_manual_grid.columnconfigure(0, weight=1)
        frame_manual_grid.columnconfigure(1, weight=1)

        # Loop for all needed variable
        # And grid their (label, entry)
        for row, (text, key, value) in enumerate(self.get_image_parameter_list()):
            # Init variable (may cut it)
            string_var = tk.StringVar()
            s_from_header = vars(get_root().header)[key]
            if len(str(s_from_header)) > 6:
                string_var.set("%.5f" % float(s_from_header))
            else:
                string_var.set(s_from_header)

            # Grid label
            label = tk.Label(
                frame_manual_grid, text=text,
                justify=tk.LEFT, anchor="nw")
            label.grid(row=row, column=0, sticky="NSEW")

            # Create entry <- string_var
            entry = tk.Entry(
                frame_manual_grid, width=10,
                textvariable=string_var)
            # Color entry
            if vars(get_root().header)[key] == value:
                entry["bg"] = "#ff9090"
            # Bind entry Return
            entry.bind(
                '<Return>', lambda _: self.set_image_parameter())

            # Grid entry && Save
            entry.grid(row=row, column=1, sticky="NSEW")
            self.image_parameter_tkvar_dic[key] = string_var
            self.image_parameter_entry_dic[key] = entry

        # Show me
        self.init_will_toogle(visible=True, add_title=False)

    def close_image_parameter(self):
        self.frame_image_parameter.destroy()
        self.will_update_sash()


    # Manual Cut
    #############################################################

    def toogle_manual_cut(self):
        """Stupid switch"""
        self.see_manual_cut = not self.see_manual_cut
        log(5, "Manual Cut see me ?", self.see_manual_cut)
        if self.see_manual_cut:
            self.open_manual_cut()
        elif self.frame_manual_cut:
            self.close_manual_cut()

    def open_manual_cut(self):
        # Grid main
        self.frame_manual_cut = tk.Frame(self)
        self.frame_manual_cut.grid(sticky='nsew')

        # Pack title
        lt = tk_ext.TitleLabel(self.frame_manual_cut, text="Cut image scale")
        lt.pack(side=tk.TOP, anchor="w")

        # Pack rest
        parent = tk.Frame(self.frame_manual_cut)
        parent.pack(side=tk.TOP, expand=0, fill=tk.X)
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        # Keep ref to string_vars
        string_vars = []

        # Define callback
        def set_cuts(_):
            get_state().i_image_max_cut = float(string_vars[0].get())
            get_state().i_image_min_cut = float(string_vars[1].get())
            get_root().frame_image.refresh_image()

        # Grid them both
        lst = [["Max cut", get_state().i_image_max_cut],
               ["Min cut", get_state().i_image_min_cut]]
        for text, value in lst:
            # Label
            l = tk.Label(parent, text=text)
            l.grid(column=0, sticky="snew")

            # Entry
            string_var = tk.StringVar()
            string_var.set("%.1f" % value)
            string_vars.append(string_var)
            e = tk.Entry(parent, width=10, textvariable=string_var)
            e.grid(column=1, sticky="nsew")
            e.bind('<Return>', set_cuts)

        # Grid close
        bu_close = tk.Button(
            parent, text=u'\u25b4 ' + 'Close',
            command=self.close_manual_cut)
        bu_close.grid(column=0, columnspan=2)

        # Redraw
        self.init_will_toogle(visible=True, add_title=False)

    def close_manual_cut(self):
        self.frame_manual_cut.destroy()
        self.will_update_sash()


    # More analysis
    #############################################################

    def toogle_more_analysis(self, parent=None):
        self.see_more_analysis = not self.see_more_analysis

        # Keep ref to change label
        if parent is not None:
            self.parent_more_analysis = parent

        # Toogle menu
        self.parent_more_analysis.toogle_more_options()

        # Discriminate show / hide
        if self.see_more_analysis:
            self.open_more_analysis()
        else:
            self.close_more_analysis()

    @staticmethod
    def grid_more_checkbuttons(frame):
        # Define callback
        def on_change_aniso(int_var):
            get_state().b_aniso = int_var.get()
            # Aniso
            if get_state().b_aniso:
                msg = "Anisotropy: angular dimension are fitted separately"
            else:
                msg = "Isotropy: angular dimension are fitted together"
            log(0, msg)

        def on_change_psf(int_var):
            get_state().b_same_psf = int_var.get()
            if get_state().b_same_psf:
                msg = "Same psf: Both stars are fitted with same psf"
            else:
                msg = "Not same psf: Each star is fitted with independant psf"
            log(0, msg)

        def on_change_saturated(int_var):
            get_state().b_saturated = int_var.get()
            if get_state().b_saturated:
                msg = "Saturated: fit assuming a max level cutting the intensity shape"
            else:
                msg = "Not saturated: fit sull psf"
            log(0, msg)

        # Declare label and associated variable
        text_n_var_n_fct = (
            ('Anisotropy', get_state().b_aniso, on_change_aniso),
            ('Binary same psf', get_state().b_same_psf, on_change_psf),
            ('Fit saturation', get_state().b_saturated, on_change_saturated),
        )

        # Create && Grid all
        for (text, var, fct) in text_n_var_n_fct:
            int_var = tk.IntVar(value=var)
            check = tk.Checkbutton(
                frame, text=text, variable=int_var,
                command=lambda fct=fct, int_var=int_var: fct(int_var))
            check.grid(column=0, columnspan=2, sticky='nwse')

    def is_more_analysis_visible(self):
        """Used by menu bar"""
        return self.see_more_analysis

    def open_more_analysis(self):
        """Create More Frame"""
        # Grid root
        self.frame_more_analysis = tk.Frame(
            get_root().frame_option)
        self.frame_more_analysis.grid(sticky='nsew')

        # Pack title
        label_more = tk_ext.TitleLabel(self.frame_more_analysis, text="More Options")
        label_more.pack(side=tk.TOP, anchor="w")

        # Pack rest
        frame_more_grid = tk.Frame(
            self.frame_more_analysis)
        frame_more_grid.pack(side=tk.TOP, expand=0, fill=tk.X)
        frame_more_grid.columnconfigure(0, weight=1)
        frame_more_grid.columnconfigure(1, weight=1)

        # Grid button: substract background
        bu_subtract_bg = tk.Button(
            frame_more_grid, text='SubstractBackground',
            command=open_backgroud_and_substract)
        bu_subtract_bg.grid(row=0, column=0, columnspan=2, sticky="nswe")

        # Grid Menu: set photometric type
        def create_phot_menu(frame):
            menu_phot = tk.Menubutton(
                frame, text=u'\u25be '+'Photometry',
                relief=tk.RAISED)
            menu_phot.menu = tk.Menu(menu_phot, tearoff=False)
            menu_phot['menu'] = menu_phot.menu

            lst = [
                ['Elliptical Aperture', EPhot.ELLIPTICAL],
                ['Fit', EPhot.FIT],
                ['Rectangle Aperture', EPhot.RECTANGLE],
                ['Manual', EPhot.MANUAL],
            ]

            def set_phot(_, tag):
                """Passing string_var to avoid gc"""
                log(3, 'Setting Photometry mesurement:', tag, '->', tag.value)
                get_state().e_phot_type = tag

            # Add radio buttons:
            string_var = tk.StringVar()
            string_var.set(get_state().e_phot_type)
            for text, tag in lst:
                menu_phot.menu.add_radiobutton(
                    label=text, command=lambda tag=tag: set_phot(string_var, tag),
                    variable=string_var, value=tag)

            return menu_phot

        create_phot_menu(frame_more_grid).grid(row=1, column=1, sticky="nswe")

        # Grid menu: set noise type (or background estimation)
        def create_noise_menu(frame):
            # Root
            menu = tk.Menubutton(
                frame, text=u'\u25be '+'Background',
                relief=tk.RAISED)
            menu.menu = tk.Menu(menu, tearoff=False)
            menu['menu'] = menu.menu


            lst = [
                ["Annulus", ESky.ANNULUS],
                ['Fit', ESky.FIT],
                ["8Rects", ESky.RECT8],
                ['Manual', ESky.MANUAL],
                ["None", ESky.NONE],
            ]

            def set_noise(_, tag):
                log(3, 'Setting background mesurement:', tag, '->', tag.value)
                get_state().e_sky_type = tag
                if tag == ESky.NONE:
                    get_state().i_background = 0

            string_var = tk.StringVar()
            string_var.set(get_state().e_sky_type)
            for text, tag in lst:
                if tag == ESky.MANUAL:
                    menu.menu.add_radiobutton(
                        label=text, command=self.toogle_manual_background,
                        variable=string_var, value=tag)
                else:
                    menu.menu.add_radiobutton(
                        label=text, command=lambda tag=tag: set_noise(string_var, tag),
                        variable=string_var, value=tag)

            return menu

        menu_noise = create_noise_menu(frame_more_grid)
        menu_noise.grid(row=1, column=0, sticky="nswe")

        # Grid check buttons: for conf
        self.__class__.grid_more_checkbuttons(frame_more_grid)

        bu_close = tk.Button(
            frame_more_grid, text=u'\u25b4 '+'Close',
            command=self.toogle_more_analysis)
        bu_close.grid(column=0, columnspan=2)

        # Show me
        self.init_will_toogle(visible=True, add_title=False)

    def close_more_analysis(self):
        """Close the Frame"""
        if not self.frame_more_analysis: return

        # Close sub frame
        self.close_manual_background()

        self.frame_more_analysis.destroy()

        # Refresh
        self.will_update_sash()


    # Manual background
    #############################################################

    def toogle_manual_background(self):
        """Create manual background frame"""
        self.see_manual_background = not self.see_manual_background
        if self.see_manual_background:
            self.open_manual_background()
        else:
            self.close_manual_background()

    def open_manual_background(self):
        get_state().e_sky_type = ESky.MANUAL

        # Grid root
        self.frame_manual_background = tk.Frame(self)
        self.frame_manual_background.grid(sticky='nsew')
        self.frame_manual_background.columnconfigure(0, weight=1)
        self.frame_manual_background.columnconfigure(1, weight=1)

        def on_enter(string_var):
            i_in = float(string_var.get())
            get_state().i_background = i_in
            log(0, "ManualBackground setted to:", i_in)

        # Grid label
        label = tk.Label(
            self.frame_manual_background, text="Background value:")
        label.grid(row=0, column=0, sticky="snew")

        # Grid entry
        string_var = tk.StringVar()
        string_var.set(get_state().i_background)
        entry = tk.Entry(
            self.frame_manual_background, width=10,
            textvariable=string_var)
        entry.grid(row=0, column=1, sticky="nsew")
        entry.bind('<Return>', lambda event: on_enter(string_var))

        # Grid close button
        button = tk.Button(
            self.frame_manual_background,
            text=u'\u25b4 ' + 'Close',
            command=self.close_manual_background)
        button.grid(row=1, column=0, columnspan=2)

        # Show Me
        self.init_will_toogle(visible=True, add_title=False)

    def close_manual_background(self):
        if not self.see_manual_background: return
        self.frame_manual_background.destroy()
        self.will_update_sash()


class AnswerFrame(TextFrame):
    """Some conf"""
    def __init__(self, parent, **args):
        super().__init__(parent, **args)

        for i in range(4):
            self.grid_columnconfigure(i, weight=1, uniform="fred")

        # For fit param
        self.text_fit_param = None
        self.i_tab_1 = 0
        self.i_tab_2 = 0
        self.bu_fit = None

        self.init_after()

    def init_after(self, add_title=True):
        """Add fit type label"""
        # Title left
        label = tk_ext.TitleLabel(self, text=self._label_text)
        label.grid(row=0, column=0, sticky=tk.W)

        # Add also standard above
        super().init_after(add_title=False)

    def grid_text_answer(self):
        """Grid tk text for results
        Return: tk text to be filled
        """
        # Create text
        text = tk.Text(self)

        # Declare size callback
        def on_resize_text(event):
            # pylint: disable = no-member
            if 'i_tab_len' not in vars(text):
                text.i_tab_len = 40
            i_tab = min((text.i_tab_len) * 12, event.width / 2)
            log(5, 'Answer, Resize text:', event, i_tab)
            event.widget.configure(tabs=(i_tab, tk.LEFT))

        # Configure Text
        text.bind("<Configure>", on_resize_text)
        text.tag_configure('tag-important', foreground=tk_ext.scheme.important)
        text.tag_configure('tag-center', justify=tk.CENTER)
        text.tag_configure('tag-blue', foreground=tk_ext.scheme.solarized_blue)

        # Grid text
        text.grid(row=2, columnspan=4, sticky='new')

        return text

    def grid_top_button(self, convertion_callback):
        """Grid coordinate convertion and Show fit dic"""
        # Fit type middle
        fit_type_label = tk.Label(
            self, justify=tk.CENTER, text=get_state().s_fit_type)
        fit_type_label.grid(row=0, column=1)

        # Declare button info
        if get_state().s_answer_unit == "detector":
            s_button = u"\u21aa"+'To sky     '
            s_label = "In detector units"
        else:
            s_button = u"\u21aa"+'To detector'
            s_label = "In sky units"

        def on_change_coord():
            if get_state().s_answer_unit == 'detector':
                get_state().s_answer_unit = 'sky'
            else:
                get_state().s_answer_unit = 'detector'
            self.close_fit_param()
            convertion_callback()

        # Label showing current coord
        label = tk.Label(
            self, text=s_label, justify=tk.LEFT, anchor="nw")
        label.grid(row=1, column=0, sticky=tk.W)

        # Button to change coordonate
        bu_coord = tk.Button(
            self, text=s_button, command=on_change_coord)
        bu_coord.grid(row=0, column=3, sticky=tk.E)
        get_root().bind_all(
            "<Control-k>", lambda _: on_change_coord())
        bu_coord.set_hover_info(
            "<C-k>: Change coordinate system of displayed answer\n"
            "sKy <-> detector")

        def on_toogle_param():
            if self.text_fit_param is None:
                self.open_fit_param()
            else:
                self.close_fit_param()

        # Show fit dctionary
        self.bu_fit = tk.Button(
            self, text=u'\u25be Show Fit Param',
            command=on_toogle_param)

        get_root().bind_all(
            "<Control-d>", lambda _: on_toogle_param())
        self.bu_fit.set_hover_info(
            "<C-d>: Show/Hide Fit Dictionaries:\nparameters and errors")
        self.bu_fit.grid(row=0, column=2)


    def get_new_text_frame(self, convertion_callback):
        # Save visibility
        b_show_fit_param = self.text_fit_param is not None

        # Pack fit type in Frame
        self.clear()

        # Button to change cord
        self.grid_top_button(convertion_callback)
        text = self.grid_text_answer()

        # Restore visibility (fit_param)
        if b_show_fit_param:
            self.open_fit_param()
        return text


    def open_fit_param(self):
        self.bu_fit.configure(text=u'\u25b4 Hide Fit Param')
        self.text_fit_param = tk.Text(self)
        self.text_fit_param.grid(row=2, columnspan=4, sticky='new')

        stg, (self.i_tab_1, self.i_tab_2) = get_state().str_fit_param()
        self.text_fit_param.insert(tk.END, stg)

        self.text_fit_param.configure(tabs=(
            self.i_tab_1 * 12, tk.LEFT, self.i_tab_2 * 12, tk.LEFT))

    def close_fit_param(self):
        try:
            self.bu_fit.configure(text=u'\u25be Show Fit Param')
            self.text_fit_param.destroy()
        except BaseException:
            pass
        self.text_fit_param = None


class ButtonFrame(tk.Frame):
    """Frame 1 with quit, restart"""
    def __init__(self, parent, **args):
        super().__init__(parent, **args)

        self.frame_cube = None

        # Define button option
        opts = {}

        # Create Quit
        opts.update({'background': tk_ext.scheme.quit})
        bu_quit = tk.Button(
            self, text='QUIT',
            command=quit_process, **opts)

        # Create Restart
        opts.update({'background': tk_ext.scheme.restart})
        bu_restart = tk.Button(
            self, text='RESTART',
            command=restart, **opts)
        get_root().bind_all("<Control-r>", lambda _: restart())
        bu_restart.set_hover_info(
            "<C-R>: Restart Absim with the same command line")

        # Create Expand Image Parameter
        opts.update({'background': tk_ext.scheme.parameter1})
        self.bu_manual = tk.Button(
            self, text=u'\u25be ' + 'ImageParameters',
            command=get_root().frame_option.toogle_image_parameter, **opts)
        get_root().bind_all(
            "<Control-i>", lambda _: get_root().frame_option.toogle_image_parameter())
        self.bu_manual.set_hover_info(
            "<C-i>: Show/Hide Image parameters\n"
            "necessaries for Strehl mesurement (λ, pxl scale, diam, obstr)\n"
            "or to give sky coordinates (zpt, exposure)")

        # Grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        bu_quit.grid(row=0, column=0, sticky="nsew")
        bu_restart.grid(row=0, column=1, sticky="nsew")
        self.bu_manual.grid(row=1, column=0, columnspan=2, sticky="nsew")

    def config_button_image_less(self):
        self.bu_manual['background'] = tk_ext.scheme.parameter2
        self.bu_manual['text'] = u'\u25b4 ImageParameters'

    def config_button_image_more(self):
        self.bu_manual['background'] = tk_ext.scheme.parameter1
        self.bu_manual['text'] = u'\u25be ImageParameters'


    def toogle_cube(self):
        """Prepare Cube buttons"""
        # Try to destroy if not a cube
        # Create a cube interface else
        if not get_state().image.is_cube:
            self.close_cube()
        else:
            self.close_cube()
            self.open_cube()

    def close_cube(self):
        try:
            self.frame_cube.destroy()
        except BaseException:
            pass

    def open_cube(self):
        # Gird Frame
        self.frame_cube = tk.Frame(self)
        self.frame_cube.grid(sticky='nsew', columnspan=2)

        # Conf && ad title
        for i in range(3):
            self.frame_cube.columnconfigure(i, weight=1)
        lt = tk_ext.TitleLabel(self.frame_cube, text="Cube Number")
        lt.grid(row=0, column=0, columnspan=3, sticky="w")

        # Define tk variable (1 based)
        int_var = tk.IntVar()
        int_var.set(get_state().image.cube_num)

        # callback
        def scroll_cube(i_click):
            """Callback for cube button + -
            Note: cube_num is "0 based" and int_var is "1 based"
            """
            # Get in
            cube_num = get_state().image.cube_num
            if i_click == 0:
                cube_num = int_var.get()
            else:
                cube_num += i_click

            # Cycle
            if cube_num < 1:
                cube_num = get_state().image.i_cube_len
            elif cube_num > get_state().image.i_cube_len:
                cube_num = 1

            # Get limits
            ax = get_root().frame_image.get_figure().axes[0]
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            print(xlim, ylim)

            # Set and update
            get_state().image.cube_num = cube_num
            int_var.set(get_state().image.cube_num)
            get_state().image.update_cube()
            get_root().frame_image.draw_image(new_fits=False)

            # Set limits
            ax = get_root().frame_image.get_figure().axes[0]
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

            # Refresh
            get_root().frame_image.refresh_image()

            # Reconnect pick
            if get_state().pick is not None:
                get_state().pick.disconnect()
                get_state().pick.connect()



        # Button left
        bu_left = tk.Button(
            self.frame_cube, text='<-',
            command=lambda: scroll_cube(-1))
        bu_left.grid(row=1, column=0, sticky="nsew")
        get_root().bind_all(
            "<Control-b>", lambda _: scroll_cube(-1))
        bu_left.set_hover_info(
            "<C-b>: Display previous cube image\n(Backward)")

        # Entry
        entry = tk.Entry(
            self.frame_cube, width=10, justify=tk.CENTER, textvariable=int_var)
        entry.bind("<Return>", lambda x: scroll_cube(0))
        entry.grid(row=1, column=1, sticky="nsew")

        # Button right
        bu_right = tk.Button(
            self.frame_cube, text='->',
            command=lambda: scroll_cube(1))
        bu_right.grid(row=1, column=2, sticky="nsew")
        get_root().bind_all(
            "<Control-f>", lambda _: scroll_cube(1))
        bu_right.set_hover_info(
            "<C-f>: Display next cube image\n(Forward)")

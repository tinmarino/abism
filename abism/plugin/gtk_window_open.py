"""
    Open File dialog for my Ubuntu 19.10 / Gnome 3
    Requires GTK, so will usually fail
    But the tk ask open file is so ugly, and FileOpen may come too
"""
import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class GtkDialog(Gtk.FileChooserDialog):
    """The dialog to open a fits image"""
    def __init__(self, title='', filetypes=None, initialdir=''):
        super().__init__(
            title=title,
            parent=None,
            action=Gtk.FileChooserAction.OPEN)

        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        if initialdir:
            self.set_current_folder(os.path.abspath(initialdir))

        for text_n_regex in filetypes:
            self.add_one_filter(text_n_regex)




    def get_response(self):
        """Born, Work and die"""
        # Metro
        response = self.run()
        # Boulot
        if response == Gtk.ResponseType.OK:
            fname = self.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            fname = ''
        self.destroy()
        # Dodo
        return fname


    def add_one_filter(self, text_n_regex):
        text, regex = text_n_regex
        filter_text = Gtk.FileFilter()
        filter_text.set_name(text)
        filter_text.add_pattern(regex)
        self.add_filter(filter_text)



def gtk_askopenfilename(**args):
    """Returns filename given by user"""
    dialog = GtkDialog(**args)
    res = dialog.get_response()
    return res



def test():
    gtk_askopenfilename(
        title="Open a FITS image",
        filetypes=[("FITS", "*.fits"), ('Python', '*.py'), ("allfiles", "*")],
        initialdir='.')

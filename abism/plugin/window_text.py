"""
    Helper to open a tk window with some text
used by manual and header
"""
import tkinter as tk

from abism.util import log


class WindowText(tk.Tk):
    """A window with some text in it.
    TODO mardown nice view
    """
    def __init__(self, title='', geometry='', text=''):
        super().__init__()

        if title: self.title(title)
        if geometry: self.geometry(geometry)

        self.find_num = [0]
        self.find_list = []
        # Previous string
        self.s_old = ''

        # Pack
        self.pack_head()
        self.pack_body(text)


    def pack_body(self, text):
        """Pack text and scrollbar"""
        # Pack Scrollbar
        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Pack Text
        self.text = tk.Text(self)
        self.text.insert(tk.END, text)
        self.text.configure(state=tk.DISABLED)
        self.text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.text.configure(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.text.yview)


    def pack_head(self):
        """Pack buttons to scroll"""
        head_frame = tk.Frame(self)
        head_frame.pack(side=tk.TOP, fill=tk.X)
        for i in range(4):
            head_frame.columnconfigure(i, weight=1)

        # tk.Label Find
        label_find = tk.Label(
            head_frame, text='Find expression: ')
        label_find.grid(row=0, column=0, sticky='nsew')

        # tk.Texttk.Entry search
        self.edit = tk.Entry(head_frame)
        self.edit.bind("<Return>", lambda event: self._scroll("+"))
        self.edit.grid(row=0, column=1, sticky="nsew")
        self.edit.focus_set()

        # - Previous
        tk.Button(
            head_frame, text='<-',
            command=lambda: self._scroll("-")
            ).grid(row=0, column=2, sticky="nsew")

        # + Next
        tk.Button(
            head_frame, text='->',
            command=lambda: self._scroll("+")
            ).grid(row=0, column=3, sticky="nsew")


    def colorize_md(self):
        """Colorize text with markdown syntax"""


    def _find(self):
        """Find string from edit in text
        """
        self.text.tag_remove('found', '1.0', tk.END)
        s_to_find = self.edit.get()
        if s_to_find:
            if s_to_find != self.s_old:  # reset
                self.find_num[0] = 0
                self.s_old = s_to_find
            idx = '1.0'
            while 1:
                idx = self.search(s_to_find, idx, nocase=1, stopindex=tk.END)
                if not idx:
                    break
                lastidx = '%s+%dc' % (idx, len(s_to_find))
                self.text.tag_add('found', idx, lastidx)
                self.find_list.append(idx)
                idx = lastidx
            self.text.tag_config('found', foreground='blue')
        self.edit.focus_set()

        return s_to_find


    def _scroll(self, side):
        """AutoScroll when user click + or -"""
        # Get
        s_to_find = self._find()

        # Check in
        if len(self.find_list) == 0:
            log(0, "FitsHeaderWindow: Pattern '",
                s_to_find, "' not found in header")
            return
        if self.find_num[0] != 0:
            if side == "+":
                self.find_num[0] += 1
            if side == "-":
                self.find_num[0] -= 1
        lastidx = self.find_list[self.find_num[0]]
        idx = '%s+%dc' % (lastidx, len(s_to_find))
        self.see(lastidx)
        try:
            self.tag_remove('on', '1.0', tk.END)
        except:
            pass
        self.tag_add("on", lastidx, idx)
        self.tag_config("on", foreground="red")
        if self.find_num[0] == 0:
            self.find_num[0] += 1
        return

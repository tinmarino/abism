"""
    Helper to open a tk window with some text
used by manual and header
"""
import re
import tkinter as tk

from abism.util import log


class WindowText(tk.Tk):
    """A window with some text in it"""

    def __init__(self, title='', geometry='', text='', color_md=False):
        super().__init__()

        if title: self.title(title)
        if geometry: self.geometry(geometry)

        self.find_num = [0]
        self.find_list = []
        # Previous string
        self.s_old = ''

        # Replace markdown list
        self.txt = text
        if color_md:
            self.txt = re.sub(r'^(\s*)\*', r'\1☀', self.txt, flags=re.MULTILINE)

        # Pack
        self.pack_head()
        self.pack_body()

        # Color
        if color_md:
            MarkdownColorizer(self.tk_text, self.txt).colorize()


    def pack_body(self):
        """Pack text and scrollbar"""
        # Pack Scrollbar
        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Pack Text
        self.tk_text = tk.Text(self)
        self.tk_text.insert(tk.END, self.txt)
        self.tk_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Configure
        self.tk_text.configure(wrap=tk.WORD)
        self.tk_text.configure(state=tk.DISABLED)
        self.tk_text.configure(yscrollcommand=self.scroll.set)

        # Bind
        self.tk_text.bind(
            "<Control-a>",
            lambda _: self.tk_text.tag_add("sel", "1.0", "end"))
        # make sure the widget gets focus when clicked on,
        # to enable highlighting and copying to the clipboard
        self.tk_text.bind("<1>", lambda _: self.tk_text.focus_set())
        self.bind_all(
            "<Control-f>",
            lambda _: self.edit.focus_set())

        # Bind configure scroll
        self.scroll.config(command=self.tk_text.yview)


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


    def _find(self):
        """Find string from edit in text
        """
        # Get string <- edit
        self.tk_text.tag_remove('found', '1.0', tk.END)
        s_to_find = self.edit.get()
        log(9, 'Searching:', s_to_find)
        if not s_to_find: return ''

        # Reset
        if s_to_find != self.s_old:
            self.find_num[0] = 0
            self.find_list = []
            self.s_old = s_to_find

        # Find next
        idx = '1.0'
        while True:
            idx = self.tk_text.search(
                s_to_find, idx,
                nocase=1, stopindex=tk.END, regexp=True)
            if not idx:
                break
            lastidx = '%s+%dc' % (idx, len(s_to_find))
            self.tk_text.tag_add('found', idx, lastidx)
            self.find_list.append(idx)
            idx = lastidx
        self.tk_text.tag_config('found', foreground='#268bd2')
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

        # Scroll to last index
        lastidx = self.find_list[self.find_num[0]]
        idx = '%s+%dc' % (lastidx, len(s_to_find))
        self.tk_text.yview(lastidx)

        # Update colors
        self.tk_text.tag_remove('on', '1.0', tk.END)
        self.tk_text.tag_add("on", lastidx, idx)
        self.tk_text.tag_config("on", foreground='#dc322f')
        if self.find_num[0] == 0:
            self.find_num[0] += 1
        return


# Dic: tag_name: (regex, tag_params)
md_dic = {
    'h1': (r'^# .*$', {
        # Violet
        'foreground': '#6c71c4',
        'font': 'Helvetica 20',
    }),
    'h2': (r'^## .*$', {
        # Blue
        'foreground': '#268bd2',
        'font': 'Helvetica 18',
    }),
    'h3': (r'^### .*$', {
        # Cyan
        'foreground': '#2aa198', 'underline': True,
        'font': 'Helvetica 15',
    }),
    'h4': (r'^#### .*$', {
        # Green
        'foreground': '#859900', 'underline': True,
    }),
    'backtick': (r'`[^`]*`', {
        # Magenta
        'foreground': '#d33682',
    }),
    'bold': (r'__.+?__', {
        'font': 'Helvetica 13 bold',
    }),
    'bold2': (r'\*\*.+?\*\*', {
        'font': 'Helvetica 13 bold',
    }),
}

# Regex to hide (second loop)
r_elide = r'^# |^## |^### |^#### |__|\*\*|`'


# Regex for link [visible](#intenal_link)
r_link = r'\[(.*?)\]\((.*?)\)'


class MarkdownColorizer:
    """Colorize text widget with markdown text in it
    Hardcode colors
    Copy from Suraj Singh ColorLight.py (by hand)
    """

    def __init__(self, tk_text, txt):
        self.tk_text = tk_text
        self.txt = txt

    def colorize(self):
        """Colorize text with markdown syntax"""
        if len(self.txt) == 1: return

        self.color_syntax()
        self.create_hlink()
        self.hide_syntax()

        # Configure tag color
        for tag_name in md_dic:
            self.tk_text.tag_config(tag_name, **md_dic[tag_name][1])
        self.tk_text.tag_config('link', foreground='blue')
        self.tk_text.tag_config('hide', elide=True)


    def color_syntax(self):
        """Color with regex"""
        r_stg = '|'.join(
            '(?P<%s>' % key + md_dic[key][0] + ')'
            for key in md_dic)
        txtfilter = re.compile(r_stg, re.MULTILINE)

        for i in txtfilter.finditer(self.txt):
            start = i.start()
            end = i.end() - 1

            # Get tag name (in ?P<h1>)
            group_dic = i.groupdict()
            tag_name = None
            for key, val in group_dic.items():
                if val is not None:
                    tag_name = key
                    break
            if tag_name is None: continue
            tag_txt = group_dic[tag_name].replace(' ', '-')
            tag_txt = re.sub('#+-', '', tag_txt)

            ind1, ind2 = _coordinate(start, end, self.txt)
            self.tk_text.tag_add(tag_txt, ind1, ind2)
            self.tk_text.tag_add(tag_name, ind1, ind2)


    def create_hlink(self):
        """Create internal hlink"""
        # pylint: disable = too-many-locals
        linkfilter = re.compile(r_link, re.MULTILINE)
        l_hide = []
        for i in linkfilter.finditer(self.txt):
            start = i.start()
            end = i.end() - 1
            # Text
            start_1 = start + 1
            end_1 = start + len(i.group(1))
            l_hide.append([start, start])
            # Link
            start_2 = end_1 + 4
            end_2 = end
            l_hide.append([end_1 + 1, end_2])

            link = i.group(2)
            link = re.sub('.*#', '', link)
            link = link.replace(' ', '-')
            tag_name = 'link_' + link
            try:
                link_index = self.tk_text.tag_ranges(link)[0]
            except:
                log(3, 'Link: could not find anchor for:', link)
                link_index = 0


            def jump_tag(_, index):
                if index == 0: return
                self.tk_text.yview(index)

            def show_xterm_cursor(_):
                self.tk_text.configure(cursor='xterm')

            def show_on_cursor(_):
                self.tk_text.configure(cursor='hand2')

            ind_1_s, ind_1_e = _coordinate(start_1, end_1, self.txt)
            self.tk_text.tag_add(tag_name, ind_1_s, ind_1_e)
            self.tk_text.tag_config(tag_name, foreground='#268bd2')  # blue
            self.tk_text.tag_bind(tag_name, "<Enter>", show_on_cursor)
            self.tk_text.tag_bind(tag_name, "<Leave>", show_xterm_cursor)
            self.tk_text.tag_bind(
                tag_name, '<Button-1>',
                lambda e, li=link_index: jump_tag(e, li))

            ind_2_s, ind_2_e = _coordinate(start_2, end_2, self.txt)
            self.tk_text.tag_add('link', ind_2_s, ind_2_e)

        # Hide
        for hide_1, hide_2 in l_hide:
            hide_s, hide_e = _coordinate(hide_1, hide_2, self.txt)
            self.tk_text.tag_add('hide', hide_s, hide_e)


    def hide_syntax(self):
        """Hide what need to be"""
        hidefilter = re.compile(r_elide, re.MULTILINE)
        for i in hidefilter.finditer(self.txt):
            start = i.start()
            end = i.end() - 1
            ind1, ind2 = _coordinate(start, end, self.txt)
            self.tk_text.tag_add('hide', ind1, ind2)


def _coordinate(start, end, string):
    """Get coordinate from stirng position index"""
    # Starting row
    srow = string[:start].count('\n') + 1
    scolsplitlines = string[:start].split('\n')
    if len(scolsplitlines) != 0:
        scolsplitlines = scolsplitlines[len(scolsplitlines) - 1]
    scol = len(scolsplitlines)  # Ending Column
    lrow = string[:end + 1].count('\n') + 1
    lcolsplitlines = string[:end].split('\n')
    if len(lcolsplitlines) != 0:
        lcolsplitlines = lcolsplitlines[len(lcolsplitlines) - 1]
    lcol = len(lcolsplitlines) + 1  # Ending Column
    return '{}.{}'.format(srow, scol), '{}.{}'.format(lrow, lcol)  # , (lrow, lcol)

"""
    Show fits header
"""

from tkinter import Tk, Frame, Scrollbar, Text, \
    Label, Button, Entry, \
    END, LEFT, RIGHT, BOTH, TOP, X, Y, INSERT


find_num = [0]
find_list = []
# Previous string
s_old = ''

def _find(text, edit):
    """Find string in header
    text Frame with text
    edit Entry
    """
    global s_old  # pylint: disable=global-statement
    text.tag_remove('found', '1.0', END)
    s_to_find = edit.get()
    if s_to_find:
        if s_to_find != s_old:  # reset
            find_num[0] = 0
            s_old = s_to_find
        idx = '1.0'
        while 1:
            idx = text.search(s_to_find, idx, nocase=1, stopindex=END)
            if not idx:
                break
            lastidx = '%s+%dc' % (idx, len(s_to_find))
            text.tag_add('found', idx, lastidx)
            find_list.append(idx)
            idx = lastidx
        text.tag_config('found', foreground='blue')
    edit.focus_set()

    return s_to_find


def Scroll(text, edit, side):
    """AutoScroll when user click + or -"""
    # Get
    s_to_find = _find(text, edit)

    # Check in
    if len(find_list) == 0:
        print("FitsHeaderWindow: Pattern '",
              s_to_find, "' not found in header")
        return
    if find_num[0] != 0:
        if side == "+":
            find_num[0] += 1
        if side == "-":
            find_num[0] -= 1
    lastidx = find_list[find_num[0]]
    idx = '%s+%dc' % (lastidx, len(s_to_find))
    text.see(lastidx)
    try:
        text.tag_remove('on', '1.0', END)
    except:
        pass
    text.tag_add("on", lastidx, idx)
    text.tag_config("on", foreground="red")
    if find_num[0] == 0:
        find_num[0] += 1
    return


def DisplayHeader(image_name, s_text):
    """Pop Window to display the header (helper)"""
    # Parent
    root = Tk()
    root.title('header('+image_name+')')
    root.geometry("600x700+0+0")

    # Head
    head_frame = Frame(root)
    head_frame.pack(side=TOP, fill=X)
    for i in range(4):
        head_frame.columnconfigure(i, weight=1)

    # Scrollbar
    scroll = Scrollbar(root)
    scroll.pack(side=RIGHT, fill=Y)

    # Text
    text = Text(root, background='white', fg="black")
    text.insert(INSERT, s_text)
    text.pack(side=LEFT, expand=True, fill=BOTH)
    text.configure(yscrollcommand=scroll.set)
    scroll.config(command=text.yview)

    # Label Find
    Label(head_frame, text='Find expression: ', bg="grey",
          fg="black").grid(row=0, column=0, sticky="nsew")

    # TextEntry search
    edit = Entry(head_frame, bg="white", fg="black")
    edit.bind("<Return>", lambda event: Scroll(text, exit, "+"))
    edit.grid(row=0, column=1, sticky="nsew")
    edit.focus_set()

    # - Previous
    Button(
        head_frame, text='<-', bg="grey",
        fg="black", command=lambda: Scroll(text, edit, "-")
        ).grid(row=0, column=2, sticky="nsew")

    # + Next
    Button(
        head_frame, text='->', bg="grey",
        fg="black", command=lambda: Scroll(text, edit, "+")
        ).grid(row=0, column=3, sticky="nsew")


    root.mainloop()

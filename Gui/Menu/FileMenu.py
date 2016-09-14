from Tkinter import *
from tkFileDialog import askopenfilename
import GuyVariables as G
import WorkVariables as W

import MyGui as MG


def FileMenu(args):                 # Open image, header...
    """
        args is a dictionnary containing the arguments to make all menuENtry
        identical, logical, responsible, pratical
    """
    G.menu = Menubutton(G.MenuBar, **args)
    G.menu.menu = Menu(G.menu, **G.submenu_args)

    G.menu.menu.add_command(label='Open', command=Open)
    G.menu.menu.add_command(label='Display Header', command=DisplayHeader)

    G.menu['menu'] = G.menu.menu
    return G.menu


def Open():
    """Open an imae file
    A click on this button will open a window.
    You need to select a FITS image to load with Abism.
    This is an other way to load an image, the first one is to load it
    directly in the script by bash Abism.sh [-i] image.fits.
    """

    initialdir = "/".join(  W.image_name.split("/")[: -1]   ) # the same dir as the image
    String = askopenfilename(title="Open a FITS image", filetypes=[("fitsfiles", "*.fits"), ("allfiles", "*")], initialdir=initialdir)


    if (type(String) is str or type(String) is unicode) and String != "" :
      if W.verbose>0 : print "Opening file : " + String
      W.image_name = String
      MG.InitImage()


    title=W.image_name.split('/')  # we cut the title
    G.parent.title('Abism (' + title[-1]+')')


    #drawing= G.ax1.imshow(W.Im0,vmin=G.min_cut,vmax=G.max_cut)
    #G.cbar.set_clim(vmin=G.min_cut,vmax=G.max_cut)
    #G.cbar.draw_all()
    #G.fig.canvas.draw()
    return


def DisplayHeader():   # for user
    """"A basic Window to display the header."""
    # parent
    root = Tk()
    root.title('header('+W.image_name+')')
    root.geometry("600x700+0+0")
    fram = Frame(root) # Left for txt + but
    fram.pack(side=LEFT, fill=BOTH, expand=True)
    fram2 = Frame(fram) # Left top
    fram2.pack(side=TOP, fill=X)

    # SCROLLBAR
    scroll=Scrollbar(root)
    scroll.pack(side=RIGHT, fill=Y)

    # CONFIGURE FIND
    def find():
        global find_list ; find_list = []
        global s ; global olds
        if not "olds" in globals() : olds=""
        text.tag_remove('found', '1.0', END)
        s = edit.get()
        if s:
            if s != olds : # reset
              find_num[0] = 0
              olds     =s
            idx = '1.0'
            while 1:
                idx = text.search(s, idx, nocase=1, stopindex=END)
                if not idx: break
                lastidx = '%s+%dc' % (idx, len(s))
                text.tag_add('found', idx, lastidx)
                find_list.append(idx)
                idx = lastidx
            text.tag_config('found', foreground='blue')
        edit.focus_set()

    find_num = [0]
    def Scroll(side):
        find()
        if len(find_list) == 0:
            if W.verbose > 0:
                print "Pattern '"+ s +  "' not found in header"
            return
        if find_num[0] != 0:
            if side == "+" : find_num[0] +=1
            if side == "-" : find_num[0] -=1
        lastidx      = find_list[find_num[0]]
        idx = '%s+%dc' % (lastidx, len(s))
        text.see(lastidx)
        try : text.tag_remove('on', '1.0', END)
        except : pass
        text.tag_add("on", lastidx, idx)
        text.tag_config("on", foreground = "red" )
        if find_num[0] == 0 : find_num[0] +=1
        return


    # search
    for i in range(4) : fram2.columnconfigure(i, weight=1)
    Label(fram2, text='Find expression: ', bg="grey", fg="black").grid(row=0, column=0, sticky="nsew")
    edit = Entry(fram2, bg="white", fg="black")
    edit.bind("<Return>", lambda event : Scroll("+")  )
    edit.grid(row=0, column=1, sticky="nsew")
    edit.focus_set()
    butt = Button(fram2, text='<-', bg="grey", fg="black", command=lambda : Scroll("-") )
    butt.grid(row=0, column=2, sticky="nsew")
    butt = Button(fram2, text='->', bg="grey", fg="black", command=lambda : Scroll("+") )
    butt.grid(row=0, column=3, sticky="nsew")

    # Text
    text=Text(fram, background='white', fg="black")   #, height=10, width=50
    text.insert(INSERT, W.head.flathead)
    text.pack(side=LEFT, expand=True, fill=BOTH)

    text.configure(yscrollcommand=scroll.set)
    scroll.config(command=text.yview)




    root.mainloop()
    return


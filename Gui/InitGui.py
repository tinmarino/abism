try : from Tkinter import *
except  : from tkinter import *
import tkFont
import re
import os.path          # For the Icon

import MyGui  as MG
import Pick # pick et pick et kolegram bour et bour et ratatam

import MenuBar

import GuyVariables as G
import WorkVariables as W


    ##################
    ## 0/ Main Caller
    #################

def WindowInit():
    Title()               # Set title and icon
    MainFrameMaker()      # Create MenuBar and MainPaned, TextFrame and DrawFrame
    Shortcuts()           # take MG and parents


def Title():  # Title, Icon, geometry
    ""
    # TITLE
    G.parent.title('ABISM ('+"/".join(str(W.image_name).split("/")[-3:])+')')
    ""  # Adaptative Background Interactive Strehl Meter')

    # ICON
    if os.path.isfile(W.path+'/Icon/bato_chico.gif'):
        bitmap = PhotoImage(file=W.path+'/Icon/bato_chico.gif')
        G.parent.tk.call('wm', 'iconphoto', G.parent._w, bitmap)
    else:
        if W.verbose > 3: print "->you have no beautiful icon because you didn't set the PATH in Abism.py "

    # GEOMETRY
    if "parent" in G.geo_dic:
        G.parent.geometry(G.geo_dic["parent"])


def MainFrameMaker():
    ""
    # 1 TOP
    MenuBar.MenuBarMaker()

    # ALL What is not the menu is a paned windows :
    # I can rezie it with the mouse from left to right,
    # This (all but not the Menu) Frame is called MainPaned
    G.MainPaned = PanedWindow(G.parent, orient=HORIZONTAL, **G.paned_dic)
    G.all_frame.append("G.MainPaned")
    G.MainPaned.pack(side=TOP, fill=BOTH, expand=1)

    # 2 LEFT
    TextFrameMaker()

    # 3 RIGHT
    DrawFrameMaker()

    return


def DrawFrameMaker():  # receive G.MainPaned, create DrawPaned
    """
    """
    # CREATE
    G.DrawPaned = PanedWindow(G.MainPaned, orient=VERTICAL, **G.paned_dic)
    G.all_frame.append("G.DrawPaned")

    # PACK, INCLUDE in MainPaned
    if "DrawPaned" in G.geo_dic:
        G.MainPaned.add(G.DrawPaned, width=float(G.geo_dic["DrawPaned"]))
    else: # including don't set width
        G.MainPaned.add(G.DrawPaned)


    # TOP : IMAGE FRAME, displaying the full image
    def Image():
        G.ImageFrame = Frame(G.DrawPaned, bg=G.bg[0])
        G.all_frame.append("G.ImageFrame")
        if "ImageFrame" in G.geo_dic:
            G.DrawPaned.add(G.ImageFrame,
                            height=float(G.geo_dic["ImageFrame"]))
        else:  # including don't set height
            G.DrawPaned.add(G.ImageFrame)
        G.all_frame.append("G.ImageFrame")

        return  # from Image


    # BOTTOM : 2 Frames
    def RightBottom():
        G.RightBottomPaned = PanedWindow(G.DrawPaned,
                                         orient=HORIZONTAL,
                                         **G.paned_dic)
        if "RightBottomPaned" in G.geo_dic:
            targ = {"height": float(G.geo_dic["RightBottomPaned"])}
        else:
            targ = {}

        G.DrawPaned.add(G.RightBottomPaned, **targ)
        G.all_frame.append("G.RightBottomPaned")

        return  # from RightBottom


    # BOTTOM DIVIDE and create the 2 FRAMES
    def RightBottomSub():
        # In RightBottomPaned 2 : FitFrame, ResultFrame (should be star frame)

        # LEFT of the bottom, the fit frame, to see in 1d the fit
        def Fit():
            G.FitFrame = Frame(G.RightBottomPaned, bg=G.bg[0])
            if "FitFrame" in G.geo_dic:
                targ = {"width": float(G.geo_dic["FitFrame"])}
            else:
                targ = {}
            G.RightBottomPaned.add(G.FitFrame, **targ)
            G.all_frame.append("G.FitFrame")


        # RIGHT of the bottom, the result, 2-2d images, to see fit in 2d
        def Result():
            G.ResultFrame = Frame(G.RightBottomPaned, bg=G.bg[0])
            if "ResultFrame" in G.geo_dic:
                targ = {"width": float(G.geo_dic["ResultFrame"])}
            else:
                targ = {}
            G.RightBottomPaned.add(G.ResultFrame, **targ)
            G.all_frame.append("G.ResultFrame")

        Fit()
        Result()
        return  # from RightBottomSub

    Image()
    RightBottom()
    RightBottomSub()
    return  # from DrawFrameMaker



def TextFrameMaker():
    """
    """
    # Main Frame create
    G.TextFrame = Frame(G.MainPaned, **G.fr_arg)
    G.all_frame.append("G.TextFrame")

    # Main Frame Add to its parent so it get displayed
    if "TextPaned" in G.geo_dic:
        G.MainPaned.add(G.TextFrame, width=float(G.geo_dic["TextPaned"]))
    else:  # including don't set width
        G.MainPaned.add(G.TextFrame)

    # BUTTONS
    TextButton1(G.TextFrame).pack(side=TOP, expand=0, fill=X)

    # PANED TODO remove the main text frame
    G.TextPaned = PanedWindow(G.TextFrame, orient=VERTICAL, **G.paned_dic)
    G.TextPaned.pack(side=TOP, expand=1, fill=BOTH)  # this is the main paned on the left so it should expand
    G.all_frame.append("G.TextPaned")

    LeftLabel()
    LeftTop()
    LeftResult()


def TextButton1(frame):
    ""
    # FRAMES
    G.ButtonFrame = Frame(frame, bg=G.bg[0])
    G.all_frame.append("G.Button1Frame")

    G.Button1Frame = Frame(G.ButtonFrame, **G.fr_arg)
    G.Button1Frame.pack(side=TOP, fill=X, expand=0)


    # DEFINE BUTTON
    G.bu_quit = Button(G.Button1Frame, text='QUIT',
                    background=G.bu_quit_color,
                    command=MG.Quit, **G.bu_arg)  # QUIT

    G.bu_restart = Button(G.Button1Frame, text='RESTART',
                    background=G.bu_restart_color,
                    command=MG.Restart, **G.bu_arg)  # RESTART

    G.bu_manual = Button(G.Button1Frame, text=u'\u25be '+'ImageParameters',
                    background=G.bu_manual_color,
                    command=ImageParameter, **G.bu_arg)  # MANUAL M

    # GRID ITS
    G.Button1Frame.columnconfigure(0, weight=1)
    G.Button1Frame.columnconfigure(1, weight=1)

    G.bu_quit.grid(row=0, column=0, sticky="nsew")
    G.bu_restart.grid(row=0, column=1, sticky="nsew")
    G.bu_manual.grid(row=1, column=0, columnspan=2, sticky="nsew")

    return G.ButtonFrame


def LeftLabel():  # LeftTipTopFrame
    G.LabelFrame0 = Frame(G.TextPaned, **G.fr_arg)
    G.all_frame.append("G.LabelFrame0")

    arg = G.sub_paned_arg
    if 'LabelFrame' in G.geo_dic:
        arg.update({"height": int(G.geo_dic["LabelFrame"])})
        if W.verbose > 3:
            print "I chose ",
            int(G.geo_dic["LabelFrame"]),
            " for height of LABEL FRAME"

    G.TextPaned.add(G.LabelFrame0, **arg)
    G.LabelFrame = Frame(G.LabelFrame0, **G.fr_arg)
    G.LabelFrame.pack(side=TOP, fill=BOTH, expand=0)


def LeftTop():  # call TxtButton1()
    G.LeftTopFrame = Frame(G.TextPaned, bg=G.bg[0])
    G.all_frame.append("G.LeftTopFrame")

    arg = G.sub_paned_arg
    if "LeftTopFrame" in G.geo_dic:
        arg.update({"height": int(G.geo_dic["LeftTopFrame"])})
        if W.verbose > 3 : print "I chose ", int(G.geo_dic["LeftTopFrame"]), " for height of LefTOPFRAME"

    G.TextPaned.add(G.LeftTopFrame, **arg)
    LeftTopArrow()


def LeftResult() :
    ""
    # LeftBottomFrame
    G.LeftBottomFrame = Frame(G.TextPaned, bg=G.bg[0])
    G.all_frame.append("G.LeftBottomFrame")

    arg = G.sub_paned_arg
    if "LeftBottomFrame" in G.geo_dic:
       arg.update({ "height":int(G.geo_dic["LeftBottomFrame"])  })
    G.TextPaned.add(G.LeftBottomFrame, **arg)

    # result Label
    G.ResultLabelFrame = Frame(G.LeftBottomFrame, bg=G.bg[0])
    G.all_frame.append("G.ResultLabelFrame")
    G.ResultLabelFrame.pack(side=TOP, fill=X)

    # RESULT LABEL [written 'result' and fit type at the top
    Label(G.ResultLabelFrame, text="Results", **G.frame_title_arg).pack(side=LEFT)
    G.fit_type_label = Label(G.ResultLabelFrame,
                             text=W.type["fit"],
                             justify=CENTER,
                             **G.lb_arg)
    G.fit_type_label.pack(fill=X)

    # ANSWER FRAME
    G.AnswerFrame = Frame(G.TextPaned, bg=G.bg[0])
    G.all_frame.append("G.AnswerFrame")
    G.AnswerFrame.pack(expand=0, fill=BOTH)

    # ARROW in RESULT LABEL
    # if G.result_bool :  # label is big
    if False:
        photo = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
    else:
        photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")

    G.result_frame_arrow = Button(G.LeftBottomFrame, command=ResultResize, image=photo, **G.bu_arg)
    G.result_frame_arrow.image = photo  # keep a reference
    G.result_frame_arrow.place(relx=1., rely=0., anchor="ne")



###
## TEXT ARROWS
####
def LabelDisplay(expand=False):  # called later, display what I retrived from header
    """ warning: exapnd not working well
      ESO /  not ESO
      NAco/vlt
      Reduced/raw
      Nx x Ny x Nz
      WCS detected or not
    """

    lst = []

    # ESO, COMPANY
    if W.head.company == "ESO":
        comp = "ESO"
    else:
        comp = "NOT ESO"


    # VLT/NACO INSTRUMENT
    if W.head.instrument == "NAOS+CONICA":
        ins = "NaCo"
    else:
        ins = W.head.instrument
    tel = re.sub("-U.",
                 "",
                 W.head.telescope.replace("ESO-", "")
    )  # to delete ESO-  and -U4
    lbl = comp + " / " + tel + " / " + ins
    lst.append((lbl,{}))


    # REDUCED ?
    if "reduced_type" in vars(W.head):
        lbl = W.head.reduced_type + ": "

    # SIZE : Nx * Ny * Nz
    shape = list(W.Im0.shape[::-1])  # reverse, inverse, list order
    if "NAXIS3" in W.head.header.keys():
        shape.append(W.head.header["NAXIS3"])
        lbl += "%i x %i x %i" % (shape[0], shape[1], shape[2])
    else:
        lbl += "%i x %i " % (shape[0], shape[1])
    lst.append((lbl,{}))


    #WCS
    if W.head.wcs_bool:
        lbl = "WCS detected"
    else:
        lbl = "WCS NOT detected"
    lst.append((lbl,{}))


    # Header reads Strehl variables ?
    bolt = (W.head.diameter == 99. or W.head.wavelength == 99.)
    bolt = bolt or (W.head.obstruction == 99. or W.head.pixel_scale == 99.)
    if bolt:
        lbl = "WARNING: some parameters not found"
        lst.append((lbl, {"fg": "red"}))
    else:
        lbl = "Parameters read from header"
        lst.append((lbl, {"fg": "blue"}))


    # UNDERSAMPLED
    bol1 = W.head.wavelength*1e-6
    bol1 /= W.head.diameter * (W.head.pixel_scale/206265)
    bol1 = bol1 < 2
    bol2 = "sinf_pixel_scale" in vars(W.head)
    # if bol2 sinf_pixel_scane is not in W.head, we dont call the next line
    bol3 = bol2 and W.head.sinf_pixel_scale == 0.025
    bol3 = bol3 or (bol2 and (W.head.sinf_pixel_scale == 0.01))

    bolt = bol1 or bol2
    if bolt:
        lbl = "!!! SPATIALLY UNDERSAMPLED !!!"
        lst.append((lbl, {"fg": "red"}))

    # GRID LABLES
    row = 0
    G.LabelFrame.columnconfigure(0, weight=1)
    if W.verbose > 0: print "Label lst" , lst
    for i in lst:
        arg = G.lb_arg.copy()
        arg.update({"justify": CENTER})
        if type(i) == list or type(i) == tuple:
            arg.update(i[1])
        i = i[0]
        Label(G.LabelFrame, text=i, **arg).grid(row=row, column=0, sticky="nsew")
        row += 1






    # place arrow to resize
    if G.label_bool:   # label is big
        photo = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
    else:
        photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")
    G.label_frame_arrow = Button(G.LabelFrame,
                                 command=LabelResize, image=photo, **G.bu_arg)
    G.label_frame_arrow.image = photo  # keep a reference
    G.label_frame_arrow.place(relx=1., rely=0., anchor="ne")


    # place frame_title_label
    Label(G.LabelFrame, text="Labels", **G.frame_title_arg).place(x=0, y=0)


    # Button to resize
    arg = G.bu_arg.copy()
    arg.update({"text": "OK",
                "command": LabelResize,
                "padx": 3,
                "width": 20
                })
    G.last_label = Button(G.LabelFrame, **arg)
    G.last_label.grid(row=row, column=0, sticky="nswe")
    row += 1

    if expand:
        G.label_bool = 0
        LabelResize()


def LabelResize():              # called  later, resize this area
    if G.label_bool:        # Show the label frame
        G.TextPaned.sash_place(0, 0, 22)
        photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")
        if W.verbose > 3: print "Resize Label: ", 22

    else:                   # collapse the label frame
        G.TextPaned.sash_place(0, 0, G.last_label.winfo_y() + G.last_label.winfo_height())
        photo = PhotoImage(file=W.path+"/Icon/arrow_up.gif")
        if W.verbose > 3: print "REsize Label: ",  G.last_label.winfo_y()+G.last_label.winfo_height()
    G.label_bool = not G.label_bool
    G.label_frame_arrow['image'] = photo
    G.label_frame_arrow.image = photo  # keep a reference

    return


def LeftTopArrow():  # jsut draw the arrow, see after
    """ this do not need to be on a function but if you want to place
        the arrow it will vanish when packing other frame. SO I packed the
        arrow, otherwhise you need to redraw it all the time
    """
    # PACK TEH FRAME
    G.LeftTopArrowFrame = Frame(G.LeftTopFrame, **G.fr_arg)
    G.LeftTopArrowFrame.pack(side=TOP, expand=0, fill=X)

    # Load ARROW IMAGE
    if G.top_bool:  # label is big
        photo = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
    else:
        photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")

    # Pach Arrow image as button
    G.top_frame_arrow = Button(G.LeftTopArrowFrame, command=TopResize, image=photo, **G.bu_arg)
    G.top_frame_arrow.image = photo  # keep a reference
    G.top_frame_arrow.pack(side=RIGHT, anchor="ne", expand=0)



def TopResize():        # called  later when clicking on toparrow
    if G.top_bool:
        photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")
        base = G.TextPaned.sash_coord(0)[1]  # jus height of the previous sash
        G.TextPaned.sash_place(1, 0, base + 22 + 2 * G.paned_dic["sashwidth"])
        if W.verbose > 3: print("Resize top: ", 22)
    else:
        photo = PhotoImage(file=W.path+"/Icon/arrow_up.gif")
        place = G.parent.winfo_height() - G.TextPaned.winfo_rooty() - 200
        G.TextPaned.sash_place(1, 0, place)

    G.top_bool = not G.top_bool
    G.top_frame_arrow['image'] = photo
    G.top_frame_arrow.image = photo  # keep a reference

    return



def ResultResize(how="max"):  # called  later
    # if not G.result_bool : # this is to expand
    if how == "max":  # resize max
        base = G.TextPaned.sash_coord(0)[1]  # jus height of the previous sash
        G.TextPaned.sash_place(1, 0, base + 22 + 2 * G.paned_dic["sashwidth"])
        if W.verbose > 3: print "REsize result: ", 22

    elif how == "full":  # see everything but not more
        def Pos():  # calculate position of the sash
            G.TextPaned.sash_place(1, 0, )  # to expand the widget, and estimate their size, no number is interpreted ad infinity
            corner2 = max ([i.winfo_rooty() for j in G.LeftBottomFrame.winfo_children() for i in j.winfo_children()])  # the max size
            base = G.LeftBottomFrame.winfo_rooty()  # top of the left bottom Frame
            size = corner2 - base                   # size fo the left Botttom Frame
            base_sash1 = G.LeftTopFrame.winfo_rooty()
            pos = G.parent.winfo_height() - size - base_sash1
            if W.verbose >3: print "Resize", corner2, total, "base1", base_sash1, size, base, pos

            return max(pos, 22)  # minimum 22 pixels

        pos = Pos()
        G.TextPaned.sash_place(1, 0, pos)
        if W.verbose > 3: print "REsize Top: ", pos

    return






    ######################
    ### 4/  MORE FRAMES if click on some buttons  #
    ######################



def TitleArrow(title,var):
    # TITEL
    if G.in_arrow_frame == None:
       G.arrtitle = Label(G.LeftTopArrowFrame,text=title,**G.frame_title_arg)
       G.arrtitle.pack(side=LEFT,anchor="nw")
       G.in_arrow_frame = var
       return True
    else  : return False


def ImageParameter():
  if G.tutorial:
               text="To measure the Strehl ratio I really need :\n"
               text+="-> Diameter of the telescope [in meters]\n"
               text+="-> Obstruction of the telescope [ in % of the area obstructed ]\n"
               text+="-> Wavelenght [ in micro meter ], the central wavelength of the band\n"
               text+="-> Pixel_scale [ in arcsec per pixel ]\n"
               text+="All the above parameters are used to get the diffraction pattern of the telescope because the peak of the PSF will be divided by the maximum of the diffraction patter WITH the same photometry to get the strehl.\n\n"
               text+="Put the corresponding values in the entry widgets. Then, to save the values, press enter i, ONE of the entry widget or click on ImageParamter button again.\n"
               text+="Note that these parameters should be readden from your image header. If it is not the case, you can send me an email or modify ReadHeader.py module."
               MG.TutorialReturn({"title":"Image Parameters",
               "text":text
               })
               return


  G.image_parameter_list = [  ["Wavelength"+"*"+ " ["+u'\u03BC'+"m]:", "wavelength",99.] ,
	   ["Pixel scale" + "*"+ " [''/pix]: ","pixel_scale",99.],
           ["Diameter" +"*"+" [m]:","diameter",99.],
	   ["Obstruction (d2/d1)*" +  " [%]:","obstruction",99.],
	   ["Zero point [mag]: ","zpt",0.],
	   ["Exposure time [sec]: ","exptime",1.],
	   ]  # Label, variable , default value

  ##########
  # INITIATE THE FRAME, change button color
  if G.bu_manual["background"]==G.bu_manual_color:
    G.ManualFrame = Frame(G.LeftTopFrame,bg=G.bg[0]) ###
    G.all_frame.append("G.ManualFrame")
    G.ManualFrame.pack(expand=0,fill=BOTH,side=TOP) # to keep other guys upside
    # TITEL
    Label(G.ManualFrame,text="Parameters",**G.frame_title_arg).pack(side=TOP,anchor="w")
    G.ManualGridFrame=Frame(G.ManualFrame)
    G.ManualGridFrame.pack(expand=0,fill=BOTH,side=TOP)
    G.ManualGridFrame.columnconfigure(0,weight=1)
    G.ManualGridFrame.columnconfigure(1,weight=1)

    ###################
    # THE ENTRIES (it is before the main dish )
    row=0
    for i in G.image_parameter_list :
      l=Label(G.ManualGridFrame,text=i[0],font=G.font_param,justify=LEFT,anchor="nw",**G.lb_arg)
      l.grid(row=row,column=0,sticky="NSEW")
      vars(G.tkvar)[i[1]] = StringVar()
      vars(G.tkentry)[i[1]] =Entry(G.ManualGridFrame, width=10,textvariable=vars(G.tkvar)[i[1]],font=G.font_param,**G.en_arg)
      if vars(W.head)[i[1]] == i[2] :
        vars(G.tkentry)[i[1]]["bg"]="#ff9090"
      vars(G.tkentry)[i[1]].grid(row=row,column=1,sticky="NSEW")
      vars(G.tkentry)[i[1]].bind('<Return>',GetValueIP)
      if len(str(  vars(W.head)[i[1]]      )) > 6  : # not to long for display
        vars(G.tkvar)[i[1]].set(  "%.5f"% float(  vars(W.head)[i[1]]  )   )
      else :
        vars(G.tkvar)[i[1]].set(vars(W.head)[i[1]])
      row+=1


    G.bu_manual["background"]='green'
    G.bu_manual["text"]= u'\u25b4 '+'ImageParameters'

    # EXPAND
    G.top_bool = 0
    TopResize()
    return


  elif G.bu_manual["background"]=='green':  #destroy manualFrame  and save datas
    GetValueIP("") # because receive event
    G.ManualFrame.destroy()
    del G.ManualFrame
    if G.in_arrow_frame == "param_title" :
       G.arrtitle.destroy()
       G.in_arrow_frame = None
    G.all_frame = [ x for x in G.all_frame if x!="G.ManualFrame" ] # remove MoreFrame
    G.bu_manual["background"]=G.bu_manual_color
    G.bu_manual["text"]=u'\u25be '+'ImageParameters'
    return
  return



def GetValueIP(event, destroy=True): # ImageParameter
    for i in G.image_parameter_list:
        vars(W.head)[i[1]] = float(vars(G.tkentry)[i[1]].get())
        # COLOR
        if vars(W.head)[i[1]] == i[2]:
            vars(G.tkentry)[i[1]]["bg"] = "#ff9090"
        else:
            vars(G.tkentry)[i[1]]["bg"] = "#ffffff"
        ResetLabel(expand=False)



def Cube():
      if not W.cube_bool:
        try : G.CubeFrame.destroy()
	except : pass
      else :
        # FRAME
	G.CubeFrame = Frame(G.ButtonFrame,**G.fr_arg )
	G.CubeFrame.pack(side=TOP,expand=0,fill=X)

            # CUBE IMAGE SELECTION
        # LEFT
	G.bu_cubel=Button(G.CubeFrame,text = '<-',command=lambda:MG.CubeDisplay("-"),**G.bu_arg)

        # ENTRY
	G.cube_var = StringVar()
	G.cube_entry = Entry(G.CubeFrame, width=10,justify=CENTER,textvariable=G.cube_var,**G.en_arg)
	G.cube_var.set(W.cube_num+1)
	G.cube_entry.bind("<Return>",lambda x:MG.CubeDisplay("0"))

        # RIGHT
	G.bu_cuber=Button(G.CubeFrame,text = '->',command=lambda:MG.CubeDisplay("+"),**G.bu_arg)

        # GRID
	for i in range(3) : G.CubeFrame.columnconfigure(i,weight=1)
        Label(G.CubeFrame,text="Cube Number",**G.frame_title_arg).grid(row=0,column=0,columnspan=3,sticky="w")
	G.bu_cubel.grid(row=1,column=0,sticky="nsew")
	G.cube_entry.grid(row=1,column=1,sticky="nsew")
	G.bu_cuber.grid(row=1,column=2,sticky="nsew")

      #W.cube_bool = not W.cube_bool
      # we change cube bool in init image
      return


def ManualBackground():
  if G.manual_back_bool :
    ManualBackClose()

  else : # including no manula_back_bool
    W.type["noise"]= "manual"
    G.manual_back_bool = not G.manual_back_bool
    G.ManualBackFrame=Frame(G.LeftTopFrame,bg=G.bg[0])
    G.all_frame.append("G.ManualBackFrame")
    G.ManualBackFrame.pack(side=TOP,expand=0,fill=X)

    G.ManualBackFrame.columnconfigure(0,weight=1)
    G.ManualBackFrame.columnconfigure(1,weight=1)

    def GetValue(event):
      G.background = float( G.tkvar.background.get() )
      if W.verbose >2 : print "InitGui.py/ManualBack, called , ",G.background


    # ENTRY
    Label(G.ManualBackFrame,text="Background value:",font=G.font_param,**G.lb_arg).grid(row=0,column=0,sticky="snew")
    G.tkvar.background= StringVar()
    G.tkentry.background=Entry(G.ManualBackFrame, width=10,textvariable=G.tkvar.background,font=G.font_param,**G.en_arg)
    G.tkentry.background.grid(row=0,column=1,sticky="nsew")#,sticky=W)
    G.tkentry.background.bind('<Return>',GetValue)
    G.tkvar.background.set("0.0")
    if "background" in vars(G) : G.tkvar.background.set(str(G.background))


    ###############
    ##  CLOSE button
    G.bu_back_close=Button(G.ManualBackFrame,text=u'\u25b4 '+'Close',background=G.bu_close_color,command=ManualBackClose,**G.bu_arg)
    G.bu_back_close.grid(row=1,column=0,columnspan=2)
    if W.verbose >3 : print "Manual Back called"


def ManualBackClose():
  G.manual_back_bool = not G.manual_back_bool
  G.ManualBackFrame.destroy()
  G.all_frame = [ x for x in G.all_frame if x!="G.ManualBackFrame" ] # remove Frame

  G.background = float( G.tkvar.background.get() )





        ###########
        #  MISCELLANEOUS
        ###########


def ResetLabel(expand=False):
  G.LabelFrame.destroy()
  G.LabelFrame = Frame(G.LabelFrame0,**G.fr_arg) ###
  G.LabelFrame.pack(side=TOP,fill=BOTH,expand=0)
  LabelDisplay(expand=expand)




          ############
	  ## APPEARANCES
	  ###########


def PanedConfig(arg): # change paned window canvas...
  for i in G.all_frame :
    if "Paned" in i :
       if W.verbose >3 : print "I change ",i
       for j in arg :
          vars(G)[i[2:]][j] = arg[j]
  return






def callback(event):
    if W.verbose > 3: print "clicked at",
    event.x,
    event.y,
    event.widget,
    event.key


def TerminalWidget(Frame): # not used
  import os
  wid = Frame.winfo_id()
  #G.c=Button(G.TerminalFrame,text='CLEAR',background= 'cyan',
  #                command =MG.Clear)                    # CLEAR
  #G.c.pack(side=BOTTOM,expand=0,fill=X)
  #os.system('xterm -into %d -geometry 100x150 -sb -e "tty; sh" &' % wid)
  os.system('xterm -into %d -geometry 40x20 &' % wid)



def Shortcuts() :
  #Shortcut, module, function, [  args, kargs  ]
  lst = [["<Control-o>","MG","Open"],
         ["<Control-q>","MG","Quit"],
         ["<Control-r>","MG","Restart"],
	]


  for i in lst :
     G.parent.bind_all(    i[0] ,   lambda i=i : vars(i[1])[i[2]]()  )






def ManualCut():
  if G.manual_cut_bool :
    ManualCutClose()

  else : # including no manula_cut_bool
    G.top_resize = 1
    TopResize()
    G.top_resize = 0
    TopResize()
    G.manual_cut_bool = not G.manual_cut_bool
    G.ManualCutFrame=Frame(G.LeftTopFrame, bg=G.bg[0])
    G.all_frame.append("G.ManualCutFrame")
    G.ManualCutFrame.pack(side=TOP, expand=0, fill=X)

    Label(G.ManualCutFrame, text="Cut image scale", **G.frame_title_arg).pack(side=TOP, anchor="w")

    G.ManualCutGridFrame=Frame(G.ManualCutFrame, bg=G.bg[0])
    G.all_frame.append("G.ManualCutGridFrame")
    G.ManualCutGridFrame.pack(side=TOP, expand=0, fill=X)

    G.ManualCutGridFrame.columnconfigure(0, weight=1)
    G.ManualCutGridFrame.columnconfigure(1, weight=1)

    def GetValue(event):
      dic = {"min_cut":float(G.entries[1].get()),
             "max_cut":float(G.entries[0].get())}
      if W.verbose >2 : print "InitGui.py/ManualCut, dic called , ", dic
      MG.Scale(dic=dic) # Call MyGui


    lst = [  ["Max cut", "max_cut"],  ["Min cut", "min_cut"]  ]
    G.entries=[]
    r=0
    for i in lst :
      G.l=Label(G.ManualCutGridFrame, text=i[0], font=G.font_param, **G.lb_arg)
      G.l.grid(row=r, column=0, sticky="snew")#, sticky=W)
      v= StringVar()
      G.e=Entry(G.ManualCutGridFrame, width=10, textvariable=v, font=G.font_param, **G.en_arg)
      G.e.grid(row=r, column=1, sticky="nsew")#, sticky=W)
      G.e.bind('<Return>', GetValue)
      v.set("%.1f"%G.scale_dic[0][i[1]])
      G.entries.append(v)
      r+=1


    ###############
    ##  CLOSE button
    G.bu_close=Button(G.ManualCutGridFrame, text=u'\u25b4 '+'Close', background=G.bu_close_color, command=ManualCutClose, **G.bu_arg)
    G.bu_close.grid(row=r, column=0, columnspan=2)
    if W.verbose >3 : print "Manual Cut called"





def ManualCutClose():

  G.manual_cut_bool = not G.manual_cut_bool
  G.ManualCutFrame.destroy()
  G.all_frame = [ x for x in G.all_frame if x!="G.ManualCutFrame" ] # remove Frame

  G.scale_dic[0]["max_cut"] =float(G.entries[0].get())
  G.scale_dic[0]["min_cut"] =float(G.entries[1].get())
  if W.verbose > 3 : print  G.scale_dic[0]["min_cut"]
  if W.verbose > 3 : print  G.scale_dic[0]["max_cut"]
  MG.Scale()




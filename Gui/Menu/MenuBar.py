from Tkinter import *

import FileMenu
import AbismMenu
import AnalysisMenu

import GuyVariables as G
import WorkVariables as W

import MyGui as MG # TODO remove that
import InitGui as IG

import LaunchCalculator

def MenuBarMaker():             # CALLER
    global args                 # the args of "MenuButton"

    G.MenuBar = Frame(G.parent, bg=G.bg[0])
    G.all_frame.append("G.MenuBar")
    G.MenuBar.pack(side=TOP, expand = 0 , fill = X )

    col=0
    args = G.me_arg.copy()
    args.update (  {"relief":FLAT, "width":G.menu_button_width }  )
    for i in [
        [AbismMenu.AbismMenu, {"text":u"\u25be "+"ABISM"}           ],
        [FileMenu.FileMenu, {"text":u"\u25be "+"File"}  ] ,
        [AnalysisMenu.AnalysisMenu,  {"text":u'\u25be '+'Analysis'} ] ,
        [ViewMenu,  {"text":u'\u25be '+'View'} ],
        [ToolMenu,  {"text":u'\u25be '+'Tools'} ],
    ] :
        args.update( i[1] )
        button = i[0](args)
        G.MenuBar.columnconfigure(col, weight=1)
        button.grid(row=0, column=col, sticky="nsew")

        col+=1


def ToolMenu(args):
    G.tool_menu=Menubutton(G.MenuBar, **args)
    G.tool_menu.menu=Menu(G.tool_menu, **G.submenu_args)

    lst = [
       ["Profile"   ,  lambda : Pick.RefreshPick("profile") ],
       ["Stat"      ,  lambda : Pick.RefreshPick("stat") ],
       [ "Histogram", MG.Histopopo ],
       [ "Python Console", MG.PythonConsole ],
       [ u'\u25be '+'Calculator', LaunchCalculator.Calculator],
       ]
    for i in lst :
      G.tool_menu.menu.add_command(label= i[0], command = i[1] )


    G.tool_menu['menu'] = G.tool_menu.menu
    return G.tool_menu


def ViewMenu(args):
    G.scale_menu=Menubutton(G.MenuBar, **args)
    G.scale_menu.menu=Menu(G.scale_menu, **G.submenu_args)


    ###############"
    ## COLOR
    def Color() :
        if G.scale_menu_type== "cascade" :
          color_menu = Menu(G.scale_menu, **G.submenu_args)
        else :
          color_menu = G.scale_menu.menu
	color_menu.add_command(label="COLOR", bg=None, state=DISABLED)
           # if we don't want cascade, we just add in the menu

        G.cu_color=StringVar(); G.cu_color.set(G.scale_dic[0]["cmap"]) # because image not loaded yet



        ###########"
        # My colors
        lst = [
                 ["Jet", "jet"],
                 ['Black&White', 'bone'],
          ['Spectral', 'spectral'],
          ["RdYlBu", "RdYlBu"],
          ["BuPu", "BuPu"]
       ]
        for i in lst :
          color_menu.add_radiobutton(label=i[0],
            command=lambda i=i: MG.Scale(dic={"cmap":i[1]}, run="G.cu_cut.set('"+i[1] +"')"   ),
            variable=G.cu_color, value=i[1]) # we use same value as label


        ########
        # Contour
        color_menu.add_command(label='Contour',
            command=lambda  : MG.Scale(dic={"contour":'not a bool'}  )
     )


        #################
        # more colors
        more_color_menu = Menu(color_menu, **G.submenu_args)
        num=0
        for i in G.all_cmaps :
            num+=1
            more_color_menu.add_radiobutton(label=i,
              command=lambda i=i: MG.Scale(dic={"cmap":i}),
              variable=G.cu_color, value=i) # we use same value as label

            if num%30==0  :

              more_color_menu.add_radiobutton(label=i,
                command=lambda i=i : MG.Scale(dic={"cmap":i}),
                variable=G.cu_color, value=i, columnbreak=1) # we use same value as label
        color_menu.add_cascade(menu=more_color_menu, label="More colors", underline=0)



        if G.scale_menu_type== "cascade" :
           G.scale_menu.menu.add_cascade(menu=color_menu, underline=0, label="Color")
        else :
           G.scale_menu.menu.add_command(columnbreak=1)


    ##############
    ###" SCALE FUNCTION
    def Scale():
        if G.scale_menu_type== "cascade" : scale_menu = Menu(G.scale_menu, **G.submenu_args)
        else :
          scale_menu = G.scale_menu.menu
	scale_menu.add_command(label="FCT", bg=None, state=DISABLED)

        G.cu_scale=StringVar(); G.cu_scale.set(G.scale_dic[0]["stretch"])
        lst = [  ["Lin", "x", "linear"], ["Sqrt", "x**0.5", "sqrt"], ["Square", "x**2", "square"], ["Log", "np.log(x+1)/0.69", "log"], ["Arcsinh", "", "arcsinh" ]   ]
        for i in lst :
          scale_menu.add_radiobutton(label=i[0]   ,
            command=lambda i=i : MG.Scale( dic={"fct":i[1], "stretch":i[2]}, run="G.cu_scale.set('"+ i[2] +"')" ) ,
            variable=G.cu_scale, value=i[2]) # we use same value as label


        if G.scale_menu_type== "cascade" :
           G.scale_menu.menu.add_cascade(menu=scale_menu, underline=0, label="Fct")
        else :
           G.scale_menu.menu.add_command(columnbreak=1)

    #G.bu_scale['menu'] = G.bu_scale.menu
    #G.bu_scale.bind("<Button-1>", lambda event : MG.Scale(dic={"tutorial":1, "fct":"truc"}) )


    ##############
    ##  CUT TYPE
    def Cut() :
        if G.scale_menu_type== "cascade" : cut_menu = Menu(G.scale_menu, **G.submenu_args)
        else :
          cut_menu = G.scale_menu.menu
	cut_menu.add_command(label="CUTS", bg=None, state=DISABLED)

        G.cu_cut=StringVar(); G.cu_cut.set("RMS")
        # label , scale_cut_type, key, value
        lst = [  ["RMS", "sigma_clip", "sigma", 3], ["99.95%", "percent", "percent", 99.95],
                 ["99.9%", "percent", "percent", 99.9], ["99.5%", "percent", "percent", 99.5],
                 ["99%", "percent", "percent", 99.], ["90%", "percent", "percent", 90],
                 ["None", "None", "truc", "truc"] ,
          #["Manual", "manual", "truc", "truc"] ,  ]
          ]
        for i in lst :
          cut_menu.add_radiobutton(label=i[0],
            command=lambda i=i : MG.Scale(dic={"scale_cut_type":i[1], i[2]:i[3]}, run="G.cu_cut.set('"+i[0] +"')"  ),
            variable=G.cu_cut, value=i[0]) # we use same value as label

        cut_menu.add_radiobutton(label="Manual",
            command= ManualCut,
            variable=G.cu_cut, value="Manual") # we use same value as label

        if G.scale_menu_type== "cascade" :
           G.scale_menu.menu.add_cascade(menu=cut_menu, underline=0, label="Cut")
        else :
           G.scale_menu.menu.add_command(columnbreak=1)

    #G.bu_cut['menu'] = G.bu_cut.menu
    #G.bu_cut.bind("<Button-1>", lambda event : MG.Scale(dic={"tutorial":1, "scale_cut_type":"truc"}) )

    Color()
    Scale()
    Cut()
    G.scale_menu['menu'] = G.scale_menu.menu

    return G.scale_menu


def MoreWidget():       # More photometry options frame
    ""

    # Change  menu label more option -> less option
    for i in range(1, 10) :
         j = G.analysis_menu.menu.entrycget(i, "label")
         if "Option" in j:
           if G.more_bool : G.analysis_menu.menu.entryconfig(i, label=u'\u25be '+'More Option')
           else           :  G.analysis_menu.menu.entryconfig(i, label=u'\u25b4 '+'Less Option' )
           break

    # CHANGE BOOL MAY CLOSE
    if G.more_bool ==1 : # close more frame
      MoreClose()

    else :  # CREATE
      G.more_bool = not G.more_bool # mean = 1
      G.top_bool = 0
      IG.TopResize()


      ##########""
      # FRAME
      G.MoreFrame = Frame(G.LeftTopFrame, bg=G.bg[0])  #create the more_staff Frame
      G.all_frame.append("G.MoreFrame")
      G.MoreFrame.pack(side=TOP, expand=0, fill=X)

      Label(G.MoreFrame, text="More Options", **G.frame_title_arg).pack(side=TOP, anchor="w")

      G.MoreGridFrame = Frame(G.MoreFrame, bg=G.bg[0])  #create the more_staff Frame
      G.all_frame.append("G.MoreGridFrame")
      G.MoreGridFrame.pack(side=TOP, expand=0, fill=X)
      G.MoreGridFrame.columnconfigure(0, weight=1)
      G.MoreGridFrame.columnconfigure(1, weight=1)



      def SubtractBackground(frame) :
        G.bu_subtract_bg=Button(frame, text='SubstractBackground',
                        background=G.bu_subtract_bg_color, command=MG.SubstractBackground, **G.bu_arg)
        return G.bu_subtract_bg



      def NoiseType(frame) :
        G.menu_noise=Menubutton(frame, text=u'\u25be '+'Background', relief=RAISED, background=G.menu_noise_color, **G.bu_arg)
        G.menu_noise.menu=Menu(G.menu_noise)

        G.cu_noise=StringVar(); G.cu_noise.set(W.type["noise"])
        lst = [
                ["Annulus", "elliptical_annulus" ],
                ['Fit', 'fit'] ,
                ["8Rects", "8rects"]  ,
            ['Manual', "manual" ],
                ["None", "None"],
            ]
             #  ["InRectangle", "in_rectangle" ] ,
        for i in lst :
          if i[0] == "Manual" :
            G.menu_noise.menu.add_radiobutton(label=i[0]   ,
              command=ManualBackground,
              variable=G.cu_noise, value=i[1]) # W.type[noise] as value
          else :
            G.menu_noise.menu.add_radiobutton(label=i[0]   ,
              command=lambda i=i : MG.VarSet('W.type["noise"]', i[1]) ,
              variable=G.cu_noise, value=i[1])

        G.menu_noise['menu'] = G.menu_noise.menu
        return G.menu_noise


      def PhotType(frame)  :
          G.menu_phot=Menubutton(frame, text=u'\u25be '+'Photometry', relief=RAISED, background=G.menu_phot_color, **G.bu_arg)
          G.menu_phot.menu=Menu(G.menu_phot)

          G.cu_phot=StringVar(); G.cu_phot.set(W.type["phot"])
          lst =  [
      	  ["Elliptical Aperture", "elliptical_aperture"] ,
                [ 'Fit', 'fit'],
      	  ['Rectangle Aperture', 'encircled_energy'],
      	  ['Manual', 'manual'],
      	  ]
          for i in lst :
            G.menu_phot.menu.add_radiobutton(label=i[0]   ,
              command=lambda i=i : MG.VarSet('W.type["phot"]', i[1]) ,
              variable=G.cu_phot, value=i[1]) # we use W.type[phot"]

          G.menu_phot['menu'] = G.menu_phot.menu
      return G.menu_phot


      def Check(frame) :
          myargs = { "anchor":"w", "bg":G.bg[0], "fg":G.fg[0], "padx":0 ,  "pady":0 ,"highlightthickness":0 }
          ################
          # isoplanetism
          G.iso_check = Checkbutton(frame,
             text="Anisomorphism", variable=W.aniso_var,
                 command=lambda :MG.FitType(W.type["fit"]), **myargs) # by default onvalue=1

          G.same_check = Checkbutton(G.MoreGridFrame,
            text="Binary_same_psf", variable=W.same_psf_var,
                command = lambda : MG.FitType(W.type["fit"]), **myargs)

          G.same_center_check = Checkbutton(G.MoreGridFrame,
            text="Saturated_same_center", variable=W.same_center_var,
                command= lambda: MG.FitType(W.type["fit"]), **myargs)

      return G.iso_check, G.same_check, G.same_center_check


      SubtractBackground(G.MoreGridFrame).grid(row=0, column=0, columnspan = 2, sticky="nswe")
      NoiseType(G.MoreGridFrame).grid(row=1, column=0, sticky="nswe")
      PhotType(G.MoreGridFrame).grid(row=1, column=1, sticky="nswe" )
      row=2
      for i in Check(G.MoreGridFrame) :
        i.grid(row = row, column=0, columnspan = 2 ,sticky="nwse")
        row+=1

      G.bu_close=Button(G.MoreGridFrame, text=u'\u25b4 '+'Close', background=G.bu_close_color, command=MoreClose, **G.bu_arg)
      G.bu_close.grid(row=row, column=0, columnspan=2)


def MoreClose():
    ""
    # change bool destroy
    G.more_bool = not G.more_bool
    G.MoreFrame.destroy()
    if G.in_arrow_frame == "title_more":
        G.arrtitle.destroy()
    G.in_arrow_frame = None

    # REMOVE MOREFRAME AND CHILD
    G.all_frame = [x for x in G.all_frame if x != "G.MoreFrame"]

    # Change help menu label
    for i in range(1, 10):
        j = G.analysis_menu.menu.entrycget(i, "label")
        if "Option" in j:
            G.analysis_menu.menu.entryconfig(i, label=u'\u25be '+'More Option')
            break


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

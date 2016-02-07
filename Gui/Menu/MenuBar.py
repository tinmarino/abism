from Tkinter import *

import FileMenu
import GuyVariables as G
import WorkVariables as W

import MyGui as MG # TODO remove that

import LaunchCalculator

def MenuBarMaker():             # CALLER
    global args                 # the args of "MenuButton"

    G.MenuBar = Frame(G.parent,bg=G.bg[0])
    G.all_frame.append("G.MenuBar")
    G.MenuBar.pack(side=TOP, expand = 0 , fill = X )

    col=0
    args = G.me_arg.copy()
    args.update (  {"relief":FLAT, "width":G.menu_button_width }  )
    for i in [
        ["AbismMenu", {"text":u"\u25be "+"ABISM"}           ],
        ["1", {"text":u"\u25be "+"File"}  ] ,
        ["AnalysisMenu",  {"text":u'\u25be '+'Analysis'} ] ,
        ["ViewMenu",  {"text":u'\u25be '+'View'} ],
        ["ToolMenu",  {"text":u'\u25be '+'Tools'} ],
    ] :
        args.update( i[1] )
        if (i[0]=="1"):
            button = FileMenu.FileMenu(args)
        else :
            button = globals()[i[0]]() # the actual CALL
        G.MenuBar.columnconfigure(col,weight=1)
        button.grid(row=0,column=col,sticky="nsew")

        col+=1


def AbismMenu():                # Menu entry to configure ABSIM
    G.abism_menu=Menubutton(G.MenuBar,**args)
    G.abism_menu.menu=Menu(G.abism_menu,**G.submenu_args)

    # BACKGROUND FOREGROUND
    def AppearanceMenu(parent_menu,who="bg",label="Background") :
      def CrazyColor(who="bg") :
         import color_interactive
         tmp = ( lambda x, who=who : BgCl(color=x,who=who )   )
         color_interactive.Main( func = tmp   )

      appearance_menu= Menu(parent_menu)

      vars(G)["cu_appearance_"+who]=StringVar(); vars(G)["cu_appearance_"+who].set( vars(G)[who][0])
      lst =[["White","#ffffff"],["Grey1","#d0d0d0"] ,
            ["Grey2","#b0b0b0"],["Black","#000000"],
            "\n",
            ["Red","#ff7070"], ["Blue","#b4a6ff"],
     ["Green","#69ff4d"],["DarkGeen","#0a280d"],
     "\n",
     ["Yellow","#ffff73"],
     ["Cyan","#8cffff"],["Purple","#cc55ff"],
    	  ]
      for i in lst :
          if i == "\n" :
            appearance_menu.add_command(columnbreak=1)
          else :
            appearance_menu.add_radiobutton(
    	    label=i[0],
    	    command= lambda i=i : BgCl(color=i[1],who=who)  ,
    	    variable = vars(G)["cu_appearance_"+who], value = i[1]  ,
    	    )

      appearance_menu.add_command(
                label="More",
    	    command=lambda who=who : CrazyColor(who=who) ,
    	    )


      parent_menu.add_cascade(menu=appearance_menu,label=label,underline=0)
      return


    # PANED
    def PanedConfigMenu(parent_menu,label=""):
      pconfig_menu= Menu(parent_menu)

      # SAS COLOR
      def CrazyColor() :
         import color_interactive
         tmp = lambda x : PanedConfig( {"bg":x} )
         color_interactive.Main( func = tmp )


      G.cu_p1=StringVar(); G.cu_p1.set(G.paned_dic["sashwidth"])
      G.cu_p2=StringVar(); G.cu_p2.set(G.paned_dic["sashrelief"])
      G.cu_p3=StringVar(); G.cu_p3.set(G.paned_dic["bg"])


      lst1 =[
            ["lbl" , "WIDTH"],
     [str(0),0] , [str(2),2] , [str(4),4] , [str(6),6] ,
     "\n",
     ]


      lst2= [
            ["lbl" , "COLOR" ],
            ["White","#ffffff"],["Grey1","#d0d0d0"] ,
            ["Grey2","#b0b0b0"],["Black","#000000"],
            "\n",
            ["Red","#ff7070"], ["Blue","#b4a6ff"],
     ["Green","#69ff4d"],["DarkGeen","#0a280d"],
     "\n",
     ["Yellow","#ffff73"],
     ["Cyan","#8cffff"],["Purple","#cc55ff"],
     ["More", "uselefsss" ],
    	  ]

      lst3= [
            ["lbl"    , "relief" ],
     ["FLAT"   , "flat"   ],
     ["RAISED" , "raised" ],
     ["SUNKEN" , "sunken" ],
     ["GROOVE" , "groove" ],
     ["RIDGE " , "ridge"  ],
     "\n",
     ]

      for j in [  [1,"sashwidth"] , [3,"sashrelief"]  , [2,"bg"] ] :
        for i in locals()["lst"+str(j[0])] :
            k = (i,j)
            if i == "\n" :
                pconfig_menu.add_command(columnbreak=1)
            elif i[0] == "lbl" :
                pconfig_menu.add_command(label=i[1],bg=None,state=DISABLED)

            elif "More" in str(i[0]) :
              pconfig_menu.add_command( label="More color",command=  CrazyColor )
            else :
              pconfig_menu.add_radiobutton(
      	    label=i[0],
      	    command= lambda k=k : PanedConfig({k[1][1]:k[0][1]})  ,# k=(i,j)
      	    variable = vars(G)[ "cu_p" + str(j[0]) ], value = i[1]  ,
      	    )



      parent_menu.add_cascade(menu=pconfig_menu,label=label,underline=0)
      return


    def AppearanceMenu1():  # MORE
      more_menu = Menu(G.abism_menu,**G.submenu_args)

      more_lst = [
     [ "Color", lambda : AppearanceMenu(more_menu,who="bg",label="Background Color")   ],  # background color
     [ "Color", lambda : AppearanceMenu(more_menu,who="fg",label="Foreground Color")   ],  # foreground color
     [ "Color", lambda : PanedConfigMenu(more_menu,label="Config Sash") ],
     ]
      for i in more_lst :
          i[1]()
      G.abism_menu.menu.add_cascade(menu=more_menu,label="Appearance",underline=0)
      return




    lst = [
            [ "About ABISM", MG.AboutAbism ],
     [ "Quick Guide", lambda : MG.See(pdf="quick_guide.pdf") ],
     [ "Advanced Manual", lambda : MG.See(pdf="advanced_manual.pdf") ],
            [ "Appearance", AppearanceMenu1  ],
     [ "Quit", MG.Quit  ],
     ]
    for i in lst :
        if "Appearance" in i[0] :
           i[1]()
        else :
           G.abism_menu.menu.add_command(label= i[0], command = i[1] )


    G.abism_menu['menu'] = G.abism_menu.menu
    return G.abism_menu





    if (type(String) is str or type(String) is unicode) and String != "" :
      if W.verbose>0 : print "Opening file : " + String
      W.image_name = String
      InitImage()


    title=W.image_name.split('/')  # we cut the title
    G.parent.title('Abism (' + title[-1]+')')


    #drawing= G.ax1.imshow(W.Im0,vmin=G.min_cut,vmax=G.max_cut)
    #G.cbar.set_clim(vmin=G.min_cut,vmax=G.max_cut)
    #G.cbar.draw_all()
    #G.fig.canvas.draw()
    return

def ToolMenu():
    G.tool_menu=Menubutton(G.MenuBar,**args)
    G.tool_menu.menu=Menu(G.tool_menu,**G.submenu_args)

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


def ViewMenu():
    G.scale_menu=Menubutton(G.MenuBar,**args)
    G.scale_menu.menu=Menu(G.scale_menu,**G.submenu_args)


    ###############"
    ## COLOR
    def Color() :
        if G.scale_menu_type== "cascade" :
          color_menu = Menu(G.scale_menu,**G.submenu_args)
        else :
          color_menu = G.scale_menu.menu
	color_menu.add_command(label="COLOR",bg=None,state=DISABLED)
           # if we don't want cascade, we just add in the menu

        G.cu_color=StringVar(); G.cu_color.set(G.scale_dic[0]["cmap"]) # because image not loaded yet



        ###########"
        # My colors
        lst = [
                 ["Jet","jet"],
                 ['Black&White','bone'],
          ['Spectral','spectral'],
          ["RdYlBu","RdYlBu"],
          ["BuPu","BuPu"]
       ]
        for i in lst :
          color_menu.add_radiobutton(label=i[0],
            command=lambda i=i: MG.Scale(dic={"cmap":i[1]},run="G.cu_cut.set('"+i[1] +"')"   ),
            variable=G.cu_color,value=i[1]) # we use same value as label


        ########
        # Contour
        color_menu.add_command(label='Contour',
            command=lambda  : MG.Scale(dic={"contour":'not a bool'}  )
     )


        #################
        # more colors
        more_color_menu = Menu(color_menu,**G.submenu_args)
        num=0
        for i in G.all_cmaps :
            num+=1
            more_color_menu.add_radiobutton(label=i,
              command=lambda i=i: MG.Scale(dic={"cmap":i}),
              variable=G.cu_color,value=i) # we use same value as label

            if num%30==0  :

              more_color_menu.add_radiobutton(label=i,
                command=lambda i=i : MG.Scale(dic={"cmap":i}),
                variable=G.cu_color,value=i,columnbreak=1) # we use same value as label
        color_menu.add_cascade(menu=more_color_menu,label="More colors",underline=0)



        if G.scale_menu_type== "cascade" :
           G.scale_menu.menu.add_cascade(menu=color_menu, underline=0,label="Color")
        else :
           G.scale_menu.menu.add_command(columnbreak=1)


    ##############
    ###" SCALE FUNCTION
    def Scale():
        if G.scale_menu_type== "cascade" : scale_menu = Menu(G.scale_menu,**G.submenu_args)
        else :
          scale_menu = G.scale_menu.menu
	scale_menu.add_command(label="FCT",bg=None,state=DISABLED)

        G.cu_scale=StringVar(); G.cu_scale.set(G.scale_dic[0]["stretch"])
        lst = [  ["Lin","x","linear"],["Sqrt","x**0.5","sqrt"],["Square","x**2","square"],["Log","np.log(x+1)/0.69","log"],["Arcsinh","","arcsinh" ]   ]
        for i in lst :
          scale_menu.add_radiobutton(label=i[0]   ,
            command=lambda i=i : MG.Scale( dic={"fct":i[1],"stretch":i[2]},run="G.cu_scale.set('"+ i[2] +"')" ) ,
            variable=G.cu_scale,value=i[2]) # we use same value as label


        if G.scale_menu_type== "cascade" :
           G.scale_menu.menu.add_cascade(menu=scale_menu, underline=0,label="Fct")
        else :
           G.scale_menu.menu.add_command(columnbreak=1)

    #G.bu_scale['menu'] = G.bu_scale.menu
    #G.bu_scale.bind("<Button-1>",lambda event : MG.Scale(dic={"tutorial":1,"fct":"truc"}) )


    ##############
    ##  CUT TYPE
    def Cut() :
        if G.scale_menu_type== "cascade" : cut_menu = Menu(G.scale_menu,**G.submenu_args)
        else :
          cut_menu = G.scale_menu.menu
	cut_menu.add_command(label="CUTS",bg=None,state=DISABLED)

        G.cu_cut=StringVar(); G.cu_cut.set("RMS")
        # label , scale_cut_type, key, value
        lst = [  ["RMS","sigma_clip","sigma",3],["99.95%","percent","percent",99.95],
                 ["99.9%","percent","percent",99.9], ["99.5%","percent","percent",99.5],
                 ["99%","percent","percent",99.], ["90%","percent","percent",90],
                 ["None","None","truc","truc"] ,
          #["Manual","manual","truc","truc"] ,  ]
          ]
        for i in lst :
          cut_menu.add_radiobutton(label=i[0],
            command=lambda i=i : MG.Scale(dic={"scale_cut_type":i[1],i[2]:i[3]},run="G.cu_cut.set('"+i[0] +"')"  ),
            variable=G.cu_cut,value=i[0]) # we use same value as label

        cut_menu.add_radiobutton(label="Manual",
            command= ManualCut,
            variable=G.cu_cut,value="Manual") # we use same value as label

        if G.scale_menu_type== "cascade" :
           G.scale_menu.menu.add_cascade(menu=cut_menu, underline=0,label="Cut")
        else :
           G.scale_menu.menu.add_command(columnbreak=1)

    #G.bu_cut['menu'] = G.bu_cut.menu
    #G.bu_cut.bind("<Button-1>",lambda event : MG.Scale(dic={"tutorial":1,"scale_cut_type":"truc"}) )

    Color()
    Scale()
    Cut()
    G.scale_menu['menu'] = G.scale_menu.menu

    return G.scale_menu


def AnalysisMenu() :
    G.analysis_menu= Menubutton(G.MenuBar,**args)
    G.analysis_menu.menu=Menu(G.analysis_menu,**G.submenu_args)

    def FitType() :
      fit_menu = G.analysis_menu.menu
      fit_menu.add_command(label="Fit Type",bg=None,state=DISABLED)

      G.cu_fit=StringVar(); G.cu_fit.set( W.type["fit"].replace("2D","") )
      lst1 = [
           ["Gaussian"      ,  "Gaussian"        ,  lambda : MG.FitType("Gaussian"      )],
           ["Moffat"        ,  "Moffat"          ,  lambda : MG.FitType("Moffat"        )],
           ["Bessel1"       ,  "Bessel1"         ,  lambda : MG.FitType("Bessel1"       )],
           #["Gaussian_hole" ,  "Gaussian_hole"   ,  lambda : MG.FitType("Gaussian_hole" )],
           ["None"          ,  "None"            ,  lambda : MG.FitType("None"          )],
           ]
      for i in lst1 :
         fit_menu.add_radiobutton(
             label=i[0]   , command= i[2],
             variable=G.cu_fit,value=i[1]) # we use same value as label

      # more options
      if not G.more_bool : G.analysis_menu.menu.add_command(label=u'\u25be '+'More Options',command=MoreWidget)
      else :  G.analysis_menu.menu.add_command(label=u'\u25b4 '+'Less Options',command=MoreWidget)


      G.analysis_menu.menu.add_command(columnbreak=1)
      return


    def PickType() :
      pick_menu = G.analysis_menu.menu
      pick_menu.add_command(label="Pick Object(s)",bg=None,state=DISABLED)

      G.cu_pick=StringVar(); G.cu_pick.set( W.type["pick"] )
      lst2 = [
           ["PickOne"   , "one"     ,lambda : Pick.RefreshPick("one") ],
           ["Binary Fit", "binary"  ,lambda : Pick.RefreshPick("binary") ] ,
           #["Tight Binary", "tightbinary"  ,lambda : Pick.RefreshPick("tightbinary") ] ,
           ["PickMany"  , "many"    ,lambda : Pick.RefreshPick("many") ],
           ["No Pick"   , "nopick"  ,lambda : Pick.RefreshPick("nopick") ],
            ]
      lst3 = [
           #["Ellipse"   , "ellipse" ,lambda : Pick.RefreshPick("ellipse") ] ,
           #["Annulus"   , "annulus" ,lambda : Pick.RefreshPick("annulus") ],
           ]

      for i in lst2 :
          pick_menu.add_radiobutton(
               label=i[0], command=i[2],
               variable=G.cu_pick, value=i[1]) # we use same value as label

      # MORE
      #more_menu = Menu(pick_menu,**G.submenu_args)
      #for i in lst3 :
      #  more_menu.add_radiobutton(label= i[0] , command = i[1],
      #          variable=G.cu_pick, value= i[1] )

      #pick_menu.add_cascade(menu=more_menu,label="More",underline=0)
      #G.analysis_menu.menu.add_command(columnbreak=1)
      #return


    FitType() ; PickType()
    G.analysis_menu['menu'] = G.analysis_menu.menu
    return G.analysis_menu




def MoreWidget():
    ""

    # Change  menu label more option -> less option
    for i in range(1,10) :
         j = G.analysis_menu.menu.entrycget(i,"label")
         if "Option" in j:
           if G.more_bool : G.analysis_menu.menu.entryconfig(i,label=u'\u25be '+'More Option')
           else           :  G.analysis_menu.menu.entryconfig(i,label=u'\u25b4 '+'Less Option' )
           break

    # CHANGE BOOL MAY CLOSE
    if G.more_bool ==1 : # close more frame
      MoreClose()

    else :  # CREATE
      G.more_bool = not G.more_bool # mean = 1
      G.top_bool = 0
      TopResize()


      ##########""
      # FRAME
      G.MoreFrame = Frame(G.LeftTopFrame,bg=G.bg[0])  #create the more_staff Frame
      G.all_frame.append("G.MoreFrame")
      G.MoreFrame.pack(side=TOP,expand=0,fill=X)

      Label(G.MoreFrame,text="More Options",**G.frame_title_arg).pack(side=TOP,anchor="w")

      G.MoreGridFrame = Frame(G.MoreFrame,bg=G.bg[0])  #create the more_staff Frame
      G.all_frame.append("G.MoreGridFrame")
      G.MoreGridFrame.pack(side=TOP,expand=0,fill=X)
      G.MoreGridFrame.columnconfigure(0,weight=1)
      G.MoreGridFrame.columnconfigure(1,weight=1)



      def SubtractBackground(frame) :
        G.bu_subtract_bg=Button(frame,text='SubstractBackground',
                        background=G.bu_subtract_bg_color,command=MG.SubstractBackground,**G.bu_arg)
        return G.bu_subtract_bg



      def NoiseType(frame) :
        G.menu_noise=Menubutton(frame,text=u'\u25be '+'Background',relief=RAISED, background=G.menu_noise_color,**G.bu_arg)
        G.menu_noise.menu=Menu(G.menu_noise)

        G.cu_noise=StringVar(); G.cu_noise.set(W.type["noise"])
        lst = [
                ["Annulus","elliptical_annulus" ],
                ['Fit','fit'] ,
                ["8Rects","8rects"]  ,
            ['Manual',"manual" ],
                ["None","None"],
            ]
             #  ["InRectangle", "in_rectangle" ] ,
        for i in lst :
          if i[0] == "Manual" :
            G.menu_noise.menu.add_radiobutton(label=i[0]   ,
              command=ManualBackground,
              variable=G.cu_noise,value=i[1]) # W.type[noise] as value
          else :
            G.menu_noise.menu.add_radiobutton(label=i[0]   ,
              command=lambda i=i : MG.VarSet('W.type["noise"]',i[1]) ,
              variable=G.cu_noise,value=i[1])

        G.menu_noise['menu'] = G.menu_noise.menu
        return G.menu_noise


      def PhotType(frame)  :
          G.menu_phot=Menubutton(frame,text=u'\u25be '+'Photometry',relief=RAISED, background=G.menu_phot_color,**G.bu_arg)
          G.menu_phot.menu=Menu(G.menu_phot)

          G.cu_phot=StringVar(); G.cu_phot.set(W.type["phot"])
          lst =  [
      	  ["Elliptical Aperture","elliptical_aperture"] ,
                [ 'Fit','fit'],
      	  ['Rectangle Aperture','encircled_energy'],
      	  ['Manual','manual'],
      	  ]
          for i in lst :
            G.menu_phot.menu.add_radiobutton(label=i[0]   ,
              command=lambda i=i : MG.VarSet('W.type["phot"]',i[1]) ,
              variable=G.cu_phot,value=i[1]) # we use W.type[phot"]

          G.menu_phot['menu'] = G.menu_phot.menu
      return G.menu_phot


      def Check(frame) :
          myargs = { "anchor":"w","bg":G.bg[0],"fg":G.fg[0], "padx":0 ,  "pady":0 ,"highlightthickness":0 }
          ################
          # isoplanetism
          G.iso_check = Checkbutton(frame,
             text="Anisomorphism", variable=W.aniso_var,
                 command=lambda :MG.FitType(W.type["fit"]),**myargs) # by default onvalue=1

          G.same_check = Checkbutton(G.MoreGridFrame,
            text="Binary_same_psf", variable=W.same_psf_var,
                command = lambda : MG.FitType(W.type["fit"]),**myargs)

          G.same_center_check = Checkbutton(G.MoreGridFrame,
            text="Saturated_same_center", variable=W.same_center_var,
                command= lambda: MG.FitType(W.type["fit"]),**myargs)

      return G.iso_check, G.same_check, G.same_center_check


      SubtractBackground(G.MoreGridFrame).grid(row=0,column=0,columnspan = 2,sticky="nswe")
      NoiseType(G.MoreGridFrame).grid(row=1,column=0,sticky="nswe")
      PhotType(G.MoreGridFrame).grid(row=1,column=1,sticky="nswe" )
      row=2
      for i in Check(G.MoreGridFrame) :
        i.grid(row = row, column=0,columnspan = 2 ,sticky="nwse")
        row+=1

      G.bu_close=Button(G.MoreGridFrame,text=u'\u25b4 '+'Close',background=G.bu_close_color,command=MoreClose,**G.bu_arg)
      G.bu_close.grid(row=row,column=0,columnspan=2)


def ManualCut():
  if G.manual_cut_bool :
    ManualCutClose()

  else : # including no manula_cut_bool
    G.top_resize = 1
    TopResize()
    G.top_resize = 0
    TopResize()
    G.manual_cut_bool = not G.manual_cut_bool
    G.ManualCutFrame=Frame(G.LeftTopFrame,bg=G.bg[0])
    G.all_frame.append("G.ManualCutFrame")
    G.ManualCutFrame.pack(side=TOP,expand=0,fill=X)

    Label(G.ManualCutFrame,text="Cut image scale",**G.frame_title_arg).pack(side=TOP,anchor="w")

    G.ManualCutGridFrame=Frame(G.ManualCutFrame,bg=G.bg[0])
    G.all_frame.append("G.ManualCutGridFrame")
    G.ManualCutGridFrame.pack(side=TOP,expand=0,fill=X)

    G.ManualCutGridFrame.columnconfigure(0,weight=1)
    G.ManualCutGridFrame.columnconfigure(1,weight=1)

    def GetValue(event):
      dic = {"min_cut":float(G.entries[1].get()),
             "max_cut":float(G.entries[0].get())}
      if W.verbose >2 : print "InitGui.py/ManualCut, dic called , ",dic
      MG.Scale(dic=dic) # Call MyGui


    lst = [  ["Max cut","max_cut"],  ["Min cut","min_cut"]  ]
    G.entries=[]
    r=0
    for i in lst :
      G.l=Label(G.ManualCutGridFrame,text=i[0],font=G.font_param,**G.lb_arg)
      G.l.grid(row=r,column=0,sticky="snew")#,sticky=W)
      v= StringVar()
      G.e=Entry(G.ManualCutGridFrame, width=10,textvariable=v,font=G.font_param,**G.en_arg)
      G.e.grid(row=r,column=1,sticky="nsew")#,sticky=W)
      G.e.bind('<Return>',GetValue)
      v.set("%.1f"%G.scale_dic[0][i[1]])
      G.entries.append(v)
      r+=1


    ###############
    ##  CLOSE button
    G.bu_close=Button(G.ManualCutGridFrame,text=u'\u25b4 '+'Close',background=G.bu_close_color,command=ManualCutClose,**G.bu_arg)
    G.bu_close.grid(row=r,column=0,columnspan=2)
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

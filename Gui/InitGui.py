try : from Tkinter import *
except  : from tkinter import *
import tkFont
import re 

import MyGui  as MG
import Pick # pick et pick et kolegram bour et bour et ratatam


import GuyVariables as G
import WorkVariables as W


    ##################
    ## 0/ Main Caller
    #################

def WindowInit():
  Title() 
  MainFrameMaker()  # Create MenuBar and MainPaned, TextFrame and DrawFrame

  Shortcuts() # take MG and parents  



def Title(): # Icon, geometry 
  G.parent.title('ABISM ('+"/".join(str(W.image_name).split("/")[-3:])+')')     #   Adaptative Background Interactive Strehl Meter') 

  # ICON
  import os.path
  if os.path.isfile(W.path+'/Icon/bato_chico.gif') :
    bitmap = PhotoImage(file =W.path+'/Icon/bato_chico.gif')
    G.parent.tk.call('wm', 'iconphoto', G.parent._w, bitmap)
  else : 
    if W.verbose > 3 : print " you have no beautiful icon because you didn't set the PATH in Abism.py "

  if G.geo_dic.has_key("parent") :
     G.parent.geometry(G.geo_dic["parent"]) 

def MainFrameMaker():  
  ""
  # 1 TOP 
  MenuBarMaker() 

  G.MainPaned=PanedWindow(G.parent,orient=HORIZONTAL,**G.paned_dic)
  G.all_frame.append("G.MainPaned")
  G.MainPaned.pack(side=TOP, fill=BOTH,expand=1)

  # 2 left
  TextFrameMaker()  
 
  # 3 if nothing goes right go left  
  DrawFrameMaker() 


    ################
    ## 1/  MENU 
    ###############"

def MenuBarMaker(): # CALLER   
  global args         # the args of "MenuButton"

  G.MenuBar = Frame(G.parent,bg=G.bg[0]) 
  G.all_frame.append("G.MenuBar")
  G.MenuBar.pack(side=TOP, expand = 0 , fill = X ) 

  col=0
  args = G.me_arg.copy() 
  args.update (  {"relief":FLAT, "width":G.menu_button_width }  ) 
  for i in [
    ["AbismMenu", {"text":u"\u25be "+"ABISM"}           ],
    ["FileMenu", {"text":u"\u25be "+"File"}  ] ,  
    ["AnalysisMenu",  {"text":u'\u25be '+'Analysis'} ] ,
    ["ViewMenu",  {"text":u'\u25be '+'View'} ], 
    ["ToolMenu",  {"text":u'\u25be '+'Tools'} ], 
    ] : 
      args.update( i[1] ) 
      button = globals()[i[0]]() # the actual CALL  
      G.MenuBar.columnconfigure(col,weight=1)
      button.grid(row=0,column=col,sticky="nsew") 

      col+=1
    

def AbismMenu():     
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


def FileMenu():
  G.menu=Menubutton(G.MenuBar,**args)   
  G.menu.menu=Menu(G.menu,**G.submenu_args)

  G.menu.menu.add_command(label='Open',command=MG.Open)
  G.menu.menu.add_command(label='Display Header',command=MG.DisplayHeader) 

  G.menu['menu'] = G.menu.menu  
  return G.menu  


def ToolMenu(): 
  G.tool_menu=Menubutton(G.MenuBar,**args)   
  G.tool_menu.menu=Menu(G.tool_menu,**G.submenu_args)

  lst = [
     ["Profile"   ,  lambda : Pick.RefreshPick("profile") ], 
     ["Stat"      ,  lambda : Pick.RefreshPick("stat") ], 
     [ "Histogram", MG.Histopopo ], 
     [ "Python Console", MG.PythonConsole ], 
     [ u'\u25be '+'Calculator', Calculator ], 
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

  


    #################
    ## 2/  DrawPaned
    ##################

def DrawFrameMaker() :  # receive G.MainPaned 
  G.DrawPaned = PanedWindow(G.MainPaned,orient=VERTICAL,**G.paned_dic)#,width=650)
  G.all_frame.append("G.DrawPaned")
  if G.geo_dic.has_key("DrawPaned"): 
    G.MainPaned.add(G.DrawPaned,width=float(G.geo_dic["DrawPaned"]))
  else : # including don't set width 
    G.MainPaned.add(G.DrawPaned)

  Image() 
  RightBottom() 
  RightBottomSub() 

def Image(): 
  G.ImageFrame = Frame(G.DrawPaned,bg=G.bg[0])  #,width=100, height=100)
  G.all_frame.append("G.ImageFrame") 
  if G.geo_dic.has_key("ImageFrame"): 
    G.DrawPaned.add(G.ImageFrame,height=float(G.geo_dic["ImageFrame"]))
  else : # including don't set width 
    G.DrawPaned.add(G.ImageFrame)
  G.all_frame.append("G.ImageFrame") 

def RightBottom(): 
  G.RightBottomPaned = PanedWindow(G.DrawPaned,orient=HORIZONTAL,**G.paned_dic)
  if G.geo_dic.has_key("RightBottomPaned"): targ={"height":float(G.geo_dic["RightBottomPaned"]) } 
  else : targ= {} 
  G.DrawPaned.add(G.RightBottomPaned,**targ)
  G.all_frame.append("G.RightBottomPaned") 

def RightBottomSub() : #In RightBottomPaned 2 : FitFrame, ResultFrame (should be star frame) 
  def Fit() : 
    G.FitFrame = Frame(G.RightBottomPaned,bg=G.bg[0])
    if G.geo_dic.has_key("FitFrame"): targ={"width":float(G.geo_dic["FitFrame"]) }
    else : targ= {} 
    G.RightBottomPaned.add(G.FitFrame,**targ)
    G.all_frame.append("G.FitFrame") 


  def Result() : 
    G.ResultFrame = Frame(G.RightBottomPaned,bg=G.bg[0])
    if G.geo_dic.has_key("ResultFrame"): targ={"width":float(G.geo_dic["ResultFrame"]) }
    else : targ= {} 
    G.RightBottomPaned.add(G.ResultFrame,**targ)
    G.all_frame.append("G.ResultFrame") 


  Fit() ; Result() 




    ###########
    # 3/  TextPaned 
    ############


def TextFrameMaker() :
  ""
  #FRAMES 
  G.TextFrame = Frame(G.MainPaned,**G.fr_arg) 
  G.all_frame.append("G.TextFrame") 
  if G.geo_dic.has_key("TextPaned"): 
    G.MainPaned.add(G.TextFrame,width=float(G.geo_dic["TextPaned"]))
  else : # including don't set width 
    G.MainPaned.add(G.TextFrame)


  #BUTTONS 
  TextButton1(G.TextFrame).pack(side=TOP,expand=0,fill=X)

  #PANED 
  G.TextPaned = PanedWindow(G.TextFrame,orient=VERTICAL,**G.paned_dic)
  G.TextPaned.pack(side=TOP, expand=1, fill = BOTH ) # this is the main paned on the left so it should expand 
  G.all_frame.append("G.TextPaned") 

  LeftLabel() 
  LeftTop() 
  LeftResult() 


def TextButton1(frame):
  ""
  # FRAMES 
  G.ButtonFrame=Frame(frame,bg=G.bg[0]) 
  G.all_frame.append("G.Button1Frame") 
  
  G.Button1Frame= Frame(G.ButtonFrame, **G.fr_arg)
  G.Button1Frame.pack(side=TOP,fill=X,expand=0) 


  # DEFINE BUTTON 
  G.bu_quit=Button(G.Button1Frame,text='QUIT',background=G.bu_quit_color, 
                  command=MG.Quit,**G.bu_arg)  # QUIT
  G.bu_restart=Button(G.Button1Frame,text='RESTART',background =G.bu_restart_color, command=MG.Restart, **G.bu_arg)                   # RESTART
  G.bu_manual=Button(G.Button1Frame,text=u'\u25be '+'ImageParameters',
                  background=G.bu_manual_color,command=ImageParameter,**G.bu_arg) #Manual M 

  # grid its 
  G.Button1Frame.columnconfigure(0,weight=1)
  G.Button1Frame.columnconfigure(1,weight=1)

  G.bu_quit.grid(row=0,column=0,sticky="nsew")
  G.bu_restart.grid(row=0,column=1,sticky="nsew")
  G.bu_manual.grid(row=1,column=0,columnspan=2,sticky="nsew")

  return G.ButtonFrame  


def LeftLabel() : #LeftTipTopFrame
  G.LabelFrame0 = Frame(G.TextPaned,**G.fr_arg) ###
  G.all_frame.append("G.LabelFrame0") 
  arg= G.sub_paned_arg
  if G.geo_dic.has_key("LabelFrame"): 
    arg.update({ "height":int(G.geo_dic["LabelFrame"])  })
    if W.verbose > 3 : print "I chose ", int(G.geo_dic["LabelFrame"]), " for height of LABEL FRAME" 
  G.TextPaned.add(G.LabelFrame0,**arg)
  G.LabelFrame = Frame(G.LabelFrame0,**G.fr_arg) 
  G.LabelFrame.pack(side=TOP,fill=BOTH,expand=0) 
  

def LeftTop() : # call TxtButton1() 
  G.LeftTopFrame = Frame(G.TextPaned,bg=G.bg[0]) ###
  G.all_frame.append("G.LeftTopFrame") 
  arg= G.sub_paned_arg
  if G.geo_dic.has_key("LeftTopFrame"): 
     arg.update({ "height":int(G.geo_dic["LeftTopFrame"])  })
     if W.verbose > 3 : print "I chose ", int(G.geo_dic["LeftTopFrame"]), " for height of LefTOPFRAME" 
  G.TextPaned.add(G.LeftTopFrame,**arg)
  LeftTopArrow() 



def LeftResult() : 
  ""
  # APPEND TO PANED 
  G.LeftBottomFrame = Frame(G.TextPaned,bg=G.bg[0]) ###
  G.all_frame.append("G.LeftBottomFrame") 
  arg= G.sub_paned_arg
  if G.geo_dic.has_key("LeftBottomFrame"): 
     arg.update({ "height":int(G.geo_dic["LeftBottomFrame"])  })
  G.TextPaned.add(G.LeftBottomFrame,**arg)

  G.ResultLabelFrame =Frame(G.LeftBottomFrame,bg=G.bg[0])
  G.ResultLabelFrame.pack(side=TOP,fill=X)
  G.all_frame.append("G.ResultLabelFrame") 

  # RESULT LABEL [written 'result' and fit type at the top 
  Label(G.ResultLabelFrame,text="Results",**G.frame_title_arg).pack(side=LEFT) 
  G.fit_type_label = Label(G.ResultLabelFrame,text=W.type["fit"],justify=CENTER,**G.lb_arg)
  G.fit_type_label.pack(fill=X) 

  # ANSWER FRAME
  G.AnswerFrame=Frame(G.TextPaned,bg=G.bg[0]) 
  G.all_frame.append("G.AnswerFrame") 
  G.AnswerFrame.pack(expand=0,fill=BOTH) 

  # ARROW in RESULT LABEL 
  #if G.result_bool :  # label is big 
  if False : 
    photo = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
  else : 
    photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")
  G.result_frame_arrow = Button(G.LeftBottomFrame,command=ResultResize,image=photo,**G.bu_arg) 
  G.result_frame_arrow.image= photo  # keep a reference 
  G.result_frame_arrow.place(relx=1.,rely=0.,anchor="ne")



###
## TEXT ARROWS
####
def LabelDisplay(expand=False): # called later What do I know from header,
  """ warning: exapnd not working well 
  ESO /  not ESO 
  NAco/vlt
  Reduced/raw
  Nx x Ny x Nz
  WCS detected or not 
  """
  lst=[]
  # ESO 
  if W.head.company == "ESO" : comp = "ESO"
  else                  : comp = "NOT ESO"
  #VLT/NACO
  if W.head.instrument == "NAOS+CONICA" : ins= "NaCo"
  else                             : ins= W.head.instrument
  tel= re.sub("-U.","",W.head.telescope.replace("ESO-","") ) # to delete ESO-  and -U4
  lbl = comp +" / " +tel + " / "+ ins
  lst.append(lbl)

  #REDUCED ? #Nx * Ny * Nz
  if "reduced_type" in vars(W.head) : 
     lbl=W.head.reduced_type
  shape = list(W.Im0.shape[::-1]) # reverse, inverse, list order 
  if "NAXIS3" in W.head.header.keys(): 
     shape.append(W.head.header["NAXIS3"])
     lbl+= "%i x %i x %i" % (shape[0],shape[1],shape[2])
  else:
     lbl+= "%i x %i " % (shape[0],shape[1])
  lst.append(lbl)

  #WCS 
  if W.head.wcs_bool : lbl= "WCS detected"
  else               : lbl ="WCS NOT detected"
  lst.append(lbl)


  # Header reads Strehl variables ? 
  if (W.head.diameter==99. or  W.head.wavelength==99. or W.head.obstruction==99. or W.head.pixel_scale==99.):
      lbl = "WARNING: some parameters not found"
      lst.append(   (lbl,{"fg":"red"}) ) 
  else :  
      lbl = "Parameters read from header"     
      lst.append(   (lbl,{"fg":"blue"}) ) 


  # UNDERSAMPLED 
  bol = W.head.wavelength*1e-6/W.head.diameter/(W.head.pixel_scale/206265)<2 
  bol2 =    "sinf_pixel_scale" in vars(W.head) and ( ( W.head.sinf_pixel_scale == 0.025) or ( W.head.sinf_pixel_scale == 0.01) ) 
  bol = bol or bol2 
  if bol : 
      lbl = "!!! SPATIALLY UNDERSAMPLED !!!"
      lst.append(   (lbl,{"fg":"red"}) ) 

  # GRID LABLES 
  row = 0 
  G.LabelFrame.columnconfigure(0,weight=1) 
  if W.verbose >3 : print "Label lst" , lst
  for i in lst : 
     arg = G.lb_arg.copy() 
     arg.update({"justify":CENTER})
     if type(i) == list or type(i) == tuple  : 
         arg.update(i[1])
	 i= i[0]
     Label(G.LabelFrame,text=i,**arg).grid(row=row,column=0,sticky="nsew")
     row+=1


     



  # place arrow to resize 
  if G.label_bool :  # label is big 
    photo = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
  else : 
    photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")
  G.label_frame_arrow = Button(G.LabelFrame,command=LabelResize,image=photo,**G.bu_arg) 
  G.label_frame_arrow.image= photo  # keep a reference 
  G.label_frame_arrow.place(relx=1.,rely=0.,anchor="ne")


  # place frame_title_label 
  Label(G.LabelFrame,text="Labels",**G.frame_title_arg).place(x=0,y=0)


  # Button to resize 
  arg = G.bu_arg.copy()
  arg.update({  "text":"OK",
            "command": LabelResize,
	    "padx":3,"width":20   })
  G.last_label = Button(G.LabelFrame,**arg)
  G.last_label.grid(row=row,column=0,sticky="nswe")
  row+=1

  if expand : 
     G.label_bool = 0 
     LabelResize() 


def LabelResize() : # called  later  
     if G.label_bool : 
        G.TextPaned.sash_place(0,0,22)
        photo = PhotoImage(file=W.path+"/Icon/arrow_down.gif")
	if W.verbose > 3 : print "REsize Label: ", 22
     else :   
        G.TextPaned.sash_place(0,0, G.last_label.winfo_y()+G.last_label.winfo_height()  )
        photo = PhotoImage(file=W.path+"/Icon/arrow_up.gif")
	if W.verbose > 3 : print "REsize Label: ",  G.last_label.winfo_y()+G.last_label.winfo_height() 
     G.label_bool = not G.label_bool 
     G.label_frame_arrow['image'] = photo
     G.label_frame_arrow.image= photo  # keep a reference 
     return 


def LeftTopArrow() :  # jsut draw the arrow, see after 
  """ this do not need to be on a function but if you want to place 
      the arrow it will vanish when packing other frame. SO I packed the 
      arrow, otherwhise you need to redraw it all the time
  """
  G.LeftTopArrowFrame = Frame(G.LeftTopFrame,**G.fr_arg) 
  G.LeftTopArrowFrame.pack(side=TOP,expand=0, fill = X ) 

  if G.top_bool :  # label is big 
    photo = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
  else : 
    photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")
  G.top_frame_arrow = Button(G.LeftTopArrowFrame,command=TopResize,image=photo,**G.bu_arg) 
  G.top_frame_arrow.image= photo  # keep a reference 
  G.top_frame_arrow.pack(side=RIGHT,anchor="ne",expand=0) 


def TopResize() : # called  later  
     if G.top_bool : 
        photo = PhotoImage(file=W.path+"/Icon/arrow_down.gif")
        base = G.TextPaned.sash_coord(0)[1] # jus height of the previous sash
        G.TextPaned.sash_place(1,0,base+ 22+2* G.paned_dic["sashwidth"] )
	if W.verbose > 3 : print "REsize top: ", 22
     else :   
        photo = PhotoImage(file=W.path+"/Icon/arrow_up.gif")
        place = G.parent.winfo_height() - G.TextPaned.winfo_rooty()  - 200 
        G.TextPaned.sash_place(1,0,place)
        #def Pos(): # calculate position of the sash 
	#   #corner1 = G.TextPaned.winfo_rooty() 
	#   G.TextPaned.sash_place(1,0,2000) # to expand the widget, and estimate their size 
	#   corner2 = max ([ i.winfo_rooty() for j in G.LeftTopFrame.winfo_children() for  i in j .winfo_children()   ])

	#   return corner2 + 40   # just y pos 
	#pos = Pos() 
        #G.TextPaned.sash_place( 1,0,pos )
	#if W.verbose > 3 : print "REsize Top: ",pos 
        
     G.top_bool = not G.top_bool 
     G.top_frame_arrow['image'] = photo
     G.top_frame_arrow.image= photo  # keep a reference 
     return 


def ResultResize(how = "max") : # called  later  
     #if not G.result_bool : # this is to expand 
     if how=="max" : # resize max 
        base = G.TextPaned.sash_coord(0)[1] # jus height of the previous sash
        G.TextPaned.sash_place(1,0,base+ 22+2* G.paned_dic["sashwidth"] )
        photo = PhotoImage(file=W.path+"/Icon/arrow_down.gif")
	if W.verbose > 3 : print "REsize result: ", 22

     elif how =="full" : # see everything but not more 
        def Pos(): # calculate position of the sash 
	   G.TextPaned.sash_place(1,0,) # to expand the widget, and estimate their size 
	   corner2 = max ([ i.winfo_rooty() for j in G.LeftBottomFrame.winfo_children() for  i in j.winfo_children()   ])
	   base   = G.LeftBottomFrame.winfo_rooty() 
           size = corner2 - base 
	   base_sash1 = G.LeftTopFrame.winfo_rooty() 
           pos = G.parent.winfo_height() - size -base_sash1 
           if W.verbose >3 : print "Resize",corner2,total,"base1", base_sash1, size, base, pos  
	   
	   return max (pos ,22 )  # petite bite GUI 
	pos = Pos() 
        G.TextPaned.sash_place( 1,0,pos )
	if W.verbose > 3 : print "REsize Top: ",pos 
        
     return 






    ######################
    ### 4/  MORE FRAMES if click on some buttons  #
    ######################

def GetValueIP(event,destroy= True): # ImageParameter
    for i in G.image_parameter_list:
      vars(W.head)[i[1]] = float( vars(G.tkentry)[i[1]].get() ) 
      # COLOR 
      if vars(W.head)[i[1]] == i[2] : 
        vars(G.tkentry)[i[1]]["bg"]="#ff9090" 
      else : vars(G.tkentry)[i[1]]["bg"]="#ffffff" 
      ResetLabel(expand=False) 

          
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


def Calculator(): # On LeftTopFrame
    if G.tutorial:
                   text="This button create a Calculator in the G.LabelFrame. You can put the cursor in the text entry and type with the keyboard and press enter to get the result or clisk on the button and '=' returns the answer. Numpy is automatically import as *"
		   text+="\n\nProgrammers a memory would be user firendly, but anyway, nobody will use this calculator, bc or python or awk are much  better..." 
		   MG.TutorialReturn({"title":"Calculator",
		   "text":text,
		   })
		   return     
    G.cal_bool = not G.cal_bool



    # CONSTRUCT
    if G.cal_bool : 
	  
      # FRAME
      G.CalculatorFrame = Frame( G.LeftTopFrame ,**G.fr_arg ) 
      G.CalculatorFrame.pack(side=TOP,expand=0, fill=X) 
      # TITLE 
      Label(G.CalculatorFrame,text="Calculator",**G.frame_title_arg).pack(side=TOP,anchor="w")
      G.all_frame.append("CalculatorFrame") 
      import Calculator as Cal
      Cal.MyCalculator( G.CalculatorFrame ) 


    # DESTROY 
    elif "CalculatorFrame" in vars(G)  : 
      G.CalculatorFrame.destroy() 
      if G.in_arrow_frame == "cal_title" : G.arrtitle.destroy() 


    # Change tool menu label
    for i in range(1,10) : 
       j = G.tool_menu.menu.entrycget(i,"label")
       if "Calculator" in j: 
         if G.cal_bool : G.tool_menu.menu.entryconfig(i,label=u'\u25b4 '+'Calculator') 
	 else        :  G.tool_menu.menu.entryconfig(i,label=u'\u25be '+'Calculator' )
	 break 
         
      
    return 



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



def MoreWidget():  
  ""

  # Change  menu label more option -> less option 
  for i in range(1,10) : 
       j = G.analysis_menu.menu.entrycget(i,"label")
       if "Option" in j: 
         if G.more_bool : G.analysis_menu.menu.entryconfig(i,label=u'\u25be '+'More Option') 
	 else        :  G.analysis_menu.menu.entryconfig(i,label=u'\u25b4 '+'Less Option' )
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
def MoreClose():
       ""
       # change bool destroy 
       G.more_bool = not G.more_bool
       G.MoreFrame.destroy()      
       if G.in_arrow_frame == "title_more" : 
          G.arrtitle.destroy() 
	  G.in_arrow_frame = None
       G.all_frame = [ x for x in G.all_frame if x!="G.MoreFrame" ] # remove MoreFrame

       # Change help menu label
       for i in range(1,10) : 
         j = G.analysis_menu.menu.entrycget(i,"label")
         if "Option" in j: 
           G.analysis_menu.menu.entryconfig(i,label=u'\u25be '+'More Option') 
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

def BgCl(color=None,who="bg") :# Background COlor, change the color of ABism take G.bg[0] t
  ""
  # Defined colors, set bg, fg, lists 
  if color !=None  : vars(G)[who][0] = color 
  color = vars(G)[who][0] 

  # update some dics 
  import GlobalDefiner
  GlobalDefiner.LinkedColor() # to reload dictionnaries 



  def Frames(): # BG for frames in all_frame 
    for i in G.all_frame : 
      if not "Paned" in i : 
         if W.verbose  > 7 : print i 
	 try : 
            exec(i +"['bg'] = G.bg[0]") in globals(), locals()     # remove 2 first letter because it is G. done for sed , not Paned please 
	 except : pass

  def Canvas() : # BG for figure 
    G.fig.set_facecolor( color )
    G.fig.canvas.draw() 
    G.figfit.set_facecolor( color )
    G.figfit.canvas.draw() 
    G.figresult.set_facecolor( color )
    G.figresult.canvas.draw() 
    for i in G.toolbar.winfo_children() : 
       i[who] = color

  def MenuBut() : 
    for i in G.MenuBar.winfo_children() : 
       i[who] = color
       BackgroundLoop(i,who=who) 

  def Rest() :
     BackgroundLoop(G.TextPaned,who=who) 

  if who == "bg" : Frames() 
  if who =="bg"  : Canvas() 
  MenuBut() 
  Rest() # textframe 
  return 

def BackgroundLoop(widget,who="bg"): # read var[0], G.fb Colorize all Label and Frame children,  
  # WIDGETS TO CHANGE, do not change others 
  if who == "bg" :  bolt=    (widget.winfo_class() == "Label")  or (widget.winfo_class()=="Frame") or (widget.winfo_class()=="Menu")  or ( widget.winfo_class() == "Checkbutton") 
  elif who == "fg" :  bolt=    (widget.winfo_class() == "Label")  or (widget.winfo_class()=="Menu")  or ( widget.winfo_class() == "Checkbutton")  or ( widget.winfo_class() == "Button")

  bolt = bolt and ( widget["bg"] !=  G.frame_title_arg["bg"] )  # not change title of frames 
  if bolt :   
    widget[who] = vars(G)[who][0]
  for i in widget.winfo_children() :   
     BackgroundLoop(i,who=who) 
  return 


def PanedConfig(arg): # change paned window canvas...
  for i in G.all_frame : 
    if "Paned" in i : 
       if W.verbose >3 : print "I change ",i
       for j in arg : 
          vars(G)[i[2:]][j] = arg[j]
  return 






def callback(event):
    if W.verbose > 3 : print "clicked at", event.x, event.y , event.widget , event.key 
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




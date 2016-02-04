import tkFont
from Tkinter import * 
import re 


import GuyVariables as G
import WorkVariables as W




def Main():
  GuiVars()         # Initialt Gui vars
  WorkVars()        # Initial WorkVar
  Preference()      # Change W.sys_argv in function of a preference, default behaviour lets say 
  TerminalDef()     # Modify with sys input 
  AfterTerminal() 



def GuiVars(): # define the shared variables for the GUI definition   
  # BUTTON WIDTH 
  G.button_width=12
  G.bu_width=12
  G.menu_button_width=8

  # GUI FORM 
  G.hidden_text_bool = 0 # we don't hide text frame by default 
  G.scale_menu_type = "column"    # can be "column" or "cascade"
  G.all_frame = []
  G.interaction_type = "tkinter" 
  #G.interaction_type = "tkinter" # Can be tkinter or shell , written interaction with the mainloop 

  # COLORS
  G.bg=["#d0d0d0"]  # light grey  # the backgroudn of abism 
  G.fg=["black"]
  import matplotlib 
  G.all_cmaps = sorted([i for i in dir(matplotlib.cm) if hasattr(getattr(matplotlib.cm,i),'N')])

  G.bu_manual_color="blue" #image parameters 
  G.menu_noise_color="grey"
  G.bu_subtract_bg_color="grey"
  G.menu_phot_color="grey"
  G.bu_close_color="grey"
  G.bu_quit_color="red"
  G.bu_restart_color= 'cyan'

  """ possible colors  : ' "#ff9090" rgb in 2 hexedecimal ; all html colors or   yellow''purple''SaddleBrown'"pink'cyan''orange' "white"  """
  """
  white :         "#ffffff"
  light grey :    "#d0d0d0"
  black :         "#000000"

  red  :          "#ff0000"  
  green :         "#00ff00"
  blue :          "#0000ff"

  yellow :        "#ffff00"
  light orange :  "#ffb33b"
  light purple :  "#a000f3"


  LIGHT 
  red : #ff7c66
  green :
  blue : 

  GREY 
  red : #e15450
  green : #64c151


  """




  # FONT 
  G.small_font= tkFont.Font(size=6)
  G.answer_font= tkFont.Font(size=8)
  G.font_param = tkFont.Font(size=11) 
  G.big_font= tkFont.Font(size=16)    


  # SCALE dic for the color and contrast
  G.scale_dic_list = [{}]
  G.scale_dic= G.scale_dic_list
  G.scale_dic[0]["cmap"]="jet"
  G.scale_dic[0]["contour"]=False
  G.scale_dic[0]["answer"]="detector"
  G.scale_dic[0]["scale_cut_type"]="sigma_clip"
  G.scale_dic[0]["sigma"]=3 

  # BOOL
  G.manual_cut_bool=0
  G.more_bool = 0 
  G.more_info_bool=0
  G.cal_bool = 0 # for calculator
  G.tutorial =0
  G.tut_type="console" # tutorial output


  # DICTIONARIES
  G.frame_title_arg = {"fg":"black","bg":"blue","font":tkFont.Font(size=8),"highlightbackground":"black","highlightcolor":"black","highlightthickness":2}


   ######################
   #   WORK Variables 
   #######################

def WorkVars() : # define the varaibles that we define the way the calculations should be runned. This is an important function of the software. 
      W.verbose=5
      W.strehl_type = 'max'  
      W.strehl={}

      W.pick_type='one'
      W.fit_type='Moffat2D'                                # FIT  TYPE
      W.phot_type = 'elliptical_aperture' #  PHOTOMETRY type
      W.noise_type = '8rects'  
      W.err_msg = [] 
      W.mode="manual"  # oppsite of automatic
      W.image_click=(0.,0.)
      W.image_release=(0.,0.)        

      W.typ={}
      
      W.same_center_var= IntVar() ; W.same_center_var.set(1)
      W.aniso_var = IntVar()      ; W.aniso_var.set(1)
      W.same_psf_var=IntVar()     ; W.same_psf_var.set(1)
      
      W.cube_bool=0
      W.cube_num=-1
      W.rect_phot_bool=0 # for rectanglephot called by command
      W.same_psf=1


def Preference(string="test1") : 
  def Append(list1,list2): # list2.append(list1) but with pass if exsit 
      for i in list1:
         i = i.replace('"','') 
	 print i 
         if (i[0] == "-") :
	   if i in list2 : 
	      pass
	   else : 
              list2.append(i) 
	      list2.append( list1[list1.index(i) +1] ) 
      return list2


  PreferenceDefined() 
  my_pref= preference[string]
  my_pref=my_pref.split(" ") 
  my_pref=[ i.replace('"','') for i in my_pref]   #destroy " because everything is string yet 
  my_pref=[ i for i in my_pref if (not re.match("^\s*$",i))  ] # detroy null entry 
 
  W.sys_argv = Append(my_pref,W.sys_argv) 
  if W.verbose >2 : print "Preferences string : ",W.sys_argv
  


def TerminalDef(): # The variables can be setted with the terminal entry command. 
  argv = W.sys_argv

  G.geo_dic = {}
  lst = [ 
    ["--verbose", W, "verbose"] , 
    ["--phot_type",W, "phot_type"], 
    ["--noise_type",W, "noise_type"], 

    ["--cmap","G","scale_dic[0]['cmap']"], #COLOR  
    ["--bg","G","bg[0]"], 
    ["--fg","G","fg[0]"], 

    ["--parent","G","geo_dic['parent']"], # GEOMETRY 
    ["--TextPaned", "G","geo_dic['TextPaned']"], 
    ["--DrawPaned","G","geo_dic['DrawPaned']" ], 
    ["--LeftTopFrame","G","geo_dic['LeftTopFrame']" ], 
    ["--LeftBottomFrame","G","geo_dic['LeftBottomFrame']" ], 
    ["--RightBottomPaned","G","geo_dic['RightBottomFrame']" ], 
    ["--ImageFrame","G","geo_dic['ImageFrame']" ], 
    ["--ResultFrame","G","geo_dic['ResultFrame']" ], 
    ["--FitFrame","G","geo_dic['FitFrame']" ], 
    ] # prefix for command line , module, variable_name  

  for i in lst : 
    if i[0] in  argv:
       if "[" in i[2] : # means we are in list or dictionary 
           spt = i[2].split("[")	
           stg =i[1] + "."+  spt[0]   # variable
	   for bla in spt[1:] : stg+= "[" + bla  # index   
	   stg+= "= argv[argv.index( i[0] ) + 1 ] " 
	   if W.verbose >3 : print "GlobalDef.Terminal geo_dic stg :" , stg 
	   exec stg in globals() , locals() 
       elif i[0]  == "--verbose" : 
         vars( i[1] )[ i[2] ]= float( argv[ argv.index( i[0] ) +1 ] ) 
       else : #including no need to be float
         vars( i[1] )[ i[2] ]= argv[ argv.index( i[0] ) +1 ]


  if "-cut_type" in  argv:
    try :  # one number -> percentage 
       G.scale_dic[0]["percent"] = float( argv[ argv.index("-cut_type")+1 ] ) 
       G.scale_dic[0]["scale_cut_type"] = "percent"
    except : # method + number
       G.scale_dic[0]["scale_cut_type"] =  argv[ argv.index("-cut_type")+1 ] 
       try : 
          tmp = float( argv[ argv.index("-cut_type")+1 ] )  
          if   G.scale_dic[0]["scale_cut_type"] == "percent": 
             G.scale_dic[0]["percent"] = tmp 
          elif   G.scale_dic[0]["scale_cut_type"] == "sigma_clip": 
             G.scale_dic[0]["sigma"] = tmp 
       except : pass


def AfterTerminal() : 
  G.paned_dic = {"sashwidth":2,"sashpad":0,"showhandle":0,"bg":"blue"} # dictionnary to call PanedWindow in Tk
  G.submenu_args={"background":G.bg[0],"foreground":G.fg[0]}
  G.bu_arg={"bd":3,"highlightcolor":G.bg[0],"padx":0,"pady":0,"highlightthickness":0}# for the borders 
  


def PreferenceDefined(): # the defined preferences
  global preference
  preference={}


  preference["test1"]="""--parent "862x743+73+31" --cmap "jet" --bg "#d0d0d0" --verbose "1.0" --TextPaned "283" --DrawPaned "575" --LeftBottomFrame "255" --LeftTopFrame "454" --ImageFrame "521" --RightBottomPaned "188" --FitFrame "275" --ResultFrame "294" """






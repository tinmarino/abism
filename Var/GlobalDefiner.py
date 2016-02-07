import tkFont
try : from Tkinter import *
except  : from tkinter import *
import re
import matplotlib

import GuyVariables as G
import WorkVariables as W


# TODO entirely remove this file

def Main():
  GuiVar()         # Initialt Gui vars
  WorkVar()        # Initial WorkVar
  Preference()      # Change W.sys_argv in function of a preference, default behaviour lets say, the command line are stored in PreferenceDefined
  TerminalVar()     # Modify with sys input
  AfterTerminal()

  LinkedColor() # For G and called with BgCl()



def GuiVar(): # define the shared variables for the GUI definition

  # VERSION
  #G.version = "%.2f" % float( W.path.split("/")[-1].replace("Abism","") )

  # BUTTON WIDTH
  G.button_width        =12                         # the width of the standard buttons
  G.bu_width            =12                         # THE SAME
  G.menu_button_width   =8                          # Size of menu buttons

  # GUI FORM
  G.hidden_text_bool    = 0                         # we don't hide text frame by default, the text framme is the output frame on the left
  G.scale_menu_type     = "column"                  # can be "column" or "cascade"
  G.all_frame           = []                        # all frames will be here to change color
  G.interaction_type    = "tkinter"                 # Can be tkinter or shell , written interaction with the mainloop
  G.last_top_size       = 300

  # GEO DIC
  G.geo_dic             = {}                        # geometry dictionnay
  G.geo_dic['ResultFrame']=  300



  # COLORS
  G.bg                  = ["#d0d0d0"]               # light grey  # the backgroudn of abism
  G.fg                  = ["black"]                 # foreground, the color of the font
  G.all_cmaps = sorted([i for i in dir(matplotlib.cm) if hasattr(getattr(matplotlib.cm,i),'N')]) # inclouding inverse

  # BUTTONS COLORS
  G.bu_manual_color     ="blue"                     # Color of buttons
  G.menu_noise_color    ="grey"
  G.bu_subtract_bg_color="grey"
  G.menu_phot_color     ="grey"
  G.bu_close_color      ="grey"
  G.bu_quit_color       ="red"
  G.bu_restart_color    = 'cyan'



  # FONT
  G.small_font          = tkFont.Font(size=6)
  G.answer_font         = tkFont.Font(size=10)   # all answer in AnswerFrame
  G.strehl_font         = tkFont.Font(size=12)  # just strehl answer
  G.warning_font        = tkFont.Font(size=12)  # just strehl answer
  G.font_param          = tkFont.Font(size=11)  #Image parameters
  G.big_font            = tkFont.Font(size=16)


  # SCALE dic for the color and contrast
  G.scale_dic_list = [{}]
  G.scale_dic= G.scale_dic_list
  G.scale_dic[0]["cmap"]    = "jet"
  G.scale_dic[0]["contour"] = False
  G.scale_dic[0]["answer"]  = "detector"
  G.scale_dic[0]["percent"] = 99.99
  G.scale_dic[0]["scale_cut_type"]="sigma_clip"
  G.scale_dic[0]["sigma"]   = 3
  G.scale_dic[0]["stretch"] = "linear"

  # BOOL
  G.manual_cut_bool = 0
  G.more_bool       = 0
  G.more_info_bool  = 0
  G.cal_bool        = 0                             # Is the calculator opened yet ?
  G.tutorial        = 0                             # Is the tutorial opened yet ?
  G.tut_type        = "console"                     # tutorial output
  G.toolbar_fit_bool = False
  G.toolbar_result_bool = False
  G.manual_back_bool = False
  G.label_bool      = True                          # the labels on the left, when open image, this is set to true
  G.result_bool     = True                          # show the full results frame
  G.top_bool        = True
  G.in_arrow_frame  = None                          # no body in lefftoparrowframe

  # CLASS
  G.tkvar = G.VoidClass() #(we save the tkvariables ) # it may be changed see image parameters
  G.tkentry = G.VoidClass()


  # DICTIONARIES
  G.paned_dic = {   "sashwidth":2,                  # The sas is the little between windows "glissiere", to resize
                    "sashpad":0,
                    "showhandle":0,
                    "bg":"blue",
		            "borderwidth":0,
                    "sashrelief":RAISED,
		        }                                   # dictionnary to call PanedWindow in Tk


  G.frame_title_arg = {
    "fg":"blue","bg":"white","font":tkFont.Font(size=10),
    "highlightbackground":"black","highlightcolor":"black","highlightthickness":1,
    "padx":3,
       }

  G.sub_paned_arg = { "minsize":22, "pady":0,"sticky":"nsew" }


   ######################
   #   WORK Variables
   #######################



def WorkVar() : # define the varaibles that we define the way the calculations should be runned. This is an important function of the software.
      W.verbose=1

      W.sys_argv = sys.argv

      class tmp: pass
      W.tmp = tmp() # this is for the temporary variables to pass from one function to an other. Like W.tmp.lst... carrefull

      W.imstat = G.VoidClass()
      W.image_name='no_image_name'
      W.strehl_type = 'max'
      W.strehl={}


      W.type={}
      W.type["pick"]='one'
      W.type["fit"]='Moffat2D'                                # FIT  TYPE
      W.type["phot"] = 'elliptical_aperture' #  PHOTOMETRY type
      W.type["noise"] = 'elliptical_annulus'
      W.type["aperture"] = "fit"
      W.err_msg = []
      W.mode="manual"  # oppsite of automatic
      W.image_click=(0.,0.)
      W.image_release=(0.,0.)


      W.same_center_var= IntVar() ; W.same_center_var.set(1)
      W.aniso_var = IntVar()      ; W.aniso_var.set(1)
      W.same_psf_var=IntVar()     ; W.same_psf_var.set(1)

      W.cube_bool=0
      W.cube_num=-1
      W.rect_phot_bool=0 # for rectanglephot called by command
      W.same_psf=1





def TerminalVar(): # The variables can be setted with the terminal entry command.
  argv = W.sys_argv



  lst = [
    ["--verbose", W, "verbose"] ,
    ["--phot_type","W", "type['phot']"],
    ["--noise_type","W", "type['noise']"],

    ["--bg","G","bg[0]"],
    ["--fg","G","fg[0]"],

    # SCALE DIC
    ["--cmap","G","scale_dic[0]['cmap']"], #COLOR
    ["--scale_dic_stretch","G",'scale_dic[0]["stretch"]' ],
    ["--scale_dic_scale_cut_type","G",'scale_dic[0]["scale_cut_type"]' ],
    ["--scale_dic_percent","G",'scale_dic[0]["percent"]' ],

    # FRAMES
    ["--parent","G","geo_dic['parent']"],
    ["--TextPaned", "G","geo_dic['TextPaned']"],
    ["--DrawPaned","G","geo_dic['DrawPaned']" ],
    ["--LabelFrame","G","geo_dic['LabelFrame']" ],
    #["--LeftTopFrame","G","geo_dic['LeftTopFrame']" ],
    # I commented that because it gets in conflict with result
    ["--LeftBottomFrame","G","geo_dic['LeftBottomFrame']" ],
    ["--RightBottomPaned","G","geo_dic['RightBottomFrame']" ],
    ["--ImageFrame","G","geo_dic['ImageFrame']" ],
    ["--ResultFrame","G","geo_dic['ResultFrame']" ],
    ["--FitFrame","G","geo_dic['FitFrame']" ],

    ["--ImageName",W,"image_name"],
    ["-i",W,"image_name"],
    ["-p",W,"path"],

    ] # prefix for command line , module, variable_name



  for i in lst :
    if i[0] in  argv:
       if "[" in i[2] : # means we are in list or dictionary
           spt = i[2].split("[")
           stg =i[1] + "."+  spt[0]   # variable
	   for bla in spt[1:] : stg+= "[" + bla  # index
	   try :
	     stg2 = stg + "=float( argv[argv.index( i[0] ) + 1 ])  "
	     if W.verbose >3 : print "GlobalDef.Terminal geo_dic stg :" , stg
	     exec stg2 in globals() , locals()
	   except :
	     stg2 =stg +  "= argv[argv.index( i[0] ) + 1 ] "
	     if W.verbose >3 : print "GlobalDef.Terminal geo_dic stg :" , stg
	     exec stg2 in globals() , locals()

       else : #including not in a dict to be float
	 try :
           vars( i[1] )[ i[2] ]= float( argv[ argv.index( i[0] ) +1 ] )
         except :
           vars( i[1] )[ i[2] ]= argv[ argv.index( i[0] ) +1 ]


  # IMAGE_NAME
  W.image_name="no_image_name"
  for i in W.sys_argv[::-1] :
     if i.find(".fits") != -1 :
        W.image_name = i
	break


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
  return


def LinkedColor() :
  # BUTTON
  G.bu_arg={"bd":3,"highlightcolor":G.bg[0],"padx":0,"pady":0,"highlightthickness":0,"fg":G.fg[0]}# for the borders
  # LABEL
  G.lb_arg={"bg":G.bg[0], "fg":G.fg[0] }
  # MENU
  G.me_arg={"bg":G.bg[0], "fg":G.fg[0] }
  G.submenu_args={"background":G.bg[0],"foreground":G.fg[0]}
  # ENTRY
  G.en_arg={"bg":"white","fg":G.fg[0],"bd":0}

  # FRAME
  G.fr_arg={"bg":G.bg[0]}





def Preference(string="test1") :
  def Append(list1,list2): # list2.append(list1) but with pass if exsit
      for i in list1:
         i = i.replace('"','')
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

def PreferenceDefined(): # the defined preferences
  global preference
  preference={}


  preference["test1"]="""--parent "862x743+73+31" --cmap "jet" --bg "#d0d0d0" --verbose "1.0" --TextPaned "283" --DrawPaned "575" --LeftBottomFrame "255" --LeftTopFrame "454" --ImageFrame "521" --RightBottomPaned "188" --FitFrame "275" --ResultFrame "294" """






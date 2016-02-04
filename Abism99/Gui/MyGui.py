import matplotlib
import pyfits
import numpy as np

from Tkinter import *
from tkFileDialog import askopenfilename
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas

# Gui
import InitGui as IG  # draw the GUI
import Pick
import DraggableColorbar
import NormalizeMy
import AnswerReturn as AR 
#Plugin
import ReadHeader as RH    


# ArrayFunction
import Scale
import Stat   
import ImageFunction as IF  # Function on images
import BasicFunction as BF  # 2D psf functions


# Variables
import GuyVariables as G
import WorkVariables as W



# MAYBE not usefull bite  
#import  multiprocessing 
import threading 
import select 
from time import sleep 
import traceback 

from matplotlib import pyplot as plt 
import matplotlib.font_manager as fm

import warnings 

#class MyWindow:
def MyWindow():

  # Tk 
  G.parent = Tk()
  import GlobalDefiner  ; GlobalDefiner.Main() 

  IG.WindowInit()
  LaunchImageInit() # set the G.fig = plt.figure() and its marge  

  # Shell 
  #InteractiveShell.Main() 
  
  G.parent.mainloop()



def LaunchImageInit():
  def Create(): 
    G.fig=matplotlib.figure.Figure()#figsize=(6,6))
    G.figfit=matplotlib.figure.Figure(figsize=(5,2.5))         #figsize=(4,1), dpi=100
    G.figresult=matplotlib.figure.Figure(figsize=(3,2.5)) 
  def Size() : 
    G.fig.subplots_adjust(left=0.08, right=1.00, top=0.95, bottom=0.05)
    G.figfit.subplots_adjust(left=0.15, right=0.9, top=1, bottom=0.2)
    G.figresult.subplots_adjust(left=0.1, right=0.9, top=1, bottom=0)
  def Color() : 
    G.fig.set_facecolor(G.bg[0])
    G.figfit.set_facecolor(G.bg[0])
    G.figresult.set_facecolor(G.bg[0])
  def Canvas() :   
     #############
     # IMAGE 
     G.ImageCanvas=FigureCanvas(G.fig,master=G.ImageFrame)      
     G.ImageCanvas.get_tk_widget()["bg"] = G.bg[0]
     G.ImageCanvas.get_tk_widget()["highlightthickness"]=0 # to have no little border use to know if I have focus
     G.ImageCanvas.get_tk_widget().pack(side=TOP,expand=0,fill=BOTH)
     G.all_frame.append("G.ImageCanvas.get_tk_widget()") 
     Label(G.ImageFrame,text="Image",**G.frame_title_arg).place(x=0,y=0) 

     ###########
     # TOOLBAR 
     #G.ToolbarFrame=Frame(G.ImageFrame,bg=G.bg[0])
     #G.ToolbarFrame.pack(side=TOP,expand=1,fill=BOTH)
     #G.all_frame.append("G.ToolbarFrame") 
     G.toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2TkAgg(G.ImageCanvas,G.ImageFrame )
     G.toolbar["bg"] = G.bg[0]
     for i in G.toolbar.winfo_children() : 
       i["bg"] = G.bg[0]
     G.all_frame.append("G.toolbar") 

     ########"
     #  FIT
     G.dpfit=FigureCanvas(G.figfit,master=G.FitFrame)
     G.dpfit.get_tk_widget()["bg"] = G.bg[0]
     G.dpfit.get_tk_widget()["highlightthickness"]=0
     G.dpfit.get_tk_widget().pack(expand=0,fill=X)
     G.all_frame.append("G.dpfit.get_tk_widget()") 
     Label(G.FitFrame,text="1d shape",**G.frame_title_arg).place(x=0,y=0) 

     #######
     # STAR 
     G.dpresult=FigureCanvas(G.figresult,master=G.ResultFrame)
     G.dpresult.get_tk_widget()["bg"] = G.bg[0]
     G.dpresult.get_tk_widget()["highlightthickness"]=0
     G.dpresult.get_tk_widget().pack(expand=0,fill=X)        
     G.all_frame.append("G.dpresult.get_tk_widget()") 
     Label(G.ResultFrame,text="2d shape",**G.frame_title_arg).place(x=0,y=0) 

  def Call() : 
    if W.image_name!="no_image_name" : # in case the user launch the program without giving an image as arg
      InitImage()
  Create() ; Size() ; Color() ;Canvas() ;  Call()  
  return 

def __automatic__():   # Not finished, not called 
  center,pixel_max= IF.GoodPixelMax(W.Im0,'bidon')
  #FindStarCenter
  if W.verbose > 3 : print 'center,pixel_max : ',center,pixel_max
  #FWHM
  FWHM= IF.FWHM(W.Im0,center)
  if W.verbose > 3 : print FWHM
  StrehlMeter(center,10*FWHM)    #the image is in G
      




def ScienceVariable():
  IG.ResetLabel()                                                     #  WARNINGS
  W.sort = W.Im0.flatten() 
  W.sort.sort() 
  IG.LabelDisplay() 
  if (W.head.diameter==99. or  W.head.wavelength==99. or W.head.obstruction==99. or W.head.pixel_scale==99.):
     Label(G.LabelFrame,foreground='red',bg=G.bg[0], 
                 text="WARNING : \n Cannot read from header. \n Please enter image parameters ").pack(side=BOTTOM)
  else :  
    G.bite =  Label(G.LabelFrame,foreground='blue', bg=G.bg[0] , 
              text="Ok : Image Parameter \n readen from header. \n Pick a star  \n ").pack(side=BOTTOM)
    if W.head.wavelength*1e-6/W.head.diameter/(W.head.pixel_scale/206265)<2 : 
          Label(G.LabelFrame,foreground='red',bg= G.bg[0], 
            text="WARNING : Bad pixelisation \n Use FWHM better than Strehl  \n ").pack(side=BOTTOM)
    

def Histopopo():
      if G.tutorial:
               text="This is drawing the histogram of pixel values. It may be usefull."
               text+="\n\nProgrammers, We can implement a selection of the scale cut of the image with a dragging the vertical lines., with a binning of the image, this could even be in real time." 
               TutorialReturn({"title":"Histogram",
               "text":text,
               })
               return    
      matplotlib.font_manager.FontEntry(fname="DejaVuSans") 
      font0= matplotlib.font_manager.FontProperties() 
      G.figfit.clf()
      G.ax2 = G.figfit.add_subplot(111)

      #plt.rcParams['mathtext.fontset'] = "regular"
      #plt.rcParams['mathtext.default']="regular"
      font = {'family':'sans-serif','sans-serif':['Helvetica'],
          'weight' : 'normal', 'size' : 12}
      #matplotlib.rc('font', **font)
      G.ax2.set_xticklabels(G.ax2.get_xticks(), font)
      G.ax2.set_xticklabels(G.ax2.get_xticks(), font)
      G.ax2.axvline(x=G.scale_dic[0]["min_cut"],color='black',linestyle='-',linewidth=2)#,label='Encircled Energy')
      G.ax2.axvline(x=G.scale_dic[0]["max_cut"],color='black',linestyle='-',linewidth=2)#,label='Encircled Energy')      
      #G.ax2.set_title("HISTOGRAM")
      G.ax2.set_xticklabels(W.sort, fontproperties = fm.FontProperties(family ="Helvetica")) 
      G.hist = G.ax2.hist(W.sort,100, log=True) # n, bin, patches 

       ## LABELS Because pb of font 
      #G.ax2.set_xticks((  0,np.max(G.hist[0]) ))
      #G.ax2.set_yticks((  0,np.max(W.Im0) ))

      warnings.simplefilter("ignore")
      G.figfit.canvas.draw()      
      warnings.simplefilter("default")
      return
    
    
def Open():
  if G.tutorial:
               text="A click on this button will open a window. You need to select a FITS image to load with Abism. This is an other way to load an image, the first one is to load it directly in the script by bash Abism.sh [-i] image.fits."
               TutorialReturn({"title":"Open an image file",
               "text":text,
               })
               return   
  initialdir = "/".join(  W.image_name.split("/")[:-1]   ) # the same dir as the image 
  String = askopenfilename(title="Open a FITS image",filetypes=[("fitsfiles","*.fits"),("allfiles","*")], initialdir=initialdir)
  if type(String) is str :
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
        

def Quit():
  if W.verbose > 0 : print "Closing Abism, Goodbye. Come back soon.\n_________________________________________________________________________\n\n\n"
  import sys
  sys.exit(1)
  # other ways to destroy : #G.parent.destroy() #raise SystemExit

def Restart():
      if G.tutorial:
               text="Pushing this button will close ABISM and restart it the same way it was launch before."
               text+="\n\nProgrammers: this is made to reload the Software if a modification in the code were made."
               TutorialReturn({"title":"Restart",
               "text":text,
               })
               return     
    
      #################
      ## prepare arguments 
      arg = W.sys_argv 
       
      my_cmap= G.scale_dic[0]["cmap"] 
      try : my_cmap = G.cbar.cbar.get_cmap().name  
      except : pass 
      for i in [   ["--parent",G.parent.geometry()]  ,  
	       ["--cmap",my_cmap ], 
               ["--bg",G.bg[0]], 
	       ["--verbose", W.verbose ],  
               ["--TextPaned",G.TextPaned.winfo_width()]   ,  
	       ["--DrawPaned",G.DrawPaned.winfo_width()] , 
               ["--LeftBottomFrame",G.LeftBottomFrame.winfo_height()], 
               ["--LeftTopFrame",G.LeftTopFrame.winfo_height()], 
               ["--ImageFrame",G.ImageFrame.winfo_height()], 
               ["--RightBottomPaned",G.RightBottomPaned.winfo_height()], 
               ["--FitFrame",G.FitFrame.winfo_width()], 
               ["--ResultFrame",G.ResultFrame.winfo_width()], 
	       ] : 
        if not i[0] in arg : 
           arg.append(i[0]) 
           arg.append( '"'+str(i[1] ) +'"' ) 
        else : arg[arg.index(i[0])+1] =  '"' +  str(i[1]) + '"' 

      # IMAGE_NAME 
      matching = [s for s in arg if ".fits" in s]
      if len(matching) >0 : arg[arg.index(matching[0])] = W.image_name 
      else : arg.insert(1,W.image_name)
      

      ###########
      # PREPARE STG 
      stg =   "python "  
      for i in arg :
         stg +=" "+  i 
      stg+= " &"
      if W.verbose > 0 : print "\n\n\n______________________________________\nRestarting ABISM with command:\n"+stg + "\nplease wait" 

      ##########
      # DESTROY AND LAUNCH 
      import sys
      from os import system 
      G.parent.destroy()
      #stg+=" &"
      system(stg)
      sys.exit(1) 
  

def Clear():
  if G.tutorial:
               text="This button will clear the image frames and reinitiate its. It was made in order to delete some arrows, for example with the pick many mode."
               TutorialReturn({"title":"Clear",
               "text":text,
               })
               return    
#try : 
  #G.MainPaned.forget(G.DrawPaned) 
  #IG.DrawingFrameMaker()  
  try :G.AnswerFrame.destroy() # in cas this doesn't exist 
  except : pass	
#except : pass	
  LaunchImageInit()
  return 


def DisplayHeader():   # for user
  if G.tutorial:
               text="A basic Window to display the header. There is no shortcut to find sa string right now"
               TutorialReturn({"title":"Display Header",
               "text":text,
               })
               return     
  root = Tk()
  root.title('header('+W.image_name+')')
  root.geometry("600x700+0+0")
  text=Text(root,background='white')   #,height=10,width=50
  text.insert(INSERT, W.hdulist[0].header)      
  # put a scroll bar in the frame
  scroll=Scrollbar(root)
  text.configure(yscrollcommand=scroll.set)
  #pack everything
  text.pack(side=LEFT,expand=True,fill=BOTH)
  scroll.pack(side=RIGHT,fill=Y)
  scroll.config(command=text.yview)
  root.mainloop()
  return 
        

def Save(first=1): # first time you save, to prin header and staff 
  try : 
    from os import popen
    date=popen("date").read().split()
    pwd=popen("pwd").read() 
  except : 
    date=["day","month","day","time","pff","year"]
    pwd="no_pwd"
  archive = "Abm_" + W.image_name.split('/')[-1].split('.fits')[0] 
  try : archive+= "_"+date[-1]+"_"+date[1]+"_"+date[2]+"_"+date[3]+".txt"
  except : pass
  exit = open(archive,'a')
  if W.verbose >0 : print "Writting files in " + archive
  if W.verbose >0 : print "in directory : " + pwd
  exit.write("#Abism -> data from :"+ W.image_name)
  exit.write("#######\n----->1/ Header \n still missing in abism...")
  exit.write( "#######\n----->2/ Strehl Output : \n")
  try : aa=W.answer_saved
  except : W.answer_saved=W.answer
  try : # in case we just took PickOne and cannot sort 
   for key in sorted(W.answer_saved, key = lambda x: int(x.split(".")[-1])):
     exit.write(key + " " + str(W.answer_saved[key])+ '\n') 
  except :
   for key in W.answer_saved : 
     exit.write(key + " " + str(W.answer_saved[key])+ '\n') 
  exit.write("\n \n")
  exit.close()
  return
    




def CubeDisplay(String):
      if String =='+': W.cube_num+=1
      if String =='-': W.cube_num-=1
      if String =='0': W.cube_num=float(G.cube_var.get())
      G.cube_var.set(W.cube_num)
      InitImage()
      ScienceVariable()
      return

    
def Tutorial():                                     # In help menu
      G.help=True
      G.tutorial= not G.tutorial 
      IG.ResetLabel()
      Label(G.LabelFrame,foreground='blue',
        text="Read the terminal \n or README file \n in Abism folder").pack(side=BOTTOM)
      TutorialReturn({"title":"Tutorial","text":"Click on the buttons to get the explanation of their function"}) 
      return


def TutorialReturn(dic): #dic contains title, text   , made for tutorail but can return los of staff with a nice terminal output      
  default_dic = {"title":"","text":""}
  default_dic.update(dic) ; dic = default_dic

  if G.tut_type == "console":
    from subprocess import call 
    tut_sh = W.path+"/write_tutorial.sh"
    call("bash " +tut_sh + " '"+  dic["title"] +"' '" + dic["text"]+ "' " ,shell=True )   
 
def my_raw_input(message):
    sys.stdout.write(message)

    select.select([sys.stdin], [], [])
    return sys.stdin.readline()

def Run(String):
  #String = String.get("1.0",END)
  if String == "help" : 
    stg = "quit() #to disable intercative shell "
    stg+="\nimport sys ; sys.exit() # to kill Abism "
    print stg 
  exec String in globals()# no in local to store all variables, locals()      
  out=open(W.path+"/Plugin/old_command.txt","a") 
  out.write(String+"***************************\n")
  out.close()

def Hide(hidden=0) :
  if W.verbose > 3 : print "My hidden", hidden 
  if G.hidden_text_bool : 
    G.MainPaned.sash_place(0,G.hidden_frame_size,0)
    G.bu_hide["text"]=u'\u25c2' # rigth arrow 

       

  else : 
    G.hidden_frame_size = G.MainPaned.sash_coord(0)[0] # bakcup the x position of the sash 
    G.MainPaned.sash_place(0,10,0)
    G.bu_hide["text"]=u'\u25b8' # left arrow 
  G.hidden_text_bool  = not G.hidden_text_bool  

def daemon() :
    if W.verbose >3 : print threading.currentThread().getName(), 'Starting'
    #p = multiprocessing.current_process()
    #sys.stdout.flush()
    while 1 :  
      sleep(2)
      fct() 
    if W.verbose >3 : print 'Exiting :'
    #sys.stdout.flush()
  

def fct() : 
        a= raw_input("Abism listen >")  
	#Run(a)
	G.TextPaned["bg"]="green"
	print "it works " 
	print a 
	#sleep(1)
	#G.parent.after(2000,fct)  


def PythonConsole():
   if G.tutorial : 
                   TutorialReturn({"title":"Python Console",
                   "text":"A text window is opened, write python command and click on run. These commands know the variables presents in MyGui.py and the module it imports (like WorkVariable, W or GuiVariable, G) , the secret is just a: \n exec string in globals() locals(); \n\nTip : To know if a variable is in W or G : \nfor i in vars(W) : \n  if 'pixel_scale' in i : print i, vars(i) \n          ",
                   }) 
                   return 


   if G.interaction_type == "shell" : # in console  
      import threading
      import time
      
      def worker():
          print "___________________________________________\n",threading.currentThread().getName(), "Starting------------------\n---give me a python command or 'quit','break' to break the loop, 'help' maybe"  
          while 1 :  
            time.sleep(1)
	    try : 
                key_input= my_raw_input("-->")
		if (key_input == "quit")  or (key_input == "break"): break 
                else : 
		   try : 
		      arith = eval(key_input) 
		      print arith
                   except : 
		      exec key_input in globals() 
            except Exception, err:
                traceback.print_exc()
                print "I tried, I didn't succed command :, try again " 
		if "key_input" in vars() : 
		   print "You asked for : "  +'"'+key_input+'"'
	    
          print threading.currentThread().getName(), 'Exiting, feel free.'
      
      
      def Bite() :
         w = threading.Thread(name='console_tread', target=worker)
         w.start()
      Bite() 

   else : # including interaction = tkinter 
      window_run = Tk()
      window_run.title('Python console')   
      #window_run.geometry("+0+0")
      def MyText(frame,new=0): # if not new, Clear it 
        if not new : G.text_user.pack_forget()
	  #text= '# Hey man, this is for programmers. \n# This basically uses exec function to get into the code. \n\nfor key in W.answer : print key,W.answer[key] '
	text=""
        G.text_user = Text(frame,bg=G.bg[0])
        G.text_user.insert(INSERT,text)      
        G.text_user.pack(side=TOP,fill=BOTH,expand=True)
        G.text_user.focus_force()
        return G.text_user

      # TEXT 
      frame=Frame(window_run)
      frame.pack(side=TOP,fill=BOTH,expand=True)
      MyText(frame,new=1)


      # BUTTON
      bu_frame = Frame(window_run,bg="purple")
      bu_frame.pack(side=BOTTOM,expand=0,fill=X )
      but_list = []
      but_list.append(   Button(bu_frame,text="Run", background="DeepSkyBlue", 
                  command=lambda : Run(G.text_user.get("1.0",END) )  )    )
      but_list.append(   Button(bu_frame,text="Clear", command=lambda: MyText(frame))
                     ) 
      but_list.append(   Button(bu_frame,text='QUIT',background = 'red',  
                  command=window_run.destroy ) 
		     )

      for bu in but_list : bu.pack(side=LEFT,expand=1,fill=X)	

      window_run.mainloop()
      return


def SubstractBackground():
        if G.tutorial:
               text="Choose a FITS image tho subtract to the current image to get read of the sky value or/and the pixel response. This is a VERY basic task that is only subtracting 2 images. It could be improved but image reduction is not the goal of ABISM."
               TutorialReturn({"title":"Subtract A background image",
               "text":text,
               })
               return    
        String = askopenfilename(filetypes=[("fitsfiles","*.fits"),("allfiles","*")])
        W.image_bg_name = String     # image_background_name 
        W.hdulist_bg = pyfits.open(String)
        W.Im0_bg = W.hdulist_bg[0].data
        if (not W.Im0.shape == W.Im0_bg.shape) and (W.verbose>0 )  : print 'ERROR : Science image and Background image should have the same shape' 
        else : 
          W.Im0 -=  W.Im0_bg
          InitImage(load=0)
        return







def FitType(name):  # strange but works
      if name=="tutorial":
                 if G.tutorial:
                             text="\nDifferent fit types: A Moffat fit is setted by default. You can change it. Gaussian, Moffat,Bessel are three parametrics psf. Gaussian hole is a fit of two Gaussians with the same center by default but you can change that in more option in file button. The Gaussian hole is made for saturated stars. It can be very useful, especially because not may other software utilize this fit.   "
                   	     text+="\n\nWhy is the fit type really important? The photometry and the peak of the objects utilize the fit. For the photometry, the fit measure the aperture and the maximum is directly taken from the fit. So changing the fit type can change by 5 to 10% your result."
                   	     text+="\n\nWhat should I use? For strehl <10% Gaussian, for Strehl>50% Bessel, between these, Moffat. "
                   	     text+="\n\nProgrammers: Strehl@MyGui.py calls SeeingPSF@ImageFunction.py which calls BasicFunction.py.\n To do : fastly analyse the situation and choose a fit type consequently."  
                   	     TutorialReturn({"title":"Choose Fit Type",
                   	     "text":text,
                   	     })
                   	     return     
		 else : return # include no G.tutorial
      W.fit_type = name 
      try :   
         if W.aniso_var.get() ==0 : 
            W.fit_type =W.fit_type.replace('2D','')
         elif W.aniso_var.get() ==1  and not '2D' in W.fit_type  : W.fit_type +='2D'
      except  :
         if W.fit_type.find('2D')==-1 : W.fit_type+='2D'
      if not W.fit_type.find('None')==-1 : W.fit_type ='None'

       # Saturated
      if "Gaussian_hole" in W.fit_type :
           try: 
             if W.same_center_var.get()==0 : 
               W.fit_type =W.fit_type.replace('same_center','')
               if W.verbose >0 : print " same_center : We asssume that the saturation is centered at the center of th object"
             elif not 'same_center' in W.fit_type :
               W.fit_type+="same_center" 
               if W.verbose >0 : print "not same_center : We asssume that the saturation isn't centered at the center of th object"
           except :
              if not 'same_center' in W.fit_type :W.fit_type+="same_center"
      if W.verbose >0 : print 'Fit Type = ' +W.fit_type 

        # same psf 
      if W.same_psf_var.get() ==0 : 
        W.same_psf=0
        if W.verbose >0 : print " same_psf : We will fit the binary with the same psf"
      elif W.same_psf_var.get() ==1 :
        W.same_psf=1
        if W.verbose >0 : print " not same_psf : We will fit each star with independant psf"  
      return


def WVarSet(key,value): # change the value of a WorkVariable
  vars(W)[key]=value
  if W.verbose >0 : print "-----> WVarSet : Change the value of W."+key+" to ",value 
  return
      

def GetIntensity(event): # configure text in Label z and zmax where the mouse is 
      #if W.verbose >0 : print 'mouse',event.xdata,event.ydata, W.Im0[event.ydata][event.xdata]
      if not (event.xdata==None or event.ydata==None):
	try : 
	  G.LabelZ.configure(text='z='+"%.0f"% (W.Im0[event.ydata][event.xdata])+' ',font=G.small_font)
	  G.LabelL.configure(text='Max='+
	               "%.0f"%(  IF.GoodPixelMax(W.Im0,r=(event.ydata-10,event.ydata+11,event.xdata-10,event.xdata+11))[1] ) 	                      
	                       +' ' ,font =G.small_font)
        except : 
	  W.err_msg.append("Cannot get local max in toolbar frame")
      return 

def DrawCompass():  
    if W.verbose >3 : print "MG, what do I know from header", vars(W.head)
    if not ( ("CD1_1" in vars(W.head)) and  ("CD2_2" in vars(W.head) ) ) :
      if W.verbose > 0 : print "WARNING WCS Matrix not detected, I don't know where the north is."
      W.head.CD1_1 = W.head.pixel_scale *3600
      W.head.CD2_2 = W.head.pixel_scale *3600 
    
    if not ( ("CD1_2" in vars(W.head)) and  ("CD2_1" in vars(W.head) ) ) :
      W.head.CD1_2,W.head.CD2_1 = 0,0 
    
    north_direction = [-W.head.CD1_2,-W.head.CD1_1] / np.sqrt( W.head.CD1_1**2 + W.head.CD1_2**2 )  
    east_direction = [-W.head.CD2_2,-W.head.CD2_1] / np.sqrt( W.head.CD2_1**2 + W.head.CD2_2**2 )  

    coord_type="axes fraction"
    if coord_type == "axes fraction" :    # for the arrow in the image, axes fraction 
        arrow_center=[0.95,0.1] # in figura fraction
          # -  because y is upside down       think raw collumn 
        north_point = arrow_center+north_direction/10 
        east_point  = arrow_center+east_direction/15

    #else : 
    elif coord_type == "data" : # for the arrow IN the image coords can be "data" or "figure fraction"
       arrow_center=[0.945*len(W.Im0) , 0.1*len(W.Im0) ] # in figure fraction
         # -  because y is upside down       think raw collumn 
       north_point = [ arrow_center+  north_direction/20*len(W.Im0)  , arrow_center-north_direction/20*len(W.Im0)  ]
       east_point  = [north_point[1] + east_direction/20*len(W.Im0)   , north_point[1] ]
    if W.verbose > 3 : print "north",  north_point, east_point,arrow_center,  north_direction, east_direction


    #coord_type="figure fraction"
    #################
    # 2/ DRAW        0 is the end of the arrow 
    G.north = G.ax1.annotate("",
        xy=arrow_center, xycoords=coord_type, # we invert to get the text at the end of the arrwo
        xytext=north_point, textcoords=coord_type,color="purple", 
        arrowprops=dict(arrowstyle="<-",facecolor="purple",edgecolor="purple"),
                       # connectionstyle="arc3"),
        )
    G.east = G.ax1.annotate("",
        xy= arrow_center , xycoords=coord_type,
        xytext=east_point, textcoords=coord_type,color="red", 
        arrowprops=dict(arrowstyle="<-",facecolor='red',edgecolor='red'),
                        #connectionstyle="arc3"),
        )
    G.north_text=G.ax1.annotate("N",xy=north_point,textcoords=coord_type,color='purple')
    G.east_text=G.ax1.annotate("E",xy=east_point,textcoords=coord_type,color='red')

    W.north_direction=north_direction
    W.east_direction=east_direction
def RemoveCompass():
   G.ax1.texts.remove(G.north)
   G.ax1.texts.remove(G.east)
   G.ax1.texts.remove(G.north_text)
   G.ax1.texts.remove(G.east_text)       


def InitImage(): # Clear : opened by clear button, or for the first time, Load : load the image. 
  ######################
  ##       CLEAR OLD  CANVAS and Colorbar WITH CLF  
  try :  # not done if one image was previously loaded , means if used "open" button
    G.cbar.disconnect() 
    del G.cbar
    G.fig.clf() 
  except : 
    if W.verbose >2 : print "InitImage, cannot delete cbar"


  W.hdulist= pyfits.open(W.image_name)
  W.Im0=W.hdulist[0].data  #define the 2d image : W.Im0 
  W.Im0[np.isnan(W.Im0)]=0 #delete the np.nan
  RH.EsoHeader(W.hdulist[0].header)                                       # HEADER
      


   ####################
   ### CUBES         ##
   ####################
  if (len(W.hdulist[0].data.shape)==3):# for CUBES
    if (abs(W.cube_num)<len(W.hdulist[0].data[:,0,0])) : # should run if abs(G.cube_num)<len(G.hdulist)  
        if W.cube_bool==0 :# to load cube frame
          W.cube_bool=1
          IG.Cube()                  #To display cubes

        W.Im0=W.hdulist[0].data[W.cube_num]#,:,G.cube_num]          #in case we are in a cube
    elif W.verbose >0  : print 'ERROR InitImage@MyGui.py :'+ W.image_name +' has no index ' +str(W.cube_num)
   
  else :  # including image not a cube, we try to destroy cube frame
    W.cube_bool=0
    try : IG.Cube()
    except : pass # if cubeFrame not defined 

  

   ##############################
   ##   READ (+BPM)  THE VARIABLES     ##
   ##############################
  ScienceVariable()
  if "bpm_name" in vars(W):
    hdu      = pyfits.open(name) 
    W.Im_bpm = hdu[0].data 
  else : 
    W.Im_bpm = 0*W.Im0 + 1  

   #############
   ## LABEL ESO 
   #############

  IG.ResetLabel() 
  IG.LabelDisplay() 


   ######################
   ###  SCALE  image 
   ########################
  G.current_image= W.Im0.astype(np.float16) # much faster also draw_artist can help ?  
  if W.verbose > 3 : print "dic init" , G.scale_dic[0]
  Scale(dic=G.scale_dic[0], load=1) # not to draw the image. 

  ####################"
  #     DISPLAY  the image HERE the origin = lower change everything in y 
  G.ax1=G.fig.add_subplot(111)        
  drawing= G.ax1.imshow(G.current_image,vmin=G.scale_dic[0]["min_cut"],
    vmax=G.scale_dic[0]["max_cut"],cmap=G.scale_dic[0]["cmap"],  origin='lower' )
       

  #############################
  #   COMPASS
  ############################
  try :RemoveCompass() 
  except : pass    
  if W.verbose > 3 : print "I am still ok1 " 
  DrawCompass()
 
  if W.verbose > 3 : print "I am still ok 2" 


  G.toolbar.update()
  ####
  # COLORBAR 
  G.cbar= G.fig.colorbar(drawing,pad = 0.02)
  #G.cbar.set_norm(NormalizeMy.MyNormalize(vmin=image.min(),vmax=image.max(),stretch='linear'))
  G.cbar = DraggableColorbar.DraggableColorbar(G.cbar,drawing)
  G.cbar.connect()

  ################
  # IMAGE GET INTENSITY  in G.toolbarframe 
  if "LabelL" in vars(G) : # DESTROY otherwsie get it twice after open 
    G.LabelL.destroy()
    G.LabelZ.destroy()
  G.LabelL = Label(G.toolbar,bg=G.bg[0])#,font=G.small_font)   #LabelL like Local Max
  G.LabelL.pack(side = RIGHT,expand=0)	   
  G.LabelZ = Label(G.toolbar,bg=G.bg[0])#,font=G.small_font)
  G.LabelZ.pack(side = RIGHT,expand=0)
  G.pos = G.fig.canvas.mpl_connect('motion_notify_event',GetIntensity)

  
  if W.verbose > 3 : print "I am still ok 3.5" 
  ######################
  ##  DRAW FIG AND COLOR BAR 
  ######################
  #G.cbar.draw_all()
  G.fig.canvas.draw()

  #####################
  ###  SOME  CLICKS #
  #####################
  Pick.RefreshPick("") # assuming that the default PIck is setted yet 

  if W.verbose > 3 : print "I am still ok4 " 
  return 


def Scale(dic={},load=0): # Change contrast and color , load if it is loaded with InitImage
  """ remember that we need to update G.scael_dic in case we opne a new image, but this is not really true  """
  if W.verbose >2 : print "Scale called ", dic 
  if dic.has_key("tutorial"):
          if G.tutorial:
               if dic.has_key("cmap"): 
                       text="A menu button will be displayed and in this, there is waht is called some radio buttons, which permits to select a color for the image. And there is at the bottom a button for plotting the contours of objects. You have for colors from bright to faint:\n\n"
                       text+="->jet: red,yellow,green,blue\n"  
                       text+="->Black&White: White,Black\n"
                       text+="->spectral:red,yellow,green,blue, purple\n"    
                       text+="->RdYlBu: blue, white, red\n"  
                       text+="->BuPu: purple, white\n"  
                       text+="->Contour: This will display the 3 and 5 sigma contours of the objects on the image. To delete the contours that may crowd your image, just click again on contour.\n"     
                       TutorialReturn({"title":"Image Color",
                       "text":text,
                       })
               elif dic.has_key("fct"): 
                 text="A menu button with some radio button is displayed. Chose the function that will transforme the image according to a function. This function is apllied to the images values rescaled from 0 to 1 and then the image is mutliplied again fit the true min and max cut made.\n\n"
		 text+="Programmers, This function is trabsforming G.current_image when the true image is stocked under W.Im0 \nIf you want to add some function look at the InitGuy.py module, a function with some (2,3,4) thresholds (=steps) could be usefull to get stars of (2,3,4) differents color, nothing more, one color for each intensity range. This can be done with if also. "
                 TutorialReturn({"title":"Rescale Image Function",
                 "text":text,
                 })
               elif dic.has_key("scale_cut_type"):
                 text="A menu button with some radio button is displayed. You need to chose the cut for scaling the displaued color of the image (ie: the values of the minimum and maximum color). Youhave different way of cutting :\n\n"
		 text+="-> None, will take the true max and min values of th image to set the displayed color range. Usefull for saturated objects.\n" 
		 text+="-> Percentage, set the max (min) color as the maximum (minimum) value of the central percent% values. For example, 95% reject the 2.5% higher values and then take the maximum of the kept values.\n"
		 text+="-> RMS, will take make a -1,5 sigma for min and max\n"
		 text+="-> Manual, The power is in your hand, a new frame is displayed, enter the min and max value. When satified, please close the frame.\n"
		 text+="\n\nProgrammers, a cut setted with the histogram can be nice but not so usefull."
                 TutorialReturn({"title":"Cut Image Scale",
                 "text":text,
                 })
               return    
          else : return # including no tutorial  

  #print "----> Scale dic : ", dic 
     #######
     ##  INIT  WITH CURRENT IMAGE parameters. 
  #try : 
  if not load  : 
    G.scale_dic[0]["cmap"] = G.cbar.mappable.get_cmap().name # Image color 
    G.scale_dic[0]["min_cut"] = G.cbar.cbar.norm.vmin # Image color 
    G.scale_dic[0]["max_cut"] = G.cbar.cbar.norm.vmax # Image color 
  #except : print "cannot see image color and min max cut " 

  if W.verbose >2 : print " MG.scale ,Scale_dic ",G.scale_dic[0]
  G.scale_dic[0].update(dic) # UPDATE DIC 

  ###########
  ### CUT 
  if dic.has_key("scale_cut_type") :
    if dic["scale_cut_type"]=="None" : 
      #IG.ManualCut()
      G.scale_dic[0]["min_cut"] = W.Im0.min()
      G.scale_dic[0]["max_cut"] = W.Im0.max()
    else : 
      import Scale # otherwise get in conflict with Tkinter  
      tmp = Scale.MinMaxCut(W.Im0,dic=G.scale_dic[0] )     
      G.scale_dic[0]["min_cut"] = tmp["min_cut"]
      G.scale_dic[0]["max_cut"] = tmp["max_cut"]
    if W.verbose >2 : "I called Scale cut " 
  #import Scale 
  #G.scale_dic[0].update( Scale.MinMaxCut(W.Im0,dic=G.scale_dic[0]) )    #bite , should be in th eif  
  #else :  # if this is not a cut issue, renovate G.scale_dic 
  #  G.scale_dic[0]["min_cut"] =  
  #  G.scale_dic[0]["max_cut"] = 

  ######
  #" CONTOUR AND UPDATE    G.scale_dic[0] if not contour !! otherwise the value 
  


  ######
  # SCALE FCT 
  if not G.scale_dic[0].has_key("stretch"):  # in case 
    G.scale_dic[0]["stretch"]="linear"

    

  ###########
  # CONTOURS 
  if(dic.has_key("contour")):
    if G.scale_dic[0]["contour"] : 
         if not G.scale_dic[0].has_key("median"):
           import Stat
	   tmp = Stat.Stat(G.current_image,dic={"get":["mean","rms"]} ) 
         mean, rms = tmp["mean"], tmp["rms"]
         c0,c1,c2,c3,c4,c5 = mean, mean+rms, mean+2*rms, mean+3*rms,mean+4*rms, mean +5*rms 
         G.contour =G.ax1.contour(G.current_image,(c3,c5),
                      origin='lower',colors="k",
                      linewidths=3)
                      #extent=(-3,3,-2,2))
         if W.verbose > 0 : print "---> Contour of 3 and 5 sigma, clik again on contour to delete its."

 
    else : #include no contour  delete the contours
        if not load : 
          for coll in G.contour.collections:
            G.ax1.collections.remove(coll)
        
    G.scale_dic[0]["contour"] = not G.scale_dic[0]["contour"]
  ###############
  #  RELOAD THE IMAGE 
  if not load : 
    Draw() 

 ##########
 # RELOAD PlotStar
    try : PlotStar2()
    except : pass #in case you didn't pick the star yet
  return


def Draw(min=None,max=None,cmap=None,norm=False,cbar=True):
    if min != None : 
       G.scale_dic[0]["min_cut"] = min   
       G.scale_dic[0]["max_cut"] = max 
    if cmap != None : G.scale_dic[0]["cmap"] = cmap 

    cmap = G.scale_dic[0]["cmap"]
    min , max = G.scale_dic[0]["min_cut"] ,   G.scale_dic[0]["max_cut"]

    mynorm = NormalizeMy.MyNormalize(vmin=min  ,vmax=max,stretch=G.scale_dic[0]["stretch"], vmid = min -5)
    G.cbar.mappable.set_cmap(cmap)
    G.cbar.cbar.set_cmap(cmap=cmap)
    G.cbar.cbar.set_norm(mynorm)
    G.cbar.mappable.set_norm(mynorm)

    G.cbar.cbar.patch.figure.canvas.draw()
    G.fig.canvas.draw()  
    
    try :  # if no fig result, and if not work nevermind  
      for i in (G.figresult_mappable1, G.figresult_mappable2) : 
        i.set_norm(mynorm)   
        i.set_cmap(cmap) 
      G.figresult.canvas.draw() 
    except : 
      if W.verbose >2 : print "MyGui, Draw cannot draw in figresult" 
    #except : pass 


def PD(dic): # print dictionary for RunCommand  
  for k in dic.keys() : 
    print '%.20s    %.20s' %  (k,dic[k])
       
def RectanglePhot(): #used  for RunCommand 
  if W.verbose > 3 : print 'Rectangle Phot :'
  RefreshPickColor()
  G.rect_phot_bool =1
  r=matplotlib.widgets.RectangleSelector(
      G.ax1,ManualRectangle, drawtype='box',
      rectprops = dict(facecolor='pink', edgecolor = 'black', alpha=0.5, fill=True))
  G.rect_phot_bool= 0
  return

#def PrintCorrelation():

#def Stat(grid):
#  return  

def FigurePlotOld(x,y,dic={}):        
  """ x and y can be simple list 
  or also its can be list of list for a multiple axes
  dic : title:"string", logx:bol, logy:bol, xlabel:"" , ylabel:"" 
  """ 
  #from matplotlib import pyplot as plt 
  if W.verbose >3 : print "MG.FigurePlotCalled" 
  from matplotlib import pyplot as plt  # necessary if we are in a sub process 
  default_dic = {"warning":0,"title":"no-title"}
  default_dic.update(dic) ; dic = default_dic 

  def SubPlot(x,y) : 
    nx,ny=7, 5 
    if dic.has_key("logx") : ax.set_xscale("log")
    if dic.has_key("logy") : ax.set_yscale("log")
    if dic.has_key("xlabel") : ax.set_xlabel(dic["xlabel"])
    if dic.has_key("ylabel") : ax.set_ylabel(dic["ylabel"])

    ax.plot(x,y)  

    ax2 = ax.twiny()
    ax2.set_xticks(np.arange(nx))
    xlist= np.linspace(0,x[-1]*W.head.pixel_scale,nx)
    xlist = [int(1000*u) for u in xlist ]
    ax2.set_xticklabels(xlist,rotation=45)
    #bite this is ugly 
    ax2.set_xlabel(u"Distance [mas]")

    ax3 = ax.twinx()
    ax3.set_yticks(np.arange(ny))
    ylist = np.linspace(0,y[0],ny)
    ylist = [int(u) for u in ylist ]
    ax3.set_yticklabels(ylist)
    ax3.set_ylabel(u"number count per pixel")
    ############
    # TWIN axes 


  #MyProcess() : 
  if W.verbose >3 : print "___________________________________________\n",threading.currentThread().getName(), "Starting------------------\n"

  global ax 
  G.contrast_fig.clf() 
  #tfig.canvas.set_window_title(dic["title"])

  if not ( type(x[0]) is list ): # otherwise multiple axes  
    if W.verbose > 3 : print "MG.FigurePlot, we make a single plot" 
    ax = G.contrast_fig.add_subplot(111) 
    #from mpl_toolkits.axes_grid1 import host_subplot
    #ax = host_subplot(111) 
    SubPlot(x,y) 
    #if dic.has_key("title") : 
    #   plt.title(dic["title"])
    if not dic["warning"] : warnings.simplefilter("ignore") 
    if W.verbose >3 : print "I will show " 
    G.contrast_fig.canvas.draw() 
    if not dic["warning"] : warnings.simplefilter("default") 
    #tfig.show()      
  if W.verbose >3 : print "___________________________________________\n",threading.currentThread().getName(), "Exiting------------------\n" 

  #w = threading.Thread(name='figure_tread', target=MyProcess)
  #w.start() 
  return 

def FigurePlot(x,y,dic={}):        
  """ x and y can be simple list 
  or also its can be list of list for a multiple axes
  dic : title:"string", logx:bol, logy:bol, xlabel:"" , ylabel:"" 
  """ 
  #from matplotlib import pyplot as plt 
  if W.verbose >3 : print "MG.FigurePlotCalled" 
  from matplotlib import pyplot as plt  # necessary if we are in a sub process 
  default_dic = {"warning":0,"title":"no-title"}
  default_dic.update(dic) ; dic = default_dic 

  def SubPlot(x,y) : 
    nx,ny=7, 5 
    if dic.has_key("logx") : ax.set_xscale("log")
    if dic.has_key("logy") : ax.set_yscale("log")
    if dic.has_key("xlabel") : ax.set_xlabel(dic["xlabel"])
    if dic.has_key("ylabel") : ax.set_ylabel(dic["ylabel"])

    ax.plot(x,y)  

    ax2 = ax.twiny()
    ax2.set_xticks(np.arange(nx))
    xlist= np.linspace(0,x[-1]*W.head.pixel_scale,nx)
    xlist = [int(1000*u) for u in xlist ]
    ax2.set_xticklabels(xlist,rotation=45)
    #bite this is ugly 
    ax2.set_xlabel(u"Distance [mas]")

    ax3 = ax.twinx()
    ax3.set_yticks(np.arange(ny))
    ylist = np.linspace(0,y[0],ny)
    ylist = [int(u) for u in ylist ]
    ax3.set_yticklabels(ylist)
    ax3.set_ylabel(u"number count per pixel")
    ############
    # TWIN axes 


  #MyProcess() : 
  if W.verbose >3 : print "___________________________________________\n",threading.currentThread().getName(), "Starting------------------\n"

  global ax 
  G.contrast_fig.clf() 
  #tfig.canvas.set_window_title(dic["title"])

  if not ( type(x[0]) is list ): # otherwise multiple axes  
    if W.verbose > 3 : print "MG.FigurePlot, we make a single plot" 
    ax = G.contrast_fig.add_subplot(111) 
    #from mpl_toolkits.axes_grid1 import host_subplot
    #ax = host_subplot(111) 
    SubPlot(x,y) 
    #if dic.has_key("title") : 
    #   plt.title(dic["title"])
    if not dic["warning"] : warnings.simplefilter("ignore") 
    if W.verbose >3 : print "I will show " 
    G.contrast_fig.canvas.draw() 
    if not dic["warning"] : warnings.simplefilter("default") 
    #tfig.show()      
  if W.verbose >3 : print "___________________________________________\n",threading.currentThread().getName(), "Exiting------------------\n" 

  #w = threading.Thread(name='figure_tread', target=MyProcess)
  #w.start() 
  return 

def Remember():
  if W.verbose > 0 : print """ indentation of tutorial is 15

        """ 
    # for CBAR 
    #G.cbar.mappable.set_norm( G.cbar.cbar.norm  ) 
     #G.cbar.set_norm(NormalizeMy.MyNormalize(vmin=image.min(),vmax=image.max(),stretch='linear')) 
    #G.cbar.cbar.set_clim()
    #G.cbar.cbar.draw_all() # this is in the draggable colorbar yet 
    #G.cbar.cbar.norm.vmax=G.scale_dic[0]["max_cut"]





#  func="W.psf_fit= IF.SeeingFit(W.Im0,W.star_center,(%f,%f,%f,%f),W.fit_type,dictionary={'NoiseType':W.noise_type,'PhotType':W.phot_type,'FitType':W.fit_type}) " % (rx1,rx2,ry1,ry2) 
#  default="print 'TIME OUT, the fit was too long, I had to stop it'"
#  timeout_duration=20 # seconde 
#  anyway="import WorkVariables as W; import GuyVariables as G ; import ImageFunction as IF"
#
#  import RunCmd
##  RunCmd.RunPythonCmd(func,  timeout_duration, default=default,anyway=anyway)  # default is exec if time out. anyway is exec anyway! 

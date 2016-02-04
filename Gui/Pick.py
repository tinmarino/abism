import matplotlib 
import numpy as np # for a readind lst like an array 

import MyGui as MG 
import EventArtist  # draw an ellipse 
import AnswerReturn as AR 

import Strehl


import GuyVariables as G
import WorkVariables as W


def RefreshPick(label): # This is the only callled routine 
  if label != "" : G.connect_menu["text"] = u'\u25be ' +   label # remove the little arrow 
   
  """in function of the name of G.connect_var, we call the good one. Disconnect old pick event and connect the new one """
  lst = np.array ([
   ["PickOne","one","PickOne"]  , ["PickMany","many","PickMany"] ,
    ["Binary Fit", "binary","Binary" ] ,  ["Profile", "profile","Profile"  ]  ,
    ["Stat","stat","StatPick"], 
    ["Ellipse", "ellipse" ,"PickEllipse" ]  , ["No Pick", "nopick", "NoPick"]  ,  
    ]) # Label@Menu , W.pick_type, fct to call 
  try : W.pick_type_old = W.pick_type 
  except : pass 
  index =  list(lst[:,0]).index(G.connect_menu["text"][2:])   # or G.connect_var.get() 
  W.pick_type = lst[index,1]



   # THE dicconnect  
  if "pick_type_old" in vars(W) : 
     if type(W.pick_type_old)  is list : # for pick many  
        index_old = list(lst[:,1]).index(W.pick_type_old[0])   # or G.connect_var.get() 
     else : 
        index_old = list(lst[:,1]).index(W.pick_type_old)   # or G.connect_var.get() 
     globals()[lst[index_old,2]](disconnect=True) # This staff with disconnect is to avoid twice a call, in case pick_old = pick  it is not necessary but more pretty  
   
   # THE CALLL 
  globals()[lst[index,2]]() 
  try : 
     if W.verbose > 3 : print "Refresh called |tipe : ",  lst[index,2], "|old : ", W.pick_type_old  
  except : pass 
  


def NoPick(disconnect=False) : # to check if all pick types are disconnect 
  return 


def PickEllipse(disconnect=False): 
      # DISCONNECT 
      if disconnect and  ( "pick_type_old" in vars(W) ) and (W.pick_type_old == "ellipse") :
        try : 
	  G.ellipse.Disconnect() 
	  G.ellipse.RemoveArtist() 
	  del G.ellipse 
        except : pass
	return 
      # CONNECT 
      if W.pick_type == "ellipse" :
         G.ellipse = EventArtist.Event(G.fig,G.ax1,array=W.Im0)  
            
	
def Profile(disconnect=False):
      if G.tutorial:
               text="Draw a line on the image. Some basic statistics on the pixels cutted by your line will be displayed in the 'star frame'. And a Curve will be displayed on the 'fit frame'. A pixel is included if the distance of its center is 0.5 pixel away from the line. This is made to prevent to many pixels stacking at the same place of the line\n\n."
               text+="Programmers, an 'improvement' can be made including pixels more distant and making a mean of the stacked pixels for each position on the line." 
               MG.TutorialReturn({"title":"Linear Profile, cutted shape of a source",
               "text":text,
               })
               return     
      # DISCONNECT 
      if disconnect and   ( "pick_type_old" in vars(W) ) and (W.pick_type_old == "profile") :
	try : 
          G.my_profile.Disconnect()
	except : 
	  if W.verbose > 3 : print "Pick.Profile , cannot disconnect profile " 
	try : 
	  G.my_profile.RemoveArtist() 
	  #del G.my_profile # maybe not 
        except : 
	  if W.verbose > 3 : print "Pick.Profile , cannot remove artist profile " 
	return 
	#if W.pick_type == "profile" : return # in order not to cal twice at the begining 
      # CONNECT 
      if W.pick_type == "profile" :
        G.my_profile =  EventArtist.Profile(G.fig,G.ax1) 




def PickOne(disconnect=False):
      if G.tutorial:
               text="This button should be green and the zoom button of th eimage toolbar  unpressed. If it is pressed, clik again on it. You then hav eto draw a rectangle aroung the star to mesure the strehl ratio around this star. A first fit will be computed in the rectangle you 've just drawn. Then the photometry of the star will be computed according to the photometry and background measurement type you chose in 'MoreOption' in the file menu. By default, the photometry is processed in a 99% flux rectangle. And the backgorund, in 8 littel rectangels around the star. \n\n"
               text+="The fit is necessary to get the maximum, the peak of the psf that will be compared to the diffraction pattern. You can set to assess the photometry of the object with the fit.\n\n"
               text+="A Moffat fit type is chosen by default. but you can change it with the button FitType. I recommend you to use a Gaussian for Strehl <5%, A Moffat for intermediate Strehl and a Bessel for strehl>60%.\n\n"
               TutorialReturn({"title":"Pick One Star",
               "text":text,
               })
               return    

      # DISCONNECT 
      if  disconnect and  ( "pick_type_old" in vars(W) ) and (W.pick_type_old == "one") :
        try : G.rs_one.set_active(False)
        except : pass
	return 

      # CONNECT 
      if W.pick_type == "one" :
        print "\n\n\n________________________________\n|Pick One| : draw a rectangle around your star-------------------"
        W.pick_type='one'
        G.rs_one=matplotlib.widgets.RectangleSelector(
           G.ax1, RectangleClick, drawtype='box',
           rectprops = dict(facecolor='green', edgecolor = 'black', alpha=0.5, fill=True))


         

def Binary(disconnect=False):
  if G.tutorial:
               text="If Binary button is green, make two click on a binary system : one on each star. A Binary fit will be processed. This is still in implementation."
               TutorialReturn({"title":"Binary System",
               "text":text,
               })
               return     
  # DISCONNECT 
  if   disconnect and  ( "pick_type_old" in vars(W) ) and (W.pick_type_old == "binary") :
    try :  G.fig.canvas.mpl_disconnect(G.pt1)
    except : pass
    try :G.fig.canvas.mpl_disconnect(G.pt2)
    except : pass 
    return 

  # CONNECT 
  if W.pick_type == "binary" :
    print "\n\n\n______________________________________\n|Binary| : Make 2 clicks, one per star-------------------"
    G.pt1 = G.fig.canvas.mpl_connect('button_press_event', Binary2)
    W.pick_type="binary"                  # for PlotAnswer()
    return
  return       

def Binary2(event):
  print "1st point : ", event.xdata, event.ydata 
  G.star1=[event.ydata,event.xdata]
    # we need to inverse, always the same issue ..
  G.fig.canvas.mpl_disconnect(G.pt1)
  G.pt2 = G.fig.canvas.mpl_connect('button_press_event', Binary3) 
  return

def Binary3(event):  # Here we call the math  
  print "2nd point : ",event.xdata, event.ydata
  G.star2=[event.ydata,event.xdata]

  MultiprocessCaller()
  Binary() 


      
def PickMany(disconnect=False):
  if G.tutorial:
               text="As for PickOne, you have to draw a rectangle around a star. But this time the output is shorten. After the Strehl measurment of the star you picked, you can pick an other star."
               TutorialReturn({"title":"Pick Many Stars",
               "text":text,
               })
               return     
  # DISCONNECT 
  if disconnect and  ( "pick_type_old" in vars(W) ) and (W.pick_type_old[0] == "many") :
     try : G.rs_many.set_active(False) 
     except : pass #in case rs_many is not called yet
     return 

  # CONNECT 
  if W.pick_type == "many" :
     G.arrows, G.answer_saved=[],{}
     print '\n\n\n______________________________\n|Pick Many| : draw rectangles around your stars-----------------------'	
     W.pick_type=['many',1]     #G.pick count the index of the picked star
     if W.verbose>9 : print 'pick,G.pick',W.pick_type
     G.rs_many=matplotlib.widgets.RectangleSelector(
        G.ax1, RectangleClick, drawtype='box',
        rectprops = dict(facecolor='blue', edgecolor = 'black', alpha=0.5, fill=True))
     return

def StatPick(disconnect=False) :
      if G.tutorial:
	       text="The Stats are defined in Arrayfunction/Stat.py"
               TutorialReturn({"title":"Draw a rectangle",
               "text":text,
               })
               return    

      # DISCONNECT 
      if  disconnect and  ( "pick_type_old" in vars(W) ) and (W.pick_type_old == "stat") :
        try : G.rs_stat.set_active(False) # rs rectangle selector
        except : pass
	return 

      # CONNECT 
      if W.pick_type == "stat" :
        print "\n\n\n________________________________\n|Pick Stat| : draw a rectangle around a region and ABISM will give you some statistical informationcomputed in the region-------------------"
        W.pick_type='stat'
        G.rs_stat=matplotlib.widgets.RectangleSelector(
           G.ax1, RectangleClick, drawtype='box',
           rectprops = dict(facecolor='red', edgecolor = 'black', alpha=0.5, fill=True))
      

def RectangleClick(eclick,erelease):    
  """return the extreme coord of the human drawn rectangle  And call StrehlMeter"""
  if W.verbose>3 :print 'rectangle click_________________'
  G.image_click =eclick.xdata, eclick.ydata
  G.image_release =erelease.xdata,erelease.ydata
  if W.verbose>3 :print G.image_click,G.image_release
  center_click=(G.image_click[1]+G.image_release[1])/2,(G.image_click[0]+G.image_release[0])/2  #center  Of the Event 
  W.r=(G.image_click[1],G.image_release[1],G.image_click[0],G.image_release[0])  # we inverse to get x,y like row,column 

  MultiprocessCaller() 
  return


###USELESS 
def ManualNoiseRectangle():
  if G.tutorial:
               text="You need to read the terminal. You will be asked to make some rectangles in the sky, to get an average of the sky. Note the the sky estimated by this algorith is only a scalar variable (stocked in W.strehl['background']). "
               TutorialReturn({"title":"Manual Background estimation",
               "text":text,
               })
               return    
  if G.bu_noise_manual["background"]=='green':
     G.bu_noise_manual['background']="blue"
     G.rs_star.set_active(False)              
     G.remember_r=[]
     print 'Do rectangles in the background and click on manual' 

     G.rs_noise=matplotlib.widgets.RectangleSelector(
         G.ax1,ManualRectangle, drawtype='box',
         rectprops = dict(facecolor='pink', edgecolor = 'black', alpha=0.5, fill=True)) 
  elif G.bu_noise_manual['background']=='grey':
     RefreshPickColor()	
     G.bu_noise_manual['background']='green'
     print 'Select your star without background and click on Manual button'
     G.rs_star=matplotlib.widgets.RectangleSelector(
         G.ax1,ManualRectangle, drawtype='box',
         rectprops = dict(facecolor='pink', edgecolor = 'black', alpha=0.5, fill=True)) 
  elif G.bu_noise_manual['background']=='blue':
     G.bu_noise_manual['background']='grey'
     for r in G.remember_r :
        if W.verbose>9  : print '----->MyGui.py,ManualNoiseRectangle,surface : rx1,rx2,ry1,ry2 =',r
     W.noise_type = ('Manual',G.remember_r) 
     StrehlMeter(G.r)
     G.rs_noise.set_active(False)
     PickOne()
     G.bu_noise_8_rects['background']='green'
     W.noise_type='8Rects'
  return 
def ManualRectangle(eclick,erelease) :
           image_click =eclick.xdata, eclick.ydata
           image_release =erelease.xdata,erelease.ydata
           r=image_click[1],image_release[1],image_click[0],image_release[0]    # we inverse to get x,y like row,column
           r = IF.Order4(r)
           if G.rect_phot_bool :
               print  IF.RectanglePhot(W.Im0,r)  # when you want a phot from command
     
           if W.verbose>9 : print '----> MyGui.py, ManualRectangle',r
           if G.bu_noise_manual['background'] =='green':G.r = r
           elif G.bu_noise_manual['background'] =='blue':G.remember_r.append(r) 
           G.rect_phot_bool =0
           return


       #############################
       ## MULTIPROCESSING TOOLS    #
       #############################


def MultiprocessCaller() : 
    """ This is made in order to call and stop it if we spend to much time 
    now I putted 10 sec but a G.time_spent should be implemented. todo"""
    PickWorker() 



#from timeout import timeout 
#@timeout(1) 
def PickWorker() : 
  def NBinary(): 
    dictionary={'star1':G.star1,'star2':G.star2,"fit_type":W.fit_type}
    if W.same_psf: dictionary["same_psf"]=1
    else :dictionary["same_psf"]=0

    import ImageFunction as IF # bite  
    W.psf_fit = IF.BinaryPSF2(W.Im0,dictionary)
    W.strehl = W.psf_fit[0]
    G.fig.canvas.mpl_disconnect(G.pt2) 
    if W.verbose>3 : print "Binary res :" ,W.psf_fit

    AR.PlotAnswer()
    AR.PlotStar2()
    AR.PlotStar("bidon")

  if W.pick_type == "binary" : NBinary()  
  if W.pick_type == "stat" : AR.PlotStat()  
  else : Strehl.StrehlMeter()  
  return





def MultiprocessCallerOLD() :  # not working because of ...
  """xcb] Unknown sequence number while processing queue
  [xcb] Most likely this is a multi-threaded client and XInitThreads has not been called
  [xcb] Aborting, sorry about that."""
  from multiprocessing import Process
  # WORKER 
  W.w=Process(name='pick_worker', target=PickWorker)
  W.w.daemon = True
  W.w.start()
  # TIMER  
  W.t=Process(name='pick_worker', target=PickTimer)
  W.t.daemon = True
  W.t.start()
  return 
def PickTimer() : 
  from time import sleep 
  time_to_wait = 2
  sleep(time_to_wait) 
  if W.verbose >0 : print "I killed gratefully your process after "+ str(time_to_wait) + "seconds, its convergence was too slow : TRY AGAIN"
  W.w.terminate() 
  return 
def Comments() :
  ######
  ## TIME  limit 
  #import threading
  #class InterruptableThread(threading.Thread):
  #    def __init__(self):
  #        threading.Thread.__init__(self)
  #        self.result = "default"
  #    def run(self):
  #      try:
  #        StrehlMeter(W.r) 
  #      except Exception as e:
  #        print "Too long"
  #    def suicide(self):
  #      print "\n\n"
  #      #raise SystemExit
  #      raise RuntimeError('Stop has been called, process too slow. ')

  #import time 
  #start_time = time.time()
  #it = InterruptableThread()
  #it.start()
  #it.join(timeout_duration)
  #if it.isAlive():
  #  print "aliva"
  #  it.suicide()
  #else:
  #  p    #import threading
    #class InterruptableThread(threading.Thread):
    #    def __init__(self):
    #        threading.Thread.__init__(self)
    #        self.result="too slow"
    #    def run(self):
    #        self.result = PickWorker()
    #it = InterruptableThread()
    #it.start()
    #it.join(timeout_duration)


    #if it.isAlive():
    #    return it.result
    #else:
    #    if W.verbose >0 : print "I killed gratefully your process after "+ str(timeout_duration) + "seconds, its convergence was too slow : TRY AGAIN"
    #    return rint "dead"
  return 

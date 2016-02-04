from Tkinter import *
import numpy as np  
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas

import ImageFunction as IF 

import BasicFunction as BF
import Stat

import GuyVariables as G
import WorkVariables as W

from threading import Thread
from matplotlib import pyplot as plt 

def MyFormat(value,number,letter): 
   """ This is just to put a "," between the 1,000 for more readability"""
   stg= "{:,"
   stg+= "." + str(number) + letter + "}" 
   if W.verbose > 8 : print stg 
   return stg.format(value).replace(","," ") 


       ##################
       #  LABELS  LABELS 
       ##################

def PlotAnswer(unit=None):  
  if unit != None : 
    G.scale_dic[0]["answer"]=unit  

  ##################
  # Destroy  answer frame, remove arrows 
  if (not  type(W.pick_type) is list) or  ( W.pick_type[0]=='many' and W.pick_type[1]==1 ) :
    if W.verbose > 3 : print "Idestroy AnswerFrame"
    if "AnswerFrame" in vars(G) : G.AnswerFrame.destroy()  
    if ( "arrows" in vars(G) ) : #and ( len(G.arrows) !=0)   : 
      #try :
        for i in range(len(G.arrows))  : 
	   G.arrows.pop().remove()   # remove from G.arrows and from ax1.texts
        G.fig.canvas.draw() 
      #except : pass 
  #elif ( W.pick_type[0]=='many' and W.pick_type[1]==0 ) :
  #  if "AnswerFrame" in vars(G) : G.AnswerFrame.destroy()  
  #  if arrows in vars(G) : 
  #    for i in G.arrows : i.remove() 
  #    G.fig.canvas.draw() 
  ##################
  # and  construct it 
    G.AnswerFrame = Frame(G.LeftBottomFrame,bg=G.bg[0] ) # in G.all_frame yet 
    G.AnswerFrame.pack(expand=0 ) 


  ##"
  # CALL the corresponding PLot
  if W.pick_type=='one': PlotPickOne() 
  elif W.pick_type=='binary': PlotBinary() 
  elif W.pick_type[0]=="many": PlotPickMany()
  elif W.pick_type[0]=="stat": PlotStat()


def PlotPickOne():
  rms =  W.head.wavelength /2/np.pi * np.sqrt(-np.log(W.strehl["strehl"]/100)) 
  W.strehl["strehl2_2"] = 100 *np.exp(-(rms*2*np.pi/2.17)**2) 
  ###### <- CAlculate Equivalent strehl2.2


  G.AnswerFrame.columnconfigure(0,weight=1)  # to fill th ecolumn on th epossible space  
  G.bu_answer_type=Button(G.AnswerFrame,text='useless',background='Khaki' ,borderwidth=1) 
  G.lb_answer_type=Label(G.AnswerFrame,text="useless",justify=LEFT,anchor="nw",bg=G.bg[0])
  
  
  
  ############
  ## IMAGE COORD
  if G.scale_dic[0]["answer"]=="detector":
      G.bu_answer_type["text"]=u"\u21aa"+'To sky     '
      G.bu_answer_type["command"]=lambda: PlotAnswer(unit="sky") 
      G.lb_answer_type["text"]= "In detector units"
      G.bu_answer_type["width"]=9

      lst=[  ["Intensity: "            , W.strehl["intensity"]     ,MyFormat(W.strehl["intensity"],1,"f") +" [adu]"],
         ["Background: "           , W.strehl["my_background"]    ,MyFormat(W.strehl["background"],1,"f") +'| rms: ' + MyFormat(W.strehl['rms'],1,"f") + " [adu]"], 
         ["Photometry: "           , W.strehl["my_photometry"]    ,MyFormat(W.strehl["my_photometry"],1,"f")  + " [adu]"],
         ["Strehl: "               , W.strehl["strehl"]        ,MyFormat(W.strehl["strehl"],1,"f") +  " +/- "+   MyFormat(W.strehl["err_strehl"],1,"f")    +" %" ],
         ["Equivalent Strehl 2.17: ", W.strehl["strehl2_2"]     ,MyFormat(W.strehl["strehl2_2"],1,"f") +  " %"],
         ["Center x,y: "               , (W.strehl["fit_dic"]["center_y"],W.strehl["fit_dic"]["center_x"]) , MyFormat(W.strehl["fit_dic"]["center_y"],3,"f")    +" , "+   MyFormat(W.strehl["fit_dic"]['center_x'],3,"f")      ],  # need to inverse
         ["FWHM a,b,e: "           , (W.strehl["fwhm_x"],W.strehl["fwhm_y"]) , MyFormat(W.strehl["fwhm_a"],1,"f")   +"," +  MyFormat(W.strehl["fwhm_b"],1,"f") +","+  MyFormat(W.strehl["eccentricity"],2,"f")  ], 
         ["Fit Type: "   , W.fit_type  , str(W.fit_type) ],   
         ]

  ##################
  ## SKY COORD 
  else : # including unit = sky :    not =  detector  G.scale_dic[0]["answer"]=="sky":
      G.bu_answer_type["text"]=u"\u21aa"+'To detector'
      G.bu_answer_type["command"]=lambda: PlotAnswer(unit="detector") 
      G.lb_answer_type["text"]= "In sky units"
      G.bu_answer_type["width"]=9

      ###
      # WCS 
      try : 
        if len( W.hdulist[0].data.shape ) == 3: # if cube,  just cut the WCS object, see antoine
           my_wcs = ProjectWcs(W.head.pywcs).wcs_pix2sky( np.array([[ W.strehl["center_y"],W.strehl["center_x"] ]]), 0 )
        else : # not cube
           my_wcs = W.head.pywcs.wcs_pix2sky( np.array([[ W.strehl["center_y"],W.strehl["center_x"] ]]), 0 )
        if W.verbose >3: print "----> PicKOnePlot WCS:" ,my_wcs
      except : 
        import traceback 
	traceback.print_exc() 
        print "WARNING I did not manage to get WCS"
	my_wcs= np.array( [ [99,99],[99,99] ]) 
      W.strehl["center_ra"],W.strehl["center_dec"] = my_wcs[0,0],my_wcs[0,1]     

      lst=[  ["Intensity: "            , W.strehl["intensity"],  "%.1f"% (W.zpt-2.5*np.log10(W.strehl["intensity"]))  +" [mag]"],
             ["Background: "           , W.strehl["my_background"]    , "%.2f"% (W.zpt-2.5*np.log10(W.strehl["my_background"]))  + '| rms: ' + "%.2f" % (W.zpt-2.5*np.log10(W.strehl['rms']) )  + " [mag]"],
             ["Photometry: "           , W.strehl["my_photometry"]    , "%.2f"% (W.zpt-2.5*np.log10(W.strehl["my_photometry"]))  + " [mag]"],
             ["Strehl: "               , W.strehl["strehl"]        , "%.1f"% (W.strehl["strehl"])+  " +/- "+"%.1f"% W.strehl["err_strehl"]+" %" ],
             ["Equivalent Strehl 2.17: ", W.strehl["strehl2_2"]     , "%.1f"% W.strehl["strehl2_2"]+  "%"],
            ["Center RA,Dec: "               , (W.strehl["center_ra"],W.strehl["center_dec"]) ,  "%.8f"%W.strehl["center_ra"]+","+"%.8f"% W.strehl['center_dec']  ], 
             ["FWHM a,b,e [mas]: "   , (W.strehl["fwhm_x"],W.strehl["fwhm_y"]) ,  "%.1f" % (W.strehl["fwhm_a"]*W.head.pixel_scale*1000)   +"," +  "%.1f" % (W.strehl["fwhm_b"]*W.pixel_scale*1000)   +","+  "%.2f" % W.strehl["eccentricity"]  ], 
             ["Fit Type: "   , W.fit_type  , str(W.fit_type) ],   
	     ] # label , variable, value as string 




  ########
  # DISPLAY 
  G.bu_answer_type.grid(row=0,column=1,sticky="w")
  G.lb_answer_type.grid(row=0,column=0,sticky="w")  
  row=1
  for i in lst:
    myargs = {"font":G.answer_font,"justify":LEFT,"anchor":"nw", "bg":G.bg[0] }
    if i[0]=="Strehl: ": myargs["fg"] = "purple"
    l1 = Label(G.AnswerFrame,text=i[0],**myargs) 
    l2 = Label(G.AnswerFrame,text=i[2],**myargs)
    l1.grid(row=row,column=0,sticky="nsew") 
    l2.grid(row=row,column =1,sticky="nsew")  
    row+=1
  max_size1, max_size2 = 200, 200
  #G.AnswerFrame.grid_columnconfigure(0,minsize=max_size1,weight=1)  
  G.AnswerFrame.grid_columnconfigure(1,minsize=150,weight=1)  
                 

def PlotBinary():
      x0,x1,y0,y1=W.strehl["x0"],W.strehl["x1"],W.strehl["y0"],W.strehl["y1"] 
      ##########
      # SEPARATION DISTANCE
      separation=np.sqrt( (y1-y0)**2 + (x1-x0)**2 ) 
      sep_err = W.psf_fit[1]["x0"]**2+W.psf_fit[1]["y0"]**2
      sep_err+= W.psf_fit[1]["x1"]**2+W.psf_fit[1]["x1"]**2
      sep_err = np.sqrt(sep_err)

      #############
      # SEPARATION ANGLE 
      W.angle = (W.strehl["y1"]-W.strehl["y0"],W.strehl["x1"]-W.strehl["x0"])
      #W.angle = (W.strehl["x0"]-W.strehl["x1"],W.strehl["y0"]-W.strehl["y1"])
      W.angle/= np.sqrt(  (W.strehl["y0"]-W.strehl["y1"])**2 +(W.strehl["x0"]-W.strehl["x1"])**2  )
      im_angle = np.arccos( W.angle[1] ) * 57.295779 # 360/2pi
      sign = np.sign( W.angle[0] )
      W.im_angle  = im_angle + (sign-1)*(-90) 

      sky_angle = np.arccos( W.angle[1]*W.north_direction[1] + W.angle[0]*W.north_direction[0])* 57.295779 # inverted angle and not north 
      sign  = np.sign(W.angle[0]*W.east_direction[0] + W.angle[1]*W.east_direction[1])
      W.sky_angle  = sky_angle + (sign-1)*(-90) 
      
      ##############"
      # STREHL 
      W.phot0,W.phot1 = W.strehl["fit_dic"]["my_photometry0"],W.strehl["fit_dic"]["my_photometry1"]
      bessel_integer = W.head.wavelength *10**(-6.) / np.pi /(W.head.pixel_scale/206265)/ W.head.diameter
      bessel_integer = bessel_integer**2 *4*np.pi / (1-(W.head.obstruction/100)**2) 
      Ith0,Ith1 = W.phot0/bessel_integer, W.phot1/bessel_integer
      W.strehl0 = W.strehl["fit_dic"]["intensity0"] / Ith0 *100 
      W.strehl1 = W.strehl["fit_dic"]["intensity1"] / Ith1 *100



      ##############
      ## IMAGE COORD 
      if G.scale_dic[0]["answer"]=="image":
          G.bu_answer_type=Button(G.AnswerFrame,text='In sky units',background='Khaki',
                         command=lambda: PlotAnswer(unit="sky")  ,borderwidth=1) 
          G.bu_answer_type.pack(side=TOP,fill=X,expand=0)

          lst=[["Binary: ", W.fit_type,W.fit_type ], 
	       ["1 Star: ",(y0,x0), " ("+ "%.1f"%y0+ "|" + "%.1f"%x0 + ")"],
	       ["2 Star: ",(y1,x1), " ("+ "%.1f"%y1+ "|" + "%.1f"%x1 + ")"],
               ["Separation: ", separation, "%.2f"%separation +"+/-"+ "%.2f"%sep_err +" [pxl]" ],
	       ["Phot1: ",W.phot0,"%.1f"%W.phot0 + " [adu]"],
	       ["Phot2: ",W.phot1,"%.1f"%W.phot1 + " [adu]"],
	       ["Flux ratio: ",(W.phot0/W.phot1),"%.1f"%(W.phot0/W.phot1) ],
	       ["Orientation: ",im_angle,"%.2f"%im_angle + u'\xb0'], 
	       ["Strehl1: ",W.strehl0,"%.1f"%W.strehl0+" %"   ],
	       ["Strehl2: ",W.strehl1,"%.1f"%W.strehl1+" %"   ],
	       ]
        
          for i in lst : 
            Label(G.AnswerFrame,text=i[0]+i[2],font=G.answer_font,bg=G.bg[0]).pack(side=TOP,padx=3,pady=3) 
      
      ##############
      ## SKY COORD 
      if G.scale_dic[0]["answer"]=="sky":
          G.bu_answer_type=Button(G.AnswerFrame,text='In image units',background='Khaki',
                         command=lambda: PlotAnswer(unit="image")  ,borderwidth=1) 
          G.bu_answer_type.pack(side=TOP,fill=X,expand=0)
      
          #############"
          # WCS
          if len( W.hdulist[0].data.shape ) == 3: # if cube,  just cut the WCS object, see antoine
               try : my_wcs = ProjectWcs(W.head.pywcs).wcs_pix2sky( np.array([   [ W.strehl["y0"],W.strehl["x0"]  ] ,  [W.strehl["y1"],W.strehl["x1"] ]     ]), 0 )
	       except : 
	         if W.verbose >0 : print "Answerreturn.py/PlotBinary cannot set the wcs projection of a cube" 
                 my_wcs = np.array([   [ W.strehl["y0"],W.strehl["x0"]  ] ,  [W.strehl["y1"],W.strehl["x1"] ]     ])
          else : # not cube
               try : my_wcs = W.head.pywcs.wcs_pix2sky( np.array([   [ W.strehl["y0"],W.strehl["x0"]  ] ,  [W.strehl["y1"],W.strehl["x1"] ]     ]), 0 )
	       except : 
	         if W.verbose >0 : print "Answerreturn.py/PlotBinary cannot set the wcs projection of a cube" 
          if W.verbose >3 : print "----> BinaryPlot@AnswerReturn.py WCS:" ,my_wcs 
	  ra,dec= my_wcs[:,0], my_wcs[:,1] 



          ##########
          lst=[["Binary: ", W.fit_type,W.fit_type ], 
	       ["1 Star: ",(ra[0],dec[0]), " ("+ "%.6f"%ra[0]+ "|" + "%.6f"%dec[0] + ")"],
	       ["2 Star: ",(ra[1],dec[1]), " ("+ "%.6f"%ra[1]+ "|" + "%.6f"%dec[1] + ")"],
               ["Separation: ", separation, "%.1f"%(separation*W.head.pixel_scale*1000) +"+/-"+ "%.1f"%(sep_err*W.pixel_scale*1000) + " [mas]" ],
	       ["Phot1: ",W.phot0,"%.1f"%( W.zpt -2.5 * np.log10(W.phot0) )  + " [mag]"],
	       ["Phot2: ",W.phot1,"%.1f"%( W.zpt -2.5 *np.log10(W.phot1)  ) + " [mag]"],
	       ["Flux ratio: ",(W.phot0/W.phot1),"%.1f"%(W.phot0/W.phot1) ],
	       ["Orientation: ",W.sky_angle,"%.2f"%W.sky_angle + u'\xb0'], 
	       ["Strehl1: ",W.strehl0,"%.1f"%W.strehl0+" %"   ],
	       ["Strehl2: ",W.strehl1,"%.1f"%W.strehl1+" %"   ],
	       ]
        
          for i in lst : 
            Label(G.AnswerFrame,text=i[0]+i[2],font=G.answer_font,bg=G.bg[0]).pack(side=TOP,padx=3,pady=3)


def PlotPickMany():
      import tkFont 
                        # 1/plot the arrow
      center_click=((G.image_click[0]+G.image_release[0])/2,(G.image_click[1]+G.image_release[1])/2)  #center  Of the Event             
      tmp=matplotlib.text.Annotation(str(W.pick_type[1]),xy=center_click,xycoords='data',
               xytext=(center_click[0]+40,center_click[1]+30),textcoords='figure pixels',
	       color="red", 
               arrowprops=dict(arrowstyle="->",
               connectionstyle="arc,angleA=0,armA=30,rad=10")
               )  # accept "data", "figure fraction", see help 
      G.ax1.add_artist(tmp) 
      G.arrows.append(tmp)                  
      G.fig.canvas.draw()  	    

                         # 2/print the answer
      Label(G.AnswerFrame,text=str(W.pick_type[1])+' Strehl : '+"%.1f" % W.strehl["strehl"] + 
                  ' +/- '+ "%.1f" % W.strehl["err_strehl"],bg=G.bg[0]).pack(side=BOTTOM)#,padx=3,pady=3) 
      Label(G.AnswerFrame,text=  'FWHM :' + "%.1f"% (W.strehl["fwhm_x"]*1e3) +", "+
                  W.fit_type + '('+ 
                   "%.1f" % W.strehl["fit_dic"]['center_x']+','+ "%.1f" % W.strehl["fit_dic"]['center_y'] +')',   
                 font= tkFont.Font(size=6),bg=G.bg[0]).pack(side=BOTTOM)#,padx=3,pady=3) 
                         #3/  we create an answer_saved 
      ##############
      #### THIS IS TO SAVE 
      #for key in W.strehl["psf_fit"]:
      #   W.strehl["psf_fit"]_saved[key+"."+str(W.pick_type[1])]=W.strehl["psf_fit"][key]
      W.pick_type[1]+=1

  #if W.more_info_bool (this was for strehl2.2: 
      return     

def PlotStat(): 
  W.r = IF.Order4(W.r) 
  sub_array = W.Im0[W.r[0]:W.r[1],W.r[2]:W.r[3]]
  import Stat
  dicr = Stat.Stat(sub_array) 
  myargs = {"font":G.answer_font,"justify":LEFT,"anchor":"nw", "bg":G.bg[0] }
  row=0
  for i in dicr.keys() :
    l1 = Label(G.AnswerFrame,text=i+ ": ",**myargs) 
    l2 = Label(G.AnswerFrame,text="%.2f"%dicr[i],**myargs)
    l1.grid(row=row,column=0,sticky="nsew") 
    l2.grid(row=row,column =1,sticky="nsew")  
    row+=1
  G.AnswerFrame.grid_columnconfigure(1,minsize=150,weight=1)  
    

      ###############"
      #   1D 1D 1D 
      ###############


def PlotStar(center_max):       #will also take W.sthrel["psf_fit"] 
  if W.pick_type=="binary": # BINARY  draw radial Profile 
    PlotBinaryStar1D(center_max)
  else :  # including only one star  (ie : not binary)  
    PlotOneStar1D(center_max) 

def PlotOneStar1D(center_max): 
   #################
   ## PLOT radius profile 
   params =W.strehl      
   if W.verbose >3 : print 'center=',center_max
   fitted_center = (W.strehl["fit_dic"]['center_x'],W.strehl["fit_dic"]['center_y'] ) 
   x,y = IF.XProfile(W.Im0,fitted_center,r=W.r)  #we need to give the center (of course)
   G.figfit.clf()                                                        # RAW  DATA in X
   G.ax2 = G.figfit.add_subplot(111)
   G.ax2.plot(x+0.5,y,color='black',linestyle='steps',linewidth=1,label='Real Profile')  # x+0.5 to recenter the bar
   
   #if G.phot_type=='Aperture' or G.noise_type !=='Fit'
   rad = (W.strehl['r99x']+W.strehl['r99y'])/2             #encircled energy limit
   x0cut,x1cut=params['center_x']-rad,params['center_x']+rad
   G.ax2.axvline(x=x0cut,color='black',linestyle='-.',label='Encircled Energy')
   G.ax2.axvline(x=x1cut,color='black',linestyle='-.')
   G.ax2.axhline(y=W.strehl["background"],color='black',linestyle='-.')
   #pointsx,pointsy = IF.RadialCloud( W.Im0,(params['center_x'],params['center_y']),abs(G.r[1]-G.r[0]) )
   #G.ax2.plot(pointsx + params['center_x'],pointsy,'o')#,makersize=1)
    
   a = np.arange(min(x),max(x)+1,0.1) # we get a smaller bin for the fitted curve.  
   if not W.fit_type=='None':
                                                                            # The  FIT
      I_theory = BF.MyFit((a,params['center_y']),params,W.fit_type)
      G.ax2.plot(a,I_theory,color='purple',linewidth=2,label='Fitted PSF')
                                       # we draw just if we can see         # BESSEL
   if not W.head.wavelength*1e-6/W.head.diameter/(W.head.pixel_scale/206265)<2:  
      params2 = {'diameter':W.head.diameter,'lambda':W.head.wavelength,'center_x':params['center_x'],
              'center_y':params['center_y'],'pixelscale':W.head.pixel_scale,'phot':W.strehl["my_photometry"],
              'obstruction':W.head.obstruction/100}
      MyBessel = BF.DiffractionPatern((a,params['center_y']),params2) 
      G.ax2.plot(a,MyBessel+params['my_background'],color='blue',linewidth=2,label='Diffraction Pattern')
                                                                              # Legend
   G.ax2.legend(loc=1,prop={'size':8})
                                                                              # Axes
   def Arcsec(x): # x is the pixel
     return (x-x[0])*W.head.pixel_scale           
   def Percentage(y): #y is the intensity
     res = 100*(max(MyBessel)-W.strehl["my_background"])*y
   G.ax2.set_xlabel('Pixel')
   G.ax2.set_ylabel('Intensity')
   G.figfit.canvas.draw()
   PlotStar2()

def PlotBinaryStar1D(center_max):
   x0,y0 = W.strehl["fit_dic"]["x0"],  W.strehl["fit_dic"]["y0"]
   x1,y1 = W.strehl["fit_dic"]["x1"],  W.strehl["fit_dic"]["y1"]
   fwhm0,fwhm1 =  W.strehl["fit_dic"]["spread_x0"], W.strehl["fit_dic"]["spread_x1"]  
   
   #######
   # EXTREMITIES OF PROFILE LINE 
   line_len = np.sqrt( (x1-x0)**2 + (y1-y0)**2 )
   dx0 =  (x0-x1)/line_len * 5*fwhm0  
   dy0 =  (y0-y1)/line_len * 5*fwhm0  
   dx1 =  (x1-x0)/line_len * 5*fwhm1  
   dy1 =  (y1-y0)/line_len * 5*fwhm1  

   extremity0 = int(x0+dx0), int(y0+dy0)
   extremity1 = int(x1+dx1), int(y1+dy1)

   def Commented(): 
      return 
      #if y1>y0 :          # search order in y 
      #   extremity0 = int(x0-3*fwhm0), int(y0-3*fwhm0)
      #   extremity1 = int(x1+3*fwhm1), int(y1+3*fwhm0)
      #else  :  
      #   extremity0 = int(x0-3*fwhm0), int(y0+3*fwhm0)
      #   extremity1 = int(x1+3*fwhm1), int(y1-3*fwhm0)

      #extremity0 = int(x0- signx * 5*fwhm0), int(y0+ signy * 5*fwhm0)
      #extremity1 = int(x1+ signx * 5*fwhm1), int(y1- signy * 5*fwhm0)

   ab,od,points =  IF.RadialLine(W.Im0,(extremity0,extremity1),return_point=1)

   if "Moffat" in W.fit_type : fit_type="Moffat2pt"
   else : fit_type="Gaussian2pt"
   #ab_range =   np.min(ab) , np.max(ab) 
   ab_range =   ab[0] , ab[-1] 
   x_range  = points[0][1],points[0][-1] 
   y_range  = points[1][1],points[1][-1] 


   ab_th    = np.arange(ab_range[0],ab_range[1] ,0.1 ) 
   x_theory = np.interp(ab_th, ab_range , x_range   )
   y_theory = np.interp(ab_th, ab_range , y_range  )
   I_theory = BF.MyFit( (x_theory,y_theory) ,W.strehl["fit_dic"],fit_type)
  
   ################
   # PLOT
   G.figfit.clf() 
   G.ax2 = G.figfit.add_subplot(111)
   G.ax2.plot(ab_th+0.5,I_theory,color='purple',linewidth=2,label='Fitted PSF')
   #G.ax2.plot(ab_th,I_theory,color='purple',linewidth=2,label='Fitted PSF')
   G.ax2.plot(ab,od,color='black',linestyle='steps',linewidth=1,label='Real Profile')  # x+0.5 to recenter the bar
   G.ax2.legend(loc=1,prop={'size':8})      # Legend
   G.figfit.canvas.draw()
   G.tmp_locals = locals() 



        ####################
	#   2D 2D 2D 
	####################



def PlotStar2():   # the two images colormesh 
  if (W.pick_type=="one") or (W.pick_type[0]=="many"):
      PlotOneStar2D() 
  elif W.pick_type=="binary" :
      PlotBinaryStar2D() 


def PlotOneStar2D(): 
    x0,y0 = W.strehl["center_x"],W.strehl["center_y"]
    r99x,r99y = W.strehl["r99x"],W.strehl["r99y"]
    dx1,dx2 = int(  max(x0-4*r99x,0) ) , int( min( x0+4*r99x , len(W.Im0)  +1  ))  # d like display
    dy1,dy2 = int(  max(y0-4*r99y,0) ) , int( min( y0+4*r99y , len(W.Im0)  +1  ))  # c like cut If borders
    r = ( dx1,dx2, dy1,dy2) # Teh local cut applied to the image. To show it  
  
    x,y = np.arange(r[0],r[1]) , np.arange(r[2],r[3] ) 
    Y,X = np.meshgrid(y,x)

    ###########
    # IMAGES draw 
    # TRUE
    G.figresult.clf()         
    G.ax31=G.figresult.add_subplot(121)
    G.figresult_mappable1=G.ax31.imshow( G.current_image[r[0]:r[1],r[2]:r[3]] ,
      vmin=G.scale_dic[0]["min_cut"],vmax=G.scale_dic[0]["max_cut"],
      cmap=G.cbar.mappable.get_cmap().name, origin='lower')
      #extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")  
    # FIT 
    G.ax32=G.figresult.add_subplot(122)                   
    fit_type = W.fit_type
    if "Gaussian_hole" in fit_type : fit_type = "Gaussian_hole"
    G.figresult_mappable2=G.ax32.imshow(   vars(BF)[fit_type]((X,Y),W.strehl )     ,
       vmin=G.scale_dic[0]["min_cut"],vmax=G.scale_dic[0]["max_cut"],
       cmap=G.cbar.mappable.get_cmap().name, origin='lower',  
       #extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")  
       ) # need to comment the extent other wise too crowded and need to change rect position

    ###############"
    # APERTTURES 
    params =W.strehl
#   s   (te center of the rect is in fact the bottm left corner)    
    if (W.noise_type == "8rects") : 
       re = x0-params['r99x'],x0+params['r99x'],y0-params['r99y'],y0+params['r99y']
       var = IF.EightRectangleNoise(W.Im0,re,return_rectangle=1)[2] 
       for p in var :
           center_tmp = (p[0][0]-r[0]-p[1]/2,p[0][1]-r[2]-p[2]/2)  
           a= matplotlib.patches.Rectangle((center_tmp[1],center_tmp[0]),p[2],p[1],facecolor='orange',edgecolor='black')               
           G.ax32.add_patch(a)
       center = x0 -r[0] , y0-r[2]  
    if W.phot_type == "encircled_energy":
       a= matplotlib.patches.Rectangle((center[1]-params['r99y'],center[0]-params['r99x']),2*params['r99y'],2*params['r99x'], facecolor='none',edgecolor='black')
       G.ax32.add_patch(a)
    elif W.phot_type == "elliptical_aperture" : 
       width=2*params["r99v"] 
       height=2*params["r99u"]
       angle=params["theta"] * 180./np.pi 
       x =  params["center_x"] - r[0] 
       y =  params["center_y"] - r[2] 
       a= matplotlib.patches.Ellipse(   (y,x),width,height,angle,fc="none",ec="black"  ) 
       G.ax32.add_patch(a)

    #####
    # LABEL 
    G.ax31.set_title("True Image") 
    G.ax32.set_title("Fit") 

    G.ax32.set_yticks( (0,r[1]-r[0]) )
    G.ax32.set_yticklabels( (str(int(r[0]) ), str(int(r[1]) )  )  ) 
    G.ax32.set_xticks( (0,r[3]-r[2]) )
    G.ax32.set_xticklabels( (str(int(r[2]) ), str(int(r[3]) )  )  ) 
    #plt.xticks( (r[0],r[1] ) ) 
    #plt.xticks( (r[2],r[3] ) ) 
    G.ax31.set_xticks( () )
    G.ax31.set_yticks( () )

    G.figresult.canvas.draw()
    return 


def PlotBinaryStar2D():  
    x0,y0 = W.strehl["x0"], W.strehl["y0"] 
    x1,y1 = W.strehl["x1"], W.strehl["y1"] 
    xr,yr = 3*abs(x0-x1) , 3*abs(y0-y1) # ditances 
    dx1,dx2 = int( min(x0,x1) - xr /2 ) ,  int( max(x0,x1) + xr /2 )
    dy1,dy2 = int( min(y0,y1) - yr /2 ) ,  int( max(y0,y1) + yr /2 )
    r=( dx1,dx2,dy1,dy2) 

    # define coord for the fitted function display 
    x,y = np.arange(r[0],r[1]) , np.arange(r[2],r[3] ) 
    Y,X = np.meshgrid(y,x)

    ###########
    # IMAGES draw 
    G.figresult.clf()         
    G.ax31=G.figresult.add_subplot(121)
    G.figresult_mappable1 =G.ax31.imshow( G.current_image[r[0]:r[1],r[2]:r[3]] ,
      vmin=G.scale_dic[0]["min_cut"],vmax=G.scale_dic[0]["max_cut"],
      cmap=G.cbar.mappable.get_cmap().name, origin='lower')
      #extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")  

    if "Moffat" in W.fit_type: stg = "Moffat2pt"
    elif "Gaussian" in W.fit_type: stg = "Gaussian2pt"
    G.ax32=G.figresult.add_subplot(122)                   
    G.figresult_mappable2= G.ax32.imshow(   vars(BF)[stg]((X,Y),W.strehl )     ,
      vmin=G.scale_dic[0]["min_cut"],vmax=G.scale_dic[0]["max_cut"],
      cmap=G.cbar.mappable.get_cmap().name, origin='lower',  
      #extent=[r[2],r[3],r[0],r[1]])#,aspect="auto")  
      ) # need to comment the extent other wise too crowded and need to change rect positio
    G.figresult.canvas.draw()
    return 
        

  ###############
  ##  OLD LABELS 

# 
  #G.ax31.set_title('True Image',fontsize=10)
  #x1,y1= (int(r[0]),int(r[1])),(int(r[0]),int(r[1]))
  #G.ax31.set_xticks( (0,r[1]-r[0]) )
  #G.ax31.set_yticks( (0,r[3]-r[2]) )
  #G.ax32.set_title(str(W.fit_type)+' fit',fontsize=10)
  #x2,y2 = (0,len(W.psf_fit[3])-1),(0,len(W.psf_fit[3][0])-1)          
  #G.ax32.set_xticks(x1)
  #G.ax32.set_yticks(y1)

  #G.dpresult=FigureCanvas(G.result,master=ResultFrame)
  #G.dpresult.get_tk_widget().pack(fill=BOTH,expand=1)  


def ProjectWcs(cube_wcs): # take cube wcs return image 2D wcs 
  import pywcs

  res = pywcs.WCS(naxis=2)
  ####
  #  REJECT AXE 3 
  res.wcs.crpix = cube_wcs.wcs.crpix[:-1]
  res.wcs.crval = cube_wcs.wcs.crval[:-1] 
  res.wcs.ctype = [cube_wcs.wcs.ctype[0] ,cube_wcs.wcs.ctype[1] ] 
  res.wcs.cd  = cube_wcs.wcs.cd[:-1,:-1] 

  return res 
    #    res = AR.ProjectWcs(W.head.pywcs) 
    #    res.printwcs()



def PC(): # read W.psf_fit 
  def PCor():  # print correlation
    stg_head=","
    string=""
    cov = W.psf_fit[4]["cov"]
    keys = W.psf_fit[4]["fitOnly"]
    for i in range(len(cov) ):
      stg_head+=keys[i] +","
      string+=keys[i] +","
      for j in range(i+1) :
        string += "%.3f"%( cov[i,j] /np.sqrt( cov[i,i] * cov[j,j] ) )+","
      string=string[:-1]+"\n" # remove last "," and pass line 
    stg_head=stg_head[:-1]+"\n"
    string = stg_head+string[:-2] # remove last <newline> 
    if W.verbose > 0 : print string

    from subprocess import call 
    sh = W.path+"/print_array.sh"
    call("bash " + sh +   " '"+  string +"' ",shell=True )   
    if W.verbose > 0 : print "\n\n"


  def PFit():  # print fit 
        string= "      ##########################\n"
        string+="      #    FITTED PARAMETERS   #\n"
        string+="      ##########################\n"
        string+=   "%15s = %s \n"%('REDUCED CHI2',str(W.psf_fit[2]) ) 
        pfix=W.strehl["fit_dic"]
	uncer=W.psf_fit[1]
        for k in pfix.keys():
            string+=  "%15s = %s"%(k,pfix[k])
            if uncer[k]!=0:
                string+= ' +/- %s'%(uncer[k]) 
            string+="\n"
        if W.verbose > 0 : print string
    # result:


  try: 
    #PCor() # it is done before 
    PFit()
  except BaseException as e:
       if W.verbose > 0 : print 'Failed to do something: ' + str(e)

  return 




def ProfileAnswer():  # the output of profile line 
  def Curve() : 
    global points  # for the stat 
    G.figfit.clf()                                           # PLOT 
    G.ax2 = G.figfit.add_subplot(111)

    #DATA 
    ab,od,points =  IF.RadialLine(W.Im0,(G.my_point1,G.my_point2),return_point=1) 
    G.ax2.plot(ab,od,'-',linewidth=1,label="Data")

    #FIT  
    #if ( W.fit_type != "None" ) & ( "strehl" in vars(W) ):
    #  I_theory = BF.MyFit(points,W.strehl["fit_dic"],W.fit_type)
    #  G.ax2.plot(ab,I_theory,color='purple',linewidth=2,label='Fitted PSF')

    G.ax2.legend(loc=1,prop={'size':8})      # Legend
    G.figfit.canvas.draw()


  def Data() : 
    if W.verbose >8 : print "ProfileAnswer :" , zip(points,W.Im0[tuple(points)])
    ps = Stat.Stat(W.Im0[tuple(points)])  # like profile_stat points[0] is x and points[1] is y 
    #print points
    G.figresult.clf()
    G.ax3 = G.figresult.add_subplot(111)
    
    lst = [    ["MEAN: ",ps["mean"]]  , ["RMS: ",ps["rms"] ],  
               ["MIN: ",ps["min"]]    , ["MAX: ",ps["max"] ],    ]
    num=1.
    for i in lst:
      G.ax3.text(0.1,1.0-num/(len(lst)+1), i[0]+"%.1e"%i[1] ) 
      num+=1

    G.figresult.canvas.draw() 

  Curve() ; Data() ; return  




def CallContrastMap():    
  G.contrast_fig = matplotlib.figure.Figure() 
  ax = G.contrast_fig.add_subplot(111)

  ax.text(0.1, 0.7, 'Calculating\nContrast\nPlease Wait\n.....',
        verticalalignment='top', horizontalalignment='left',
        transform=ax.transAxes,
        color='green', fontsize=40)

  G.ContrastWindow = Tk() 
  G.ContrastWindow.title("Contrast Map") 
  G.ContrastCanvas=FigureCanvas(G.contrast_fig,master=G.ContrastWindow)   
  G.ContrastCanvas.get_tk_widget().pack(side=TOP,expand=0,fill=BOTH)
  G.contrast_fig.canvas.draw() 

  G.ContrastButtonFrame = Frame(G.ContrastWindow,bg="black")
  G.ContrastButtonFrame.pack(side=TOP,expand=0,fill=X) 

  G.ContrastButton1Frame = Frame(G.ContrastWindow,bg="black")
  G.ContrastButton1Frame.pack(side=TOP,expand=0,fill=X) 

  W.strehl["contrast_max"]=W.strehl["intensity"]


  Label(G.ContrastButton1Frame,text="Peak Intensity").grid(row=0,column=0,sticky="snew") 

  G.TEXT = Text(G.ContrastButton1Frame,height=1) 
  G.TEXT.bind()
  #  if W.verbose >3 : print "CallCOntrastMap: I got a new contrast_max", G.v1[0].get() ,   W.strehl["contrast_max"], "\nevent:", event

  #G.v1= [ ]
  #v =  StringVar()
  #G.PeakContrast1Entry = Entry(G.ContrastButton1Frame, width=10,textvariable=v,font=G.font_param )  
  #G.PeakContrast1Entry.grid(row=0,column=1,sticky="snew") 
  #G.PeakContrast1Entry.bind('<Return>',Get )
  #v.set("%.2f"%W.strehl["contrast_max"])
  #G.v1.append(v)


  def Get(event) : 
     print G.v.get() 
  






  def Worker() : 
      import ImageFunction  as IF 
      x,y,tdic = IF.ContrastMap(W.Im0,(W.strehl["center_x"],W.strehl["center_y"]),interp=True,xmin=0.5,xmax=20,step=2,dic={"theta":0,"ru":1,"rv":1},background=0) #W.strehl["my_background"])

      import MyGui as MG 
      MG.FigurePlot(x,y,dic=tdic)

  def Timer():
     from time import sleep
     sleep(0.3)
     #G.contrast_thread.E


  G.contrast_thread = Thread(target=Worker)
  G.contrast_thread.daemon = True # can close the program without closing this thread
  G.contrast_thread.start() 
  #G.contrast_timer    = Thread(target=Timer).start() 


  #G.parent.wm_attributes("-topmost", 1) 
  G.ContrastWindow.mainloop()  
  #G.parent.focus() 





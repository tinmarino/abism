import numpy as np 
import multiprocessing
from threading import Thread
import Tkinter

from timeout import timeout 
import ImageFunction as IF 
import AnswerReturn as AR 

import GuyVariables as G
import WorkVariables as W






def StrehlMeter(): # receive W.r, means a cut of the image   

  ##########################
  ## FIND   THE   CENTER  AND FWHM
  W.r = IF.Order4(W.r) 
  #IF.FindBadPixel(W.Im0,(rx1,rx2,ry1,ry2))
  star_center=IF.DecreasingGravityCenter(W.Im0,r=W.r)  #GravityCenter
  star_max,star_center = IF.LocalMax(W.Im0,star_center,size=3) 
  W.FWHM = IF.FWHM(W.Im0,star_center)
  W.background= 0



  ######################
  #  FIT   the PSF            (the most important of the software)
  import time  ; start_time = time.time()
  dictionary= {'NoiseType':W.noise_type,'PhotType':W.phot_type,'FitType':W.fit_type,"bpm":W.Im_bpm}

  @timeout(1)
  def FIT(): 
    W.psf_fit= IF.SeeingFit(W.Im0,W.r,W.fit_type,center=star_center,max=star_max,dictionary=dictionary )  
  FIT() 

  W.strehl.update(W.psf_fit[0])

  AR.PC()  # print in console 
  print  "Fit efectuated in %f seconds (from StrehlMeter)" % (time.time() - start_time)


  ### phot and noise 
  W.strehl.update(IF.Background(W.Im0,W.r,W.noise_type,dic=W.strehl) )
  W.strehl.update(IF.Photometry(W.Im0,W.r,W.phot_type,dic=W.strehl) )


  ###############
  ### Measure the strehl
  if W.strehl_type =='FTO':
       if not W.fit_type=='None': 
           star_center = W.answer['center_x'],W.answer['center_y']    
       W.fft = np.fft.fftshift(  np.abs( np.fft.fft2(IF.ImageCut(W.Im0,star_center,radius)) )**2 )
       W.photometry= IF.AperturePhot(W.fft,(0,0),radius)
       W.intensity='nan'
       W.FWHM='nan'
       W.strehl='nan' 
       #W.psf =np.fft.fftshift(np.abs(np.fft.fft2(W.P1))**2)
       #f = plt.figure(figsize=(12,5))
       #ax=plt.subplot(111)
       #ax.pcolormesh(W.fft)

  if W.strehl_type =='max':    # Now, the only one working
       W.bessel_integer = W.head.wavelength *10**(-6.) / np.pi /(W.head.pixel_scale/206265)/ W.head.diameter
       W.bessel_integer = W.bessel_integer**2 *4*np.pi / (1-(W.head.obstruction/100)**2) 
       Ith = W.strehl["my_photometry"] /W.bessel_integer
       if W.verbose>3 : print '---->MyGui.py,strehl -> diff-max :', Ith
       strehl = W.strehl["intensity"] / Ith *100
  
  W.strehl["strehl"]=strehl


  #################
  ##### ERROR estimation
  dictionary = {'Ith':Ith,'Sr':strehl,'bessel_integer':W.bessel_integer,"type":"S/N"}
  W.strehl["err_strehl"]  = IF.Error(W.Im0,dictionary=dictionary)  # SAVE ANSWER IN W 
     
      

  AR.PlotAnswer()		
  if W.fit_type != "None"  : # bite 
      AR.PlotStar(star_center)	    # we transport star center, because if it is bad, it is good to know, this star center was det by iterative grav center  the fit image is a W.psf_fit[0][3]	     
 
  #AR.CallContrastMap()

  return 
	  
def BinaryStrehl() :  
    dictionary={'star1':G.star1,'star2':G.star2,"fit_type":W.fit_type}
    if W.same_psf: dictionary["same_psf"]=1
    else :dictionary["same_psf"]=0
   
    @timeout(1)
    def FIT(): 
      W.psf_fit = IF.BinaryPSF2(W.Im0,dictionary)
    FIT() 

    W.strehl = W.psf_fit[0]
    G.fig.canvas.mpl_disconnect(G.pt2) 
    if W.verbose>3 : print "Binary res :" ,W.psf_fit

    AR.PlotAnswer()
    AR.PlotStar2()
    AR.PlotStar("bidon")


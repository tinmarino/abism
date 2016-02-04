# ImageFunction works on array to separe matematics and graphics = to hide the misery.
import numpy as np
import scipy.ndimage # for the median filter 
import scipy.interpolate # for LocalMax 

import MyGui as MG # for the plot of the contrast map 


import Stat
import FitFunction as FF
import BasicFunction as BF

import GuyVariables as G
import WorkVariables as W


#To comment then 
import warnings 
#from matplotlib import pyplot as plt 
 




def Order2((a,b)):
  if a>=b : return (b,a)
  else : return (a,b)

def Order4(r):
  rx1,rx2,ry1,ry2 = r[0], r[1], r[2], r[3] 
  if rx1>rx2:
    tmp=rx1
    rx1=rx2
    rx2=tmp
  if ry1>ry2:
    tmp=ry1
    ry1=ry2
    ry2=tmp
  return (rx1,rx2,ry1,ry2)
  

def LocalMax(grid,center,size=4): # size useless 
    #CUT 
    x0,y0 = int(center[0]) , int(center[1] ) 
    reindex = center[0]-2, center[1]-2
    x = np.arange(x0-2,x0+2)
    y = np.arange(y0-2,y0+2)
    xx = np.arange(reindex[0],center[0]+2,0.01) 
    yy = np.arange(reindex[1],center[1]+2,0.01) 
    grid = grid[  center[0]-2:center[0]+2 ,  center[1]-2:center[1]+2]
    print "shape ", grid.shape, len(x) , len(y)  

    # FILT 
    mIX =  scipy.ndimage.uniform_filter(grid, size=(3,3) ) 
    bol1 = np.abs(grid-mIX)>mIX
    grid[bol1] = mIX[bol1]

    # INTERPOLATE 
    grid = scipy.interpolate.interp2d(x,y,grid,kind="cubic")  
    grid = grid(xx,yy) 
    coord =  np.unravel_index(grid.argmax(), grid.shape)

    res =  grid[coord[0],coord[1]],( float(coord[0])/100 +reindex[0], float(coord[1])/100 +reindex[1])  
    if W.verbose > 3 : print " LocalMax@ImageFunction.py : ", res
    return res 


def GravityCenter(grid,center=None,rad=None,r=None,bol=None):  
  # radius of a square    /RETURN: center , means (x,y) 
  # bol is the bollean of teh selected pixels 

  #1/ Create Constants 
  if r==None: 
     (x0,y0)=int(center[0]) , int(center[1])
     my_r = int(rad) 
     rx1,rx2,ry1,ry2=x0-my_r,x0+my_r,y0-myr,y0+my_r
     x=np.arange(-my_r,my_r+1)
     y=np.arange(-my_r,my_r+1)
  else:   
       tmp=Order4(r)
       rx1,rx2,ry1,ry2 = int(tmp[0]) ,  int(tmp[1]) , int(tmp[2]) , int(tmp[3]) 
       x=np.arange(rx1,rx2+1)
       y=np.arange(ry1,ry2+1)

       # Create R, distance from x0,y0
  Y,X = np.meshgrid(y,x) 
      #R =  np.sqrt( Y**2+ X**2 ) 

  #2/ cut grid) 
  cutted = grid[  rx1:rx2+1, ry1:ry2+1 ]
  my_sum = np.sum(cutted) 

  #3/ get the gravity center 
  x1 = np.sum( cutted*X ) / my_sum
  y1 = np.sum( cutted*Y ) / my_sum
  
  return (x1,y1)


def FindMaxWithIncreasingSquares(grid,center): # center is th ecenter click 
  size_max=20
  return   



def DecreasingGravityCenter(grid,r=None,binfact=2,radiusmin=4): # call with radius each time samller 
  """ Get the center of gravity with decreasing squares around the previous gravity center """

  G=GravityCenter(grid,r=r)
  rx1,rx2,ry1,ry2=r # need to do that to avoid error mess 'tuple' object do not support item assignment 
  if (r[1]-r[0] > radiusmin): 
    dist   = float((r[1]-r[0]))/2/binfact
    if W.verbose > 2 : print "DecreasingGravityCenter" ,"r",r 
    rx1 = int( G[0] - dist ) 
    rx2 = int( G[0] + dist ) 
  if  (r[3]-r[2]> radiusmin)  :
    dist   = float((r[3]-r[2]))/2/binfact
    ry1 = int( G[1] - dist ) 
    ry2 = int( G[1] + dist ) 
  elif (r[1]-r[0] <= radiusmin):  # now we can leave the function
    return G 

  return DecreasingGravityCenter(grid,r=(rx1,rx2,ry1,ry2))


def FWHM(grid,centermax,direction='average'):    # Find one of the half Maximum without precision  in direction (x,-x,y,-y)
   (x,y)=centermax                                           #center should be the max pixel. 
   i,j=int(x),int(y)                                                  # RETURN  float
   if direction =='average':
      res=FWHM(grid,centermax,direction='x')
      res+=FWHM(grid,centermax,direction='-x')
      res+=FWHM(grid,centermax,direction='y')
      res+=FWHM(grid,centermax,direction='-y')
      res/=4
      return res +0.5
   else:
      while (grid[i][j]>grid[int(x)][int(y)]/2):
         if W.verbose>3 : print 'FWHM :i,j,I=',i,j,grid[i][j],direction
         if direction=='x':i+=1
         if direction=='-x':i-=1
         if direction=='y':j+=1
         if direction=='z':j-=1
         if grid[i][j]>grid[int(x)][int(y)]/2 : break
      return np.sqrt((j-y)**2+(i-x)**2)*2



def PointIntensity(grid,point):  #point is the coord of the exact point you need to assess intensity from linear assuption of nearest pixels, bite seems to be slow tooo
  res,M=0,0
  (x,y)=point
  (i,j)= (int(x),int(y))
  if ((i,j)==(x,y)): return grid[i][j]  
  else: 
    try :
      tmp=1/ ( np.sqrt( (x-i)**2+(y-j)**2 ))
      res += grid[i][j]/ ( np.sqrt( (x-i)**2+(y-j)**2 ))
      M += 1/ ( np.sqrt( (x-i)**2+(y-j)**2 ))
    except: pass
    try :
      tmp=1/ ( np.sqrt( (x-(i+1))**2+(y-j)**2 ))
      res += grid[i+1][j]*tmp
      M += tmp
    except : pass
    try: 
      tmp=1/ ( np.sqrt( (x-i)**2+(y-(j+1))**2 ))
      res += grid[i][j+1]
      M+= tmp
    except : pass
    try:
      tmp=1/ ( np.sqrt( (x-(i+1))**2+(y-(j+1))**2 ))
      res += grid[i+1][j+1]
      M+= tmp
    except : pass 
  return res/M  
  

#def PixelMax(grid,r=None):   # RETURN center, max (=2+1floats)
#                             # bite make a median filter to remove bad pixels ? 
#  if r != None : 
#    (rx1,rx2,ry1,ry2)=r
#    grid=grid[rx1:rx2,ry1:ry2]
#  max   =np.max(grid) 
#  coord =np.array( np.where(grid==max) )[:,0] # [:,0] because where returns the indexes of each occurence, one line for each occurence.   
#  return coord,max  
  

def PixelMax(grid,r=None):   # array.float , 2 float , 1 float     RETURN center, max (=2+1floats)
  l=len(grid)
  x,y=0,0
  m=0   #m will be the maximum value of a pixel
  if r==None : 
    for i in range (len(grid)):
      for j in range (len(grid[i])): 
	try:
	  if grid[i][j]>m: 
	    m=grid[i][j]
	    (x,y)=(i,j)
	except : pass   
  else : 
    rx1,rx2,ry1,ry2 =Order4(r)  
    for i in range (int(rx1), int(rx2+1)):
      for j in range (int(ry1),int(ry2)+1): 
	try:
	  if grid[i][j]>m: 
	    m=grid[i][j]
	    (x,y)=(i,j)
	except : pass
  return (x,y),m	  


def GoodPixelMax(grid,r=(10,10,10,10)):   # array.float , 2 float , 1 float
  m,bad=0,[]   #m will be the maximum value of a pixel,bad are the BadPixels coord
  (rx1,rx2,ry1,ry2) =  r 
  for i in range (int(rx1),int(rx2+1)):
    for j in range (int(ry1),int(ry2+1)): 
      if (i,j) in bad : pass
      else:
	try:  # in case we are out of the grid
	  if grid[i][j]>m:
	    m=grid[i][j]
	    (x,y)=(i,j)
	except : pass
  if  (grid[x-1][y] < grid[x][y]/10 
			and grid[x][y-1] < grid[x][y]/10
			and grid[x+1][y] < grid[x][y]/10
			and grid[x][y+1] < grid[x][y]/10):
    bad.append((x,y))
  return (x,y),m    



  # This is background in not only  Our rectangle " should change name 
def EnergyRadius(grid,fit_type,dic={}):
  """ We first define r99u and v following the spread direction x and y respectively, 
  we then transfroms it to r99x and y """
  params = dic # because no update  
  ############
  # GAUSSIAN
  if (fit_type=='Gaussian'):  # 2.14 for 99% energy, we ll use 3.14
    r99u = 3.14 * params['spread_x']
    r99v = 3.14 * params['spread_x']    
  if (fit_type=='Gaussian2D'):
    r99u = 3.14 * params['spread_x']
    r99v = 3.14 * params['spread_y']    
  if ('Gaussian_hole' in fit_type):  # 2.14 for 99% energy, we ll use 3.14
   if params.has_key('spread_y'):
    r99u = 3.14 * params['spread_x']
    r99v = 3.14 * params['spread_y']
   else: 
    r99u = 3.14 * params['spread_x']
    r99v = 3.14 * params['spread_x']

  ###############
  # MOFFAT 
  if (fit_type=='Moffat'): #r99 = r90
    #r99u= params['spread_x'] * np.sqrt( (0.1)**(1/(1-params['exponent'])) -1 )
   r99v,r99u= params['spread_x'] * 7 ,  params['spread_x'] * 7 
  if (fit_type=='Moffat2D'):  # r99 = r90
    r99u,r99v = params['spread_x'] * 7 ,params['spread_y'] * 7 

  ############
  # BESSEL and None 
  if (fit_type=='Bessel1'):  # take cara r99 = R90
    r99u = 5.8 * params['spread_x']
    r99v = 5.8 * params['spread_x']    
  if (fit_type=='Bessel12D'):  # take cara r99 = R90
    r99u = 5.8 * params['spread_x'] 
    r99v = 5.8 * params['spread_y']   
  if (fit_type=='None'):
    r99u,r99v = params["r99x"],  params["r99y"]

  ###########
  # r99x and r99y  ROTATE 
  if params.has_key("theta"):
    r99x = r99u * abs(np.cos(params["theta"]))  + r99v *  abs(np.sin(params["theta"]) )
    r99y = r99u * abs(np.sin(params["theta"]))  + r99v *  abs(np.cos(params["theta"]) ) 
  else : 
    r99x,r99y = r99u,r99v

  if W.verbose>3 : print "------>EnergyRadius(ImageFunction.py)->",(r99x,r99y)	    
  return (r99x,r99y),(r99u,r99v) 


def SeeingFit(grid,r,fit_type,center=(0,0),max=1,dictionary={},full_answer=True): 
  """full_answer get the photometry and the background """
   #dictionary will be used for the noise or not 
  (x0,y0),(rx1,rx2,ry1,ry2)=center,Order4(r)
  if W.verbose>3 : print "----->Seeingfit@ImageFunction.py -> r: " ,rx1,rx2,ry1,ry2,'center :',center 
  PMax=max
  X,Y=np.arange(int(rx1),int(rx2)+1),np.arange(int(ry1),int(ry2)+1)
  y,x = np.meshgrid(Y,X)        # We have to inverse because of matrix way 
  IX=grid[rx1:rx2+1,ry1:ry2+1]  # the cutted image 
  mIX = scipy.ndimage.uniform_filter(IX,3) # convolve with constant kernel  
  #eIX = 10 * ( np.abs(IX-mIX) ) # the error 
  if not "bite_error" in vars(G) : G.bite_error = 1  
  eIX =G.bite_error *  (IX-mIX).std() *np.ones(IX.shape) 
  #eIX = np.maximum( np.nan_to_num(np.sqrt(IX) ) , eIX ) 

  try :
    BPM =dictionary["bpm"][rx1:rx2+1,ry1:ry2+1]
    BPM[BPM==0] = np.inf  # chang 0 to inf = not fitted 
    eIX *= BPM
  except : pass 
  eIX = np.nan_to_num(eIX) 
  eIX[eIX==0] = np.inf
  my_fwhm = FWHM(grid,center)    
  try : NoiseType =dictionary['NoiseType']    # read noise and phot type
  except :   NoiseType = 'in_rectangle'
  try : PhotType = dictionary['PhotType']
  except : PhotType = 'encircled_energy'
         # SEE Noise Not to fit it 
  if NoiseType == 'None':doNotFit=['background']
  #elif NoiseType[0] == 'Annulus': 
    #IX = IX/AnnulusPhot(grid,center,NoiseType[1],NoiseType[2])
  else : doNotFit=[]  #include  'Fit'
          #Background

                              ############
                              #  FIT 
                              #############

  if W.verbose>0 :verbose =1 
  if (fit_type=="Gaussian2D"):    # 0.83 = sqrt(ln(2))
     doNotFit.append('exponent')
     SuposedParams={'center_x':x0,'center_y':y0,'spread_x':0.83*(my_fwhm),'spread_y':0.83*my_fwhm,
                    'intensity':PMax,'theta':0.1,'background':0}
     res = FF.leastsqFit(BF.Gaussian2D,(x,y),SuposedParams,IX,err=eIX,doNotFit=doNotFit,verbose=verbose)  

  elif(fit_type=='Gaussian'):
    doNotFit.append('exponent')    
    SuposedParams={'center_x':x0,'center_y':y0,'spread_x':0.83*(my_fwhm),'intensity':PMax,'background':0}   
    res = FF.leastsqFit(BF.Gaussian,(x,y),SuposedParams,IX,err=eIX,doNotFit=doNotFit,verbose=verbose)  

  elif ("Gaussian_hole" in fit_type): # we consider 2D or not, same_center or not 
     SuposedParams={'center_x':x0,'center_y':y0,'spread_x':0.83*(my_fwhm),'spread_y':0.83*my_fwhm,
                    'center_x_hole':x0,'center_y_hole':y0,'spread_x_hole':0.83*(my_fwhm),'spread_y_hole':0.83*my_fwhm,
                    'intensity':PMax,'intensity_hole':0,'theta':0.1,'theta_hole':0.1,'background':0}
     if not ("2D" in fit_type): 
           SuposedParams["2D"]=0 
           doNotFit.append("theta"); doNotFit.append("theta_hole")
           doNotFit.append("spread_y"); doNotFit.append("spread_y_hole")
     else : SuposedParams["2D"]=1 
     if ("same_center" in fit_type): 
           SuposedParams["same_center"]=1
           doNotFit.append("center_x_hole"); doNotFit.append("center_y_hole")
     doNotFit.append("2D"); doNotFit.append("same_center")
     res = FF.leastsqFit(BF.Gaussian_hole,(x,y),SuposedParams,IX,err=eIX,doNotFit=doNotFit,verbose=verbose)  

  elif (fit_type=='Moffat'): # 1.5 = /np.sqrt(1/2**(-1/b)-1)
    SuposedParams={'center_x':x0,'center_y':y0,'spread_x':1.5*my_fwhm,'intensity':PMax,'background':0,'exponent':2}    
    res = FF.leastsqFit(BF.Moffat,(x,y),SuposedParams,IX,err=eIX,doNotFit=doNotFit,verbose=verbose) 

  elif (fit_type=="Moffat2D"):    # 0.83 = sqrt(ln(2))
     SuposedParams={'center_x':x0,'center_y':y0,'spread_x':0.83*(my_fwhm),'spread_y':0.83*my_fwhm,
                    'intensity':PMax,'theta':0.1,'background':0,'exponent':2}
     res = FF.leastsqFit(BF.Moffat2D,(x,y),SuposedParams,IX,err=eIX,doNotFit=doNotFit,verbose=verbose)     

  elif (fit_type=='Bessel1'):
    doNotFit.append('exponent')    
    SuposedParams={'center_x':x0,'center_y':y0,'spread_x':0.83*(my_fwhm),'intensity':PMax,'background':0,'exponent':2}  
    res = FF.leastsqFit(BF.Bessel1,(x,y),SuposedParams,IX,err=eIX,doNotFit=doNotFit,verbose=verbose)

  elif (fit_type=="Bessel12D"):    # 0.83 = sqrt(ln(2))
     doNotFit.append('exponent')
     SuposedParams={'center_x':x0,'center_y':y0,'spread_x':0.83*(my_fwhm),'spread_y':0.83*my_fwhm,
                    'intensity':PMax,'theta':0.1,'background':0}
     res = FF.leastsqFit(BF.Bessel12D,(x,y),SuposedParams,IX,err=eIX,doNotFit=doNotFit,verbose=verbose)      

  else: # including fit_type=='None', return the image 
      restmp = {'center_x':x0,'center_y':y0,'intensity':PMax,"r99x":5*my_fwhm,"r99y":5*my_fwhm }
      res= (restmp,0,0, IX,0 )





  ######
  ## DICTIONARY , backup and star improving   
  if (not "2D" in fit_type) and (not fit_type == "None")  :  
    try :
      res[0]["spread_y"],res[0]["spread_x"]= res[0]["spread"], res[0]["spread"]
      res[1]["spread_y"],res[1]["spread_x"]= res[1]["spread"], res[1]["spread"]
    except : 
      res[0]["spread_y"],res[0]["spread_x"]= res[0]["spread_x"], res[0]["spread_x"]
      res[1]["spread_y"],res[1]["spread_x"]= res[1]["spread_x"], res[1]["spread_x"]

  tmp={}
  tmp.update(res[0])
  res[0]["fit_dic"]=tmp





  #############
  #  FITTED WALUES : PHOT and FWHM, backgorund  from f FIT 
  if full_answer  :  
       ##########"
       # GAUSSIAN
       if ('Gaussian' in fit_type):
         if not "2D" in fit_type : 
            try :  res[0]["spread_y_hole"]=res[0]["spread_x_hole"]
            except : pass
         photometry= np.pi*res[0]['intensity']*res[0]['spread_x']*res[0]['spread_y']
         if "hole" in fit_type : photometry-= np.pi*res[0]['intensity_hole']*res[0]['spread_x_hole']*res[0]['spread_y_hole']
         fwhm_x=2*np.sqrt(np.log(2))*abs(res[0]['spread_x'])   
         fwhm_y=2*np.sqrt(np.log(2))*abs(res[0]['spread_y'])    

        ############
	#### MOFFAT
       elif fit_type=='Moffat':
             if res[0]['exponent']>1:
               photometry= np.pi*res[0]['intensity']*res[0]['spread_x']**2/(res[0]['exponent']-1)
             else : photometry=0
             fwhm =2* abs(res[0]['spread_x'])* np.sqrt(  (0.5)**(-1/res[0]['exponent'])-1)
             fwhm_x,fwhm_y = fwhm,fwhm

       elif fit_type=='Moffat2D':
             if res[0]['exponent']>1:
               photometry= np.pi*res[0]['intensity']*res[0]['spread_x']*res[0]['spread_y']/(res[0]['exponent']-1)
             else : photometry =0     
             fwhm_x =2* abs(res[0]['spread_x'])* np.sqrt(  (0.5)**(-1/res[0]['exponent'])-1) 
             fwhm_y =2* abs(res[0]['spread_y'])* np.sqrt(  (0.5)**(-1/res[0]['exponent'])-1) 

         ##########
	 ## BESSEL
       elif fit_type=='Bessel1':
             photometry= 4*np.pi*res[0]['intensity']*res[0]['spread_x']**2
             fwhm_x = 2 * res[0]['spread_x'] * 1.61
             fwhm_y = 2 * res[0]['spread_x'] * 1.61	

       elif fit_type =='Bessel12D':
             photometry= 4*np.pi*res[0]['intensity']*res[0]['spread_x']*res[0]['spread_y']
             fwhm_x = 2 * res[0]['spread_x'] * 1.61
             fwhm_y = 2 * res[0]['spread_y'] * 1.61	        

       elif fit_type =='None':
	   #radius = 5*FWHM
	   photometry = Stat.RectanglePhot(grid,(rx1,rx2,ry1,ry2),get=["sum"] )["sum"]  
	   fwhm = my_fwhm 

       try :
         res[0]['fwhm_x'],res[0]['fwhm_y']=fwhm_x,fwhm_y
       except : 
         res[0]['fwhm_x'],res[0]['fwhm_y']=fwhm,fwhm
       if fit_type != "None" : # otherwise, there is no fit 
          res[0]["photometry_fit"] = photometry 
          res[0]["background_fit"] = res[0]["background"] 



       # UPDATE R99X 
       (r99x,r99y),(r99u,r99v) =EnergyRadius(grid,W.fit_type,dic=res[0]) # the apertur radius 
       res[0]["number_count"] = r99x * r99y 
       res[0]["r99x"], res[0]["r99y"]= r99x,r99y 
       res[0]["r99u"], res[0]["r99v"]= r99u,r99v 

  return res     


def Background(grid,r,NoiseType,dic={}): 
  ##################
  # Bck and rms  
  if W.verbose >3 : print "NOISE : ", NoiseType, type(NoiseType) 
  if NoiseType=='in_rectangle':                            # change noise  from fit
    dic['my_background']=back/back_count 
    rms = 0.
    for i in listrms : rms+= (i-dic['my_background'])**2
    rms = np.sqrt(rms/(len(listrms)-1))
    dic['rms'] = rms

  elif NoiseType=='8rects':
    xtmp,ytmp = dic['center_x'],dic['center_y']
    r99x,r99y = dic["r99x"], dic["r99y"]
    restmp= EightRectangleNoise(grid,(xtmp-r99x,xtmp+r99x,ytmp-r99y,ytmp+r99y))
    dic['my_background'],dic['rms'] = restmp["background"], restmp['rms'] 
    if W.verbose > 3 : print " ImageFunction.py : Background, I am in 8 rects "

  elif NoiseType[0]=='manual':
    rms,back=[],[]
    for r in NoiseType[1]:
       tmp = Stat.RectanglePhot(grid,r,dic={"get":["rms","number_count","sum"]})
       rms.append(tmp["rms"])
       back.append(tmp["sum"]/tmp["number_count"])
    dic["my_background"],dic["rms"]= np.mean(rms),np.mean(back)

  elif NoiseType=='fit': 
    try : dic['rms']=W.psf_fit[1]['background']
    except : dic['rms']=["No_in_fit"]
    dic['my_background']=dic["background"]


  elif NoiseType=='None':
     dic['my_background']=  0
     dic['background']=dic['my_background']

  else :
     dic['rms']=-99
     dic['my_background']=-99
   
  return dic 

  #######################
  # PHOTOMETRY 
  #########################


def Photometry(grid,r,PhotType,dic={}):
  #PhotType = "elliptical_aperture"
  #print "Seiing fit , elliptical aperture called " 
  r99x,r99y =  dic["r99x"], dic["r99y"]
  r99u,r99v =  dic["r99u"], dic["r99v"]

  x0,y0 = dic['center_x'], dic['center_y']
  ax1,ax2 = x0-r99x, x0+r99x 
  ay1,ay2 = y0-r99y, y0+r99y 



  if PhotType=='encircled_energy':                             # change photometry
    tmp=  Stat.RectanglePhot(grid,(ax1,ax2,ay1,ay2))
    photometry= tmp["sum"]
    dic["number_count"]= tmp["number_count"]
    dic["my_photometry"]=photometry - dic["number_count"]* dic["my_background"] 
    if W.verbose >3 : print "doing encircled energy in ImageFunction.py "


  elif PhotType=="elliptical_aperture":
    """ we take the int of everything """
    ####
    # cut image
    myrad = int (r99u + r99v)
    theta = 0 
    if dic.has_key("theta") :   theta = dic["theta"]
    x0,y0 = int(dic["center_x"]), int(dic["center_y"]) 

    if W.verbose > 2 :  print "size of the myrad, of the phot", myrad 
    cx1,cx2 = max(x0-myrad,0), min(x0+myrad,len(grid)+1  )  # c like cut If borders
    cy1,cy2 = max(y0-myrad,0), min(y0+myrad,len(grid[0])+1  )  # If borders
    im_cut = grid[cx1:cx2,cy1:cy2]
    

    bol   = EllipticalAperture(im_cut,dic={"center_x":x0-cx1,"center_y":y0-cy1,"ru":r99u,"rv":r99v,"theta":theta} )["bol"] 
    if W.verbose > 2 : print "phot len" , len(bol) , len(im_cut) 
    if W.verbose >3 : print "ImageFUnciton, Photometry " ,r99u,r99v,theta 
    phot =Stat.Stat(im_cut[bol],get=["number_count","sum"] ) 
    if W.verbose > 2 : print "phot", phot
    dic["number_count"]  = phot["number_count"] 
    dic["my_photometry"] =  phot["sum"]- phot["number_count"]* dic["my_background"]



  elif PhotType=='manual':
     #tmp = pStat.RectanglePhot(grid,r,  dic={"get":["number_count","rms"]} )
     tmp= Stat.RectanglePhot(grid,r) 
     photometry= tmp["sum"]
     dic["number_count"]= tmp["number_count"]
     dic["my_photometry"]=photometry - dic["number_count"]* dic["my_background"] 
     if W.verbose >3 : print "doing manual phot in ImageFunction.py "
  elif PhotType =='fit':
     dic["my_photometry"] = dic["photometry_fit"] 
     if W.verbose >3 : print "doing fit  phot in ImageFunction.py "




  ###########
  ## LONG SHORT AXE, ELLIPTICITY
  dic["fwhm_a"]= max( dic["fwhm_x"], dic["fwhm_y"])
  dic["fwhm_b"]= min( dic["fwhm_x"], dic["fwhm_y"])
  dic["eccentricity"] = np.sqrt( dic["fwhm_a"]**2 - dic["fwhm_b"]**2  )/dic["fwhm_a"]
  
  #########"
  ## INVERT X Y To be done 

  return dic 
  

                                    #########################
                                    ##        ERROR       ###
                                    #########################
 


def Error(grid,dictionary={"type":"fit"}):
     #read W.psf_fiti, W.strehl because psf_fit also take the cutted image
   Ith,Sr,bessel_integer= dictionary['Ith'],dictionary['Sr'],dictionary['bessel_integer']
   # BACKGROUND       
   dBack = W.strehl["rms"]
   # PHOTOMETRY
   dPhot = dBack * np.sqrt( W.strehl["number_count"] ) 
     #dFlux_up = dPhot - A*dBack       # if we have to much flux 
   
   # INTENSITY 
   if W.fit_type != "None" : 
      dI = W.psf_fit[1]["intensity"]
   else : # bite should calculate err with median filter before 
      dI = 1

   dIpsf = np.sqrt(  dI**2  +  dBack**2  ) # error from peak 
   dIth = dPhot/bessel_integer           # error from phot 
   dSr =     abs(dIpsf) + Sr/100 * abs(dIth)    
   dSr/=     Ith
   dSr*=100 
   return dSr
  

  
def BinaryPSF(grid,dictionary,search=False):

   ##########
   ## DEFINE VARS 
   star0= dictionary['star1']
   star1= dictionary['star2']
   fit_type= dictionary['fit_type']

   try : phot_type = dictionary["phot_type"]
   except : 
     phot_type = 'fit'
     if W.verbose >0 : print "Warining not phot_type, setted to fit (from imageFunction)"  
   try : noise_type = dictionary["noise_type"]
   except : 
     noise_type = 'fit'
     if W.verbose >0 : print "Warining not noise_type, setted to fit (from imageFunction)"  



   ###########
   #  INITIAL CONDITIONS   search or not for the max
   if not search:
      max0 = star0
      max1 = star1   
      

   dist0 = FWHM(grid,max0) 
   dist1 = FWHM(grid,max1)
   my_range = (abs(max0[0]-max1[0]) + abs(max0[1]-max1[1])) + 5 * max(dist0,dist1)
   my_center = [(max0[0]+max1[0])/2 , (max0[1]+max1[1])/2 ]
       # the error
   rx1,rx2=  int(my_center[0] - my_range/2) ,  int(my_center[0] + my_range/2)
   ry1,ry2 = int(my_center[1] - my_range/2) ,  int(my_center[1] + my_range/2)
   
   ########
   # DEFINE fitting space 
   if W.verbose>2:
         print "----->IF.BinaryPSF :"
         print "The fit is done between points ", (rx1,ry1)," and ", (rx2,ry2) 
         print  "with fit", fit_type 
   X,Y=np.arange(int(rx1),int(rx2)+1),np.arange(int(ry1),int(ry2)+1)
   y,x = np.meshgrid(Y,X) 
   IX=grid[rx1:rx2+1,ry1:ry2+1]
   IX,mIX=FindBadPixel(IX)#,r=r)
   eIX = (IX-mIX).std() 
   eIX *= np.ones(IX.shape)
   ###################
   ## THE BINARY FIT #
   ###################
   doNotFit = ["same_psf","aniso"]             # Anisoplanetsim and same_psf boolean never fitted
   if "Bessel" in fit_type : 
      if W.verbose >0 : print "WARNING : no bessel 2pt fit type now,fit type is set to gaussian"
      fit_type="Gaussian"
   if ("Gaussian" or "Moffat" in fit_type):    # 0.83 = sqrt(ln(2))
   
      if not dictionary['same_psf']:
		if not '2D' in fit_type :         # circular psf 
		      SuposedParams={'x0':max0[0],'x1':max1[0],'y0':max0[1],'y1':max1[1],
				      'spread_x0':0.83*(dist0),'spread_x1':0.83*dist1,                   
					'intensity0':grid[max0[0]][max0[1]],'intensity1':grid[max1[0]][max1[1]],
					'background':0, "same_psf":0,"aniso":0
				    }
                      if "Gaussian" in fit_type : # Gaussian != psf
	                   res = FF.leastsqFit(BF.Gaussian2pt,(x,y),SuposedParams,
					    IX,err=eIX,doNotFit=doNotFit) 
                      else :                      # Moffat != psf
                           SuposedParams['b0'],SuposedParams['b1']=1.8,1.8
	                   res = FF.leastsqFit(BF.Moffat2pt,(x,y),SuposedParams,
					    IX,err=eIX,doNotFit=doNotFit) 
                           		
	
		else :                            # including 2D
		      SuposedParams={'x0':max0[0],'x1':max1[0],'y0':max0[1],'y1':max1[1],
				      'spread_x0':0.83*(dist0),'spread_x1':0.83*dist1, 
				      'spread_y0':0.83*(dist0),'spread_y1':0.83*dist1,
				      'theta':1,
					'intensity0':grid[max0[0]][max0[1]],'intensity1':grid[max1[0]][max1[1]],
					'background':0,"same_psf":0,"aniso":1
				    }
                      if "Gaussian" in fit_type :  # Gaussian2D != psf 
		           res = FF.leastsqFit(BF.Gaussian2pt,(x,y),SuposedParams,
					  IX,err=eIX,doNotFit=doNotFit) 
                      else  :                      # Moffat 2D != psf 
                           SuposedParams['b0'],SuposedParams['b1']=1.8,1.8
	                   res = FF.leastsqFit(BF.Moffat2pt,(x,y),SuposedParams,
					    IX,err=eIX,doNotFit=doNotFit) 
					  


      else :                                      #including same_psf
	        if not '2D' in fit_type :
		      doNotFit.append('spread_x1')
		      SuposedParams={'x0':max0[0],'x1':max1[0],'y0':max0[1],'y1':max1[1],
				      'spread_x0':0.83*(dist0),'spread_x1':0.83*dist1,                   
					'intensity0':grid[max0[0]][max0[1]],'intensity1':grid[max1[0]][max1[1]],
					'background':0,"same_psf":1,"aniso":0
				    }
                      if "Gaussian" in fit_type : # Gaussian same_psf  
		           res = FF.leastsqFit(BF.Gaussian2pt,(x,y),SuposedParams,
					  IX,err=eIX,doNotFit=doNotFit) 			
                           res[0]["spread_x1"]=res[0]["spread_x0"]
                      else  :                      # Moffat  same_psf 
                           doNotFit.append("b1")
                           SuposedParams['b0'],SuposedParams['b1']=1.8,1.8
	                   res = FF.leastsqFit(BF.Moffat2pt,(x,y),SuposedParams,
					    IX,err=eIX,doNotFit=doNotFit) 
                           res[0]["spread_x1"]=res[0]["spread_x0"]
                           res[0]["b1"]=res[0]["b0"]


	        else :                             # including 2D
		      doNotFit.append('spread_x1')
                      doNotFit.append("spread_y1")
		      SuposedParams={'x0':max0[0],'x1':max1[0],'y0':max0[1],'y1':max1[1],
				      'spread_x0':0.83*(dist0),'spread_x1':0.83*dist1, 
				      'spread_y0':0.83*(dist0),'spread_y1':0.83*dist1,
				      'theta':1,
					'intensity0':grid[max0[0]][max0[1]],'intensity1':grid[max1[0]][max1[1]],
					'background':0,"same_psf":1,"aniso":1
				    }
                      if "Gaussian" in fit_type : # Gaussian2D  same_psf  
		           res = FF.leastsqFit(BF.Gaussian2pt,(x,y),SuposedParams,
					  IX,err=eIX,doNotFit=doNotFit)
                           res[0]["spread_x1"]=res[0]["spread_x0"]
                           res[0]["spread_y1"]=res[0]["spread_y0"]
                      else  :                      # Moffat2D   same_psf 
                           doNotFit.append("b1")
                           SuposedParams['b0'],SuposedParams['b1']=1.8,1.8
	                   res = FF.leastsqFit(BF.Moffat2pt,(x,y),SuposedParams,
					    IX,err=eIX,doNotFit=doNotFit) 
                           res[0]["spread_x1"]=res[0]["spread_x0"]
                           res[0]["spread_y1"]=res[0]["spread_y0"]
                           res[0]["b1"]=res[0]["b0"]
   res[0]["fit_dic"]= res[0]			  


		 
   # PHOTOMETRY, BACKGROUND
   if "Gaussian" in fit_type :
     if "2D" in fit_type :
      photometry0= np.pi*res[0]['intensity0']*res[0]['spread_x0']*res[0]['spread_y0']
      photometry1= np.pi*res[0]['intensity1']*res[0]['spread_x1']*res[0]['spread_y1']
     else : 
      photometry0= np.pi*res[0]['intensity0']*res[0]['spread_x0']**2
      photometry1= np.pi*res[0]['intensity1']*res[0]['spread_x1']**2
   if "Moffat" in fit_type :
     if "2D" in fit_type : 
      photometry0= np.pi*res[0]['intensity0']*res[0]['spread_x0']*res[0]['spread_y0']/(res[0]['b0']-1)
      photometry1= np.pi*res[0]['intensity1']*res[0]['spread_x1']*res[0]['spread_y1']/(res[0]['b1']-1)
     else : 
      photometry0= np.pi*res[0]['intensity0']*res[0]['spread_x0']**2/(res[0]['b0']-1)
      photometry1= np.pi*res[0]['intensity1']*res[0]['spread_x1']**2/(res[0]['b1']-1)
   if "hole" in fit_type : photometry-= np.pi*res[0]['intensity_hole']*res[0]['spread_x_hole']*res[0]['spread_y_hole']

   res[0]['center_x'],res[0]['center_y']=my_center[0],my_center[1] # to draw
   res[0]["photometry0"],res[0]["photometry1"]=photometry0,photometry1
   res[0]["my_photometry0"],res[0]["my_photometry1"]= res[0]["photometry0"],res[0]["photometry1"]


   if W.verbose>3 : print "Binary FiT, supposed parameters : ", SuposedParams  
   if W.verbose>3 : print  "fit_type is : " ,fit_type
   if W.verbose>3 : print "anisoplanetism="+ str(bool(SuposedParams["aniso"])),"same_psf="+str(bool(SuposedParams["same_psf"]))
   return res 
 





def BinaryPSF2(grid,dictionary,search=False): # slowlyer 

   ##########
   ## DEFINE VARS 
   star0= dictionary['star1']
   star1= dictionary['star2']
   fit_type= dictionary['fit_type']

   try : phot_type = dictionary["phot_type"]
   except : 
     phot_type = 'fit'
     if W.verbose >0 : print "Warining not phot_type, setted to fit (from imageFunction)"  
   try : noise_type = dictionary["noise_type"]
   except : 
     noise_type = 'fit'
     if W.verbose >0 : print "Warining not noise_type, setted to fit (from imageFunction)"  



   ###########
   #  Make a first guess  
   max0 = star0 
   max1 = star1
  
   star_distance = np.sqrt(   (max0[0]-max1[0])**2 + (max0[1]-max1[1])**2  ) # distance between two pooints 
   my_center = [(max0[0]+max1[0])/2 , (max0[1]+max1[1])/2 ]
   dist0 = min( FWHM(grid,max0) , star_distance /2  )
   dist1 = min( FWHM(grid,max1) , star_distance /2  ) 

   ###########
   # make the bounds 
   bd_x0 = (max0[0] - star_distance/2, max0[0] + star_distance/2    ) 
   bd_y0 = (max0[1] - star_distance/2, max0[1] + star_distance/2    ) 

   bd_x1 = (max1[0] - star_distance/2, max1[0] + star_distance/2    ) 
   bd_y1 = (max1[1] - star_distance/2, max1[1] + star_distance/2    ) 
   
   ########
   # DEFINE fitting space 
   fit_range = star_distance + 5 * max(dist0,dist1) # range of the fit 
       # the error
   rx1,rx2=  int(my_center[0] - fit_range/2) ,  int(my_center[0] + fit_range/2)
   ry1,ry2 = int(my_center[1] - fit_range/2) ,  int(my_center[1] + fit_range/2)
   if W.verbose>3:
         print "----->IF.BinaryPSF :"
         print "The fit is done between points ", (rx1,ry1)," and ", (rx2,ry2) 
         print  "with fit", fit_type 
   X,Y=np.arange(int(rx1),int(rx2)+1),np.arange(int(ry1),int(ry2)+1)
   y,x = np.meshgrid(Y,X) 
   IX=grid[rx1:rx2+1,ry1:ry2+1]
   IX,mIX=FindBadPixel(IX)#,r=r)
   eIX = (IX-mIX).std() 
   eIX *= np.ones(IX.shape)

   ###################
   ## Supposed params and bounds #
   ###################
   SuposedParams={'x0':max0[0],'x1':max1[0],'y0':max0[1],'y1':max1[1],
	'spread_x0':0.83*(dist0),'spread_x1':0.83*dist1,                  
	'spread_y0':0.83*(dist0),'spread_y1':0.83*dist1,                  
	'intensity0':grid[max0[0]][max0[1]],'intensity1':grid[max1[0]][max1[1]],
	'background':0, "theta":1  }

   James={'x0':bd_x0,'x1':bd_x1,'y0':bd_y0,'y1':bd_y1,
	'spread_x0':(-0.1,None) ,'spread_x1':(-0.1,None),                  
	'spread_y0':(-0.1,None),  'spread_y1':(-0.1,None) ,                  
	'intensity0':(-0.1,None) ,'intensity1':(-0.1,None) ,
	'background':(0,None) , "theta":(-0.1,3.24) } # becasue James Bound hahahah, These are the fitting limits of the varaibles . WARNING    we put the intensity positive becasue in a binary fit situation you know.... who knows 
				    
   doNotFit = []
   dic_for_fit = {"same_psf": dictionary["same_psf"],"aniso":0}
   if "2D" in fit_type : dic_for_fit["aniso"]=1

   if dictionary['same_psf']:  
      doNotFit.append("spread_x1") 
      doNotFit.append("spread_y1") 
      if not "2D" in fit_type :
        doNotFit.append("spread_x1") 
   else : # not same psf  
      if not "2D" in fit_type : 
        doNotFit.append("spread_y0") 
	doNotFit.append("spread_y1") 


   ##########
   # PRINT 
   if W.verbose>3 : print "Binary FiT, supposed parameters : ", SuposedParams  
   if W.verbose>3 : print  "fit_type is : " ,fit_type
   if W.verbose>3 : print "anisoplanetism="+ str(bool(dic_for_fit["aniso"])),"same_psf="+str(bool(dic_for_fit["same_psf"]))


   ########################
   ## FIT TYPE and FIT 
   if "Bessel" in fit_type : 
      if W.verbose > 0  : print "WARNING : no bessel 2pt fit type now,fit type is set to gaussian"
      fit_type="Gaussian"

   else : # including not a bessel fit     # 0.83 = sqrt(ln(2)) 
      if "Gaussian" in fit_type  : # Gaussian != psf
	 res = FF.leastsqFit(BF.Gaussian2pt,(x,y),SuposedParams,
		IX,err=eIX,doNotFit=doNotFit,dic=dic_for_fit,bounds=James ) 

      elif "Moffat" in fit_type : 
         SuposedParams['b0'],SuposedParams['b1']=1.8,1.8
	 James['b0']=(1,6) ; James['b1']=(1,6)  
	 if dictionary["same_psf"] : doNotFit.append("b1") 

	 res = FF.leastsqFit(BF.Moffat2pt,(x,y),SuposedParams,
	      IX,err=eIX,doNotFit=doNotFit,dic=dic_for_fit,bounds=James) 
                           		



   res[0]["fit_dic"]= res[0]			  


		 
   # PHOTOMETRY, BACKGROUND
   if "Gaussian" in fit_type :
     if "2D" in fit_type :
      photometry0= np.pi*res[0]['intensity0']*res[0]['spread_x0']*res[0]['spread_y0']
      photometry1= np.pi*res[0]['intensity1']*res[0]['spread_x1']*res[0]['spread_y1']
     else : 
      photometry0= np.pi*res[0]['intensity0']*res[0]['spread_x0']**2
      photometry1= np.pi*res[0]['intensity1']*res[0]['spread_x1']**2
   if "Moffat" in fit_type :
     if "2D" in fit_type : 
      photometry0= np.pi*res[0]['intensity0']*res[0]['spread_x0']*res[0]['spread_y0']/(res[0]['b0']-1)
      photometry1= np.pi*res[0]['intensity1']*res[0]['spread_x1']*res[0]['spread_y1']/(res[0]['b1']-1)
     else : 
      photometry0= np.pi*res[0]['intensity0']*res[0]['spread_x0']**2/(res[0]['b0']-1)
      photometry1= np.pi*res[0]['intensity1']*res[0]['spread_x1']**2/(res[0]['b1']-1)
   if "hole" in fit_type : photometry-= np.pi*res[0]['intensity_hole']*res[0]['spread_x_hole']*res[0]['spread_y_hole']

   res[0]['center_x'],res[0]['center_y']=my_center[0],my_center[1] # to draw
   res[0]["photometry0"],res[0]["photometry1"]=photometry0,photometry1
   res[0]["my_photometry0"],res[0]["my_photometry1"]= res[0]["photometry0"],res[0]["photometry1"]


   if W.verbose >3 : print "Binary res :", res
   return res 
 



def EightRectangleNoise(grid,r,return_rectangle=0,dictionary={'size':4,'distance':1.5}):
  # We Derive the noise from eight rectangle (of R/2 ) around the 99% Energy
  # size =4 means that we devide by  4 the size of the rectangle 
  # distance = 2 means we go father by a factor 2 for star center (r center)
  # we suppose order in r 
  rx1,rx2,ry1,ry2 = r
  distance,size =  dictionary['distance'],dictionary['size']
  rx1,rx2 = rx1 - distance*(rx2-rx1)/2,  rx2 + distance*(rx2-rx1)/2
  ry1,ry2 = ry1 - distance*(ry2-ry1)/2,  ry2 + distance*(ry2-ry1)/2  
  p=[]
  rx,ry,background,rms=(rx2-rx1)/2/distance/size,(ry2-ry1)/2/distance/size,[],[]  # we search the noise   
  for i in ['NW','N','NE','E','SE','S','SW','W']:
	if i == 'NW': (ax1,ax2,ay1,ay2)= (rx1-rx,rx1,ry2,ry2+ry)  #we define 8 boxes of noise
	if i == 'N':  (ax1,ax2,ay1,ay2)= ((rx1+rx2)/2-rx/2,(rx1+rx2)/2+rx/2,ry2,ry2+ry)  
	if i == 'NE': (ax1,ax2,ay1,ay2)= (rx2,rx2+rx,ry2,ry2+ry)
	if i == 'E':  (ax1,ax2,ay1,ay2)= (rx2,rx2+rx,(ry1+ry2)/2-ry/2,(ry1+ry2)/2+ry/2)	
	if i == 'SE': (ax1,ax2,ay1,ay2)= (rx2,rx2+rx,ry1-ry,ry1)
	if i == 'S':  (ax1,ax2,ay1,ay2)= ((rx1+rx2)/2-rx/2,(rx1+rx2)/2+rx/2,ry1-ry,ry1)	
	if i == 'SW': (ax1,ax2,ay1,ay2)= (rx1-rx,rx1,ry1-ry,ry1)
	if i == 'W':  (ax1,ax2,ay1,ay2)= (rx1-rx,rx1,(ry1+ry2)/2-ry/2,(ry1+ry2)/2+ry/2)
	tmp=Stat.RectanglePhot(grid,(ax1,ax2,ay1,ay2),dic={"get":["number_count","sum","rms"]})
	background.append((tmp["sum"]/tmp["number_count"]))   #rectangle phot return the sum and the number_count
	rms.append(tmp["rms"])
	if return_rectangle : # we draw the rectangles
	    center,width,height = (  ((ax1+ax2)/2,(ay1+ay2)/2), (ax2-ax1),(ay2-ay1) )
	    p.append( (center, width, height) )
  background=np.median(background)	
  rms=np.median(rms)	
  if W.verbose>3 : print '----->8rectsbackground', background
  if return_rectangle :return background, 'uselesse', p  
  return {'background':background, 'rms':rms}    #except : print "star center of the image"


  
def FindBadPixel(grid,r=None,method=('median',3,2),ordered=False):  # We compare with the median filter.
  # In the method we define in arg1 the number of pixel to include in the median 
  # and in arg2, the max differnce between true image and median
  # the bad pixels can be noise or warm pixel
  if r==None: 
     IX=grid
  else:
     if ordered ==False:  rx1,rx2,ry1,ry2 = Order4(r)      
     else :(rx1,rx2,ry1,ry2) = r
     IX=grid[rx1:rx2+1,ry1:ry2+1]
  res,mIX = IX,IX   
  if method[0] =='median':
    mIX =  scipy.ndimage.median_filter(IX, size=(method[1],method[1]) )
    res[np.abs(IX-mIX)>(method[2]-1)*mIX] = mIX[np.abs(IX-mIX)>(method[2]-1)*mIX]
       #that you Antoine for showing how to get the median value when we differ to much from it. 
  return res,mIX


def InBorder(grid,r): # to check if r is in the grid 
    rx1,rx2,ry1,ry2 = Order4(r)
    if rx1<0                  :  rx1 =0
    if rx1>len(grid)-1        :  rx1 =len(grid)-1
    if ry1<0                  :  ry1 =0
    if ry1>len(grid[rx1])-1   :  rx1 =len(grid[rx1]-1)
    return (rx1,rx2,ry1,ry2) 



               #################
	       ## PROFILE OF A LINE (Cuting ) 
	       #########################


def RadialLine(grid,(point1,point2),return_point=0):  
  # we get profile around a line, return 2 vectors
  (x1,y1),(x2,y2) = point1,point2
  vect_r = ((x2-x1),(y2-y1))
  lenght = np.sqrt(vect_r[1]**2+vect_r[0]**2) #of the line
  (xmin,xmax),(ymin,ymax) = Order2((x1,x2)),Order2((y1,y2)) # the extreme points of the line
  x,y = np.arange(int(xmin-1),int(xmax+1)) , np.arange(int(ymin-1),int(ymax+1))  #should put int otherwise mismatch with array
  Y,X= np.meshgrid(y,x)
  array = grid[int(xmin-1):int(xmax+1),int(ymin-1):int(ymax+1)]  
  R =  ( (X-x1)*(x2-x1)+(Y-y1)*(y2-y1) )/lenght   
              # the distance of (X,Y) to x1,y1 projected on the line
  d = ( R*(x2-x1)/lenght-(X-x1) )**2 + (R*(y2-y1)/lenght-(Y-y1))**2    
              # the square distance of the point from the line
  R,d,array = R.flatten(),d.flatten(),array.flatten()  
  X,Y = X.flatten(),Y.flatten()
  ab,od= np.zeros(len(array)) ,np.zeros(len(array))
  ab[d<0.25] = R[d<0.25]   # ab like abscisse
  od[d<0.25] = array[d<0.25]
  X,Y = X[d<0.25],Y[d<0.25]
      #good idea also :  od = [od for (Y,od) in sorted(zip(Y,od))] 
  ab=ab[od.nonzero()]  # why do we have so many zero ? 
  od=od[od.nonzero()]  # think, but it works
  res = zip(ab,od)
  res.sort()
  res = np.array(res)
  #res[np.abs(IX-mIX)>(method[2]-1)*mIX] = mIX[np.abs(IX-mIX)>(method[2]-1)*mIX]
  if return_point : 
    X,Y = X[od.nonzero()],Y[od.nonzero()]
    res2 = zip(ab,X,Y)
    res2.sort()
    res2 = np.array(res2)
    return res[:,0],res[:,1],(res2[:,1].astype("int"),res2[:,2].astype("int") )   # abscice ordonate, points in array 
  else : 
    return res[:,0],res[:,1]  # abscice ordonate


def XProfile(grid,center,r=None,direction='X'):  #we supose that r is ordere for the display og the strahl funciton
  if r == None : r =[center[0]-15,center[0]+15,center[1]-15,center[1]+15]	                                           #  RETURN  x,y
  Order4(r) 
  if direction=='X':
      x=np.arange(int(r[0]),int(r[1])+1)
      y=grid[ int(r[0]):int(r[1])+1,int(center[1]) ]
  return x,y	


def RadialCloud(grid,center,radius,direction='None'):
  x0,y0 =center
  rx1,rx2,ry1,ry2 = int(x0-radius),int(x0+radius+1),int(y0-radius),int(y0+radius+1)
  x,y = [],[]
  for i in range(rx1,rx2): 
    for j in range(ry1,ry2):
      x.append,y.append= np.sqrt( (x0-i)**2+(y0-i)**2 ), grid[i][j]
  return x,y




    
#take care it will take the image and its end
def FindNStars(grid,N,binfact=3,separation=30): # N number of stars. BINFACT, the size (diameter) of the "psf"
                                                # SEPARATION, the minimum separation betwenn two stars. 
  #we just bin the image and give the N maximums, there can be an error (order of binfact pixels
  #        => yo1Gu need to use PixelMax and SeeingFit then. 
  fattable = Bin(grid,binfact)
  res= np.zeros((N,3))
  for i in range (len(fattable)): 
    for j in range (len(fattable[i])):
      tmp=0
      IsFar = True
      for k in range(N):
	IsFar &= ( (i-res[k][0])**2 + (j-res[k][1])**2 < separation   )   #here you see the separation 
      while( (fattable[i][j]>res[N-tmp-1][2]) & (tmp<N) ):
	tmp+=1
      try : 
        res[N-tmp-1][0]=res[N-tmp][0]
        res[N-tmp-1][1]=res[N-tmp][1]
        res[N-tmp-1][2]=res[N-tmp][2]
      except:()
      try:
        res[N-tmp][0]=i*binfact
        res[N-tmp][1]=j*binfact 
        res[N-tmp][2]=fattable[i][j]
      except:()
  return res
  

def ThetaProfile(grid,center,radius,theta):  # We take the profile in theta direction. 
  return  




                ##################
		## DIRECT INTERACT WITH EVENT 
		##################

def EllipticalAperture(grid,dic={},interp=False,full_answer=False): # photomtery, return bol or dic 
  """return bollean (of  been inside the aperture ) 
  or if we interpolate, return directly some values (phot, rms, number_count, fractional 
  interp is dividing each pixel by 10*10 pixelsn seems enought to me 
     dic : center_x, center_y , ru,rv, theta 
          ru , rv in pixels
         centers in pixels from the begining of the array x = row, y = column 
  if full answer return dic : number_count, sum, bol,bol2, interp_grid,
  """
  if dic == {} : return 0*grid 

  x0,y0,ru,rv,theta = dic["center_x"],dic["center_y"],dic["ru"],dic["rv"],dic["theta"],
  cos = np.cos( theta ) 
  sin = np.sin( theta ) 

  a=(  (cos/ru)**2 + (sin/rv)**2 ) 
  b=(  (sin/ru)**2 + (cos/rv)**2 ) 
  c=(  np.sin( 2 *theta )  * ( 1./rv**2 - 1./ ru**2 ) )

  #print "ellipse abc : ",a,b,c
  x=np.arange(-x0,len(grid)-x0  ) # invert IDK why 
  y=np.arange(-y0,len(grid[0])-y0  ) 


  if not interp : 
    Y,X = np.meshgrid(y,x) #  need to be in this order , tested with event ellipser! 

    bol= a*X**2 + b*Y**2 + c*X*Y <1 
    if full_answer : 
       res  = Stat.Stat(grid[bol],get=["sum","number_count"])
       res["bol"] = bol 
       return res
    else : # no full_answer
       return {"bol":bol} 

  else : # including interpolate 
    binn = 0.1 
    yy=np.arange(-x0,len(grid)-x0,binn  ) 
    xx=np.arange(-y0,len(grid[0])-y0,binn  ) 
    XX,YY = np.meshgrid(yy,xx) # need to be in this order , tested 

    interp_fct = interpolate.interp2d(x,y,grid,kind="cubic")
    interp_grid = interp_fct(xx,yy) 
    bol2= a*XX**2 + b*YY**2 + c*XX*YY <1 

    stats = Stat.Stat(interp_grid[bol],get=["sum","number_count"])
    res = {"interp_grid":interp_grid,"bol2":bol2,"bol":bol}
    res["sum"]          =stats["sum"]*binn**2
    res["number_count"] = stats["number_count"] * binn**2
    return bol2,res 


def ContrastMap(grid,center,interp=True,xmin=1,xmax=50,step=2,dic={"theta":0,"ru":1,"rv":1},background=0):
  """ xmin,xmax in pixels the size to spread the aperture
  step float in pixels  is the step between two annulus (circular  apertures)
  center (2 floats) 
  dic I just use theta and rv/ru 
  an elliptical aperture could be implemented
  return x,y,dic 
  """
  in_dic = dic 

  x = np.arange(xmin,xmax,step) 
  y = []
  ell_dic = {"center_x": center[0],"center_y":center[1],"theta":in_dic["theta"]}
  ratio = in_dic["rv"]/ in_dic["ru"] 
 
  if W.verbose >3 : print "ContrastMap initiated " 
  for xi in x : 
     ell_dic.update({"ru":xi,"rv":ratio*xi})
     print "ell_dic", ell_dic  
     yi = EllipticalAperture(grid,dic=ell_dic,interp=False,full_answer=True) # photomtery, return bol or dic 
     #if xi < 2 : 
     #   yi = EllipticalAperture(grid,dic=ell_dic,interp=True ,full_answer=True) # photomtery, return bol or dic 
     #else : 
     #   yi = EllipticalAperture(grid,dic=ell_dic,interp=False,full_answer=True) # photomtery, return bol or dic 
     #print "sum number : ",      yi["sum"] , yi["number_count"]
     #yi = yi["sum"]/yi["number_count"] - background
     yi  = np.std( grid[ yi["bol"] ]  )
     yi = np.nan_to_num( yi ) 

     y.append(yi)
 
  y=np.array(y)#/W.strehl["intensity"] 
  
  tdic = {"logx":1,
          "logy":1,
          "title":"Contrast Map",
	  "xlabel":"Distance [Pixel]",
	  "ylabel":"Value [Normalised]",
	  }
  G.tmp_x=x
  G.tmp_y=y
  G.tmp_tdic=tdic 
  if W.verbose > 3 : print "Contrast Map :",x,y,tdic
  return  x,y,tdic




def GetMaxEllipse(grid,bol=None,dic={}): # we will get the max by a Iterative garvity center and then a cubic interpolation
  return 

def ContrastForDimitri(grid,step=2,center=(0,0),limit=30): 
  """the step is the size of the annulus , growing we will take, 
  the limit is the farther pixl we take 
  RETURN abscisse ordonate
  """


def ProfileEvent(obj) :# Called by Gui/EventArtist.py
   G.my_point2 = [obj.point2[0],obj.point2[1]] # not  invert, always in array coord, Event is inverting its x and y for me :)   
   G.my_point1 = [obj.point1[0],obj.point1[1]]
   import AnswerReturn as AR 
   AR.ProfileAnswer()


def AnnulusEventPhot(obj): # Called by Gui/Event...py  Event object  
     res= {}

     center_x = obj.x0  # from image to array but coord in array type 
     center_y = obj.y0
     theta    = obj.theta

     if obj.outter_u < obj.inner_u :  # put outter radius after inner
         tmp = obj.inner_u  
	 obj.inner_u = obj.outter_u 
	 obj.outter_u = tmp  


     # DEIFINE THE Bollean of being inside the elliptical aperture 
     ru    = obj.ru   ; rv    = obj.ru *obj.rapport   
     bol_e   = EllipticalAperture(obj.array,dic={"center_x":center_x,"center_y":center_y,"ru":ru,"rv":rv,"theta":theta} )["bol"] # ellipse , photomretry 
     
     ru, rv = obj.inner_u, obj.inner_u*obj.rapport
     bol_i   = EllipticalAperture(obj.array,dic={"center_x":center_x,"center_y":center_y,"ru":ru,"rv":rv,"theta":theta} )["bol"] # inner

     ru, rv = obj.outter_u, obj.outter_u*obj.rapport
     bol_o   = EllipticalAperture(obj.array,dic={"center_x":center_x,"center_y":center_y,"ru":ru,"rv":rv,"theta":theta} )["bol"]#outter  


     bol_a  = bol_o ^ ( bol_i)  # annulus  inside out but not inside in  
     phot,number_count = np.sum(obj.array[bol_e]), len(obj.array[bol_e]) 
     back,number_back  = np.sum(obj.array[bol_a]), len(obj.array[bol_a])  

     # PHOT and back 
     res["background_dic"] =Stat.Sky(obj.array[bol_a]) 
     res["my_background"] =res["background_dic"]["mean"]  
     res["phot"] =  np.sum(obj.array[bol_e]) 
     res["my_photometry"] = res["phot"] - len(obj.array[bol_e])*res["my_background"] # bite, remove bad pixels at least,  

    
     if W.verbose > 2 : print "phot1 :", res["phot"] 
     if W.verbose > 2 : print "phot2 :", res["my_photometry"] 
     if W.verbose > 2 : print "back :", res["my_background"] , "\n" 



#def Bin(image,binfact):
#  x,y=int(len(image)/binfact)+1,int(len(image[0])/binfact)+1
#  fattable = np.zeros((x,y))
#  #  fattable = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
#  for i in range (0,len(image)):
#    for j in range(0,len(image[i])): 
#      if image[i][j]<0: image[i][j]=0    
#      fattable[(i/binfact)][(j/binfact)]+=image[i][j]  
#  return fattable
##   print i,j,image[i][j],fattable[i/10][j/10],int(i/10),int(j/10)
#   ompute the sta
#    if image[i][j] > ma: 
#       ma,a,b = image[i][j],i,j  #+0*ma
#print fattable
#  archivo ='/home/tourneboeuf/Software/Python/Strehl/test/table.dat'
#  PrintTable(fattable,52,52)
# find a noise even in a little rectangle   
#get   a 3 point noise to substract  
#faire un tableau de fonction en log qui prend 1 float et le retourne a un fact pres











#>>> from a import *
#>>> if name == "Michael" and age == 15:
#...     print('Simple!')
#...
#Simple!

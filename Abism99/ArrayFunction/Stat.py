import numpy as np 
import scipy  # for median filter 


import WorkVariables as W # for verbose 


def Stat(grid,dic={},get=None): #hist for the histogram
  res={}
  if get != None : pass   # keep the get from input  
  elif dic.has_key("get"): get=dic["get"] 
  else : get = ["rms","median","mean","min","max","sum","number_count"]

  for i in get : 
    if len(grid) ==0 : res[i]=0
    elif i=="rms" : res[i]=np.std(grid)
    elif i=="number_count": 
       res["number_count"]= len( grid.flatten() ) 
    else :  # do np.i[grid] 
      method = getattr(np,i)
      res[i]=method(grid) 

    """number_count done by rectangle phot"""
    #elif i=="number_count" : 
    #  dim = len(grid.shape) -1 
    #  my_len = len(grid) 
    #  for tmp in range(dim) : my_len *= len(grid[tmp]) 
    #  res[i]=my_len
  return res


def Sky(grid,dic={}): # dic contains mean,rms, sigma(clipping), median, it is the input and output 
  """ return dic : same as stat, median, or mean id the sky """
  if not dic.has_key("mean") : # if first loop, no rejection yet
    dic_default={"rec":0,"max_rec":10,"error":0.1,"sigma":2.5} # Make a default input of dic the error is a fraction of the rms
    dic_default.update( dic ) ; dic =dic_default

    dic.update(  Stat(grid) ) 
    dic["rec"]+=1
    return Sky(grid,dic)

  else : # including we have a mean, we can do sigma (clipping) 
    if dic["rec"] > dic["max_rec"] : # maximum recursion 
      return dic 
    else : 
      rms_old=dic["rms"]
      bol1= abs(grid-dic["mean"])  <  abs(dic["sigma"] *dic["rms"])  
      grid1 = grid[bol1]
      dic.update( Stat(grid1) ) 
      
      bolt=  ( dic["rms"]  >  (1.-dic["error"])  * rms_old  ) # t like tmp  
      bolt=bolt&( dic["rms"]  < (1.+dic["error"]) *rms_old  ) # but it is error test
      if bolt :  
        return dic 
      else :
        dic["rec"]+=1
        return Sky(grid,dic)


def RectanglePhot(grid,r,dic={},get=[]):
          # 2D array,(rx1,rx2,ry1,ry2), it should be ordered 
     # exact is for the taking the percentage of the cutted pixel or not 
     # median is a median filter of 3 pixel square and 2 sigma clipping
     # in_border is examining if r is in the grid, otherwise, cannot calculate. 
  # DIC default 
  default_dic={'median_filter':(3,2),"exact":0,"get":["sum"]} 
  default_dic.update(dic) ; dic =default_dic 
  if get == [] : get = dic["get"]

  ###########
  # r  DEFAULT  
  if r==None: rx1,rx2,ry1,ry2 = 0,len(grid)-1,0,len(grid)
  else : rx1,rx2,ry1,ry2 = r[0],r[1],r[2],r[3] 
  if not dic["exact"]:
    cutted = grid[int(rx1):int(rx2+1),int(ry1):int(ry2+1)]  
    
  ##########
  # MEDIAN FILTER 
    med_size=dic["median_filter"]
    if med_size[0] != 0 :
       median = scipy.ndimage.median_filter(cutted, size=(med_size[0],med_size[0]) )
       cutted[np.abs(cutted-median)>(med_size[1]-1)*median] = median[np.abs(cutted-median)>(med_size[1]-1)*median]


  res = Stat(cutted,get=get)  
  res["number_count"]= (ry2-ry1)*(rx2-rx1)
  return res  



def ObjectDetection(grid,dic={}):
  """-sigma is the clip
     -background_box is the side of the background box 

  we first detect all objects higher than (local ?) sigma"""
  default_dic={"sigma":2.5,"background_box":10,"back_type":"global"}
  default_dic.update(dic) ; dic=default_dic
  res=grid

  
  # MEDIAN FILTER 
  median = scipy.ndimage.median_filter(res, size=(3,3)  )
  bol1   = (np.abs(res-median)  >   2*median )
  res[bol1] = median[bol1]

  # SKY call 
  sky= Sky(  res,  dic={"sigma":dic["sigma"]}  )  # stat is a dic of all keyword imaginable,
  bpm = 0*grid +1  # bpm = 0 where mask 

  # SIGMA CLIP
  bol1= np.abs(res-sky["median"])    >   dic["sigma"]  * sky["rms"]
  bpm[bol1] = 0
  bpm

  # BOX FROM FELIPE BARRIENTOS
  median = scipy.ndimage.median_filter(bpm, size=(10,10)  )
  bpm2 = 0*bpm + 1 
  bpm2[median > 0.08] = 0 

  #BOX 
  kernel = np.zeros( (10,10)  ) + 1
  conv = scipy.ndimage.convolve2d(bpm,kernel)
  
  return bpm2,median ,bpm,sky,conv

#    from matplotlib import pyplot as plt 
#    tmp= Stat.ObjectDetection(W.Im0)
#    print  tmp[3]                            
#    fig = plt.figure()
#    ax=fig.add_subplot(221)
#    plt.imshow(tmp[1],origin="lower")
#    ax=fig.add_subplot(222)
#    plt.imshow(tmp[0],origin="lower")
#    ax=fig.add_subplot(223)
#    plt.imshow(tmp[2],origin="lower")
#    ax=fig.add_subplot(223)
#    plt.imshow(tmp[3],origin="lower")
#    plt.colorbar()
#    plt.show()                                                      


   










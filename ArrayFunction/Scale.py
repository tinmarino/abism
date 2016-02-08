import numpy as np


import Stat
import WorkVariables as W # to know the stats




def MinMaxCut(grid,dic={}): # From a true value renge give min_cut and max_cut
  # CONFIGURE DEFAULT DIC
  default_dic = {"scale_cut_type":"sigma_clip","sigma_min":1,"sigma_max":5}
  default_dic.update(dic)
  dic = default_dic


  if dic["scale_cut_type"]=="None":
    min_cut,max_cut =np.min(grid), np.max(grid)


  elif dic["scale_cut_type"]=="percent":
    percent = dic["percent"]
    if dic.has_key("whole_image"):
      sort = W.sort
    else :
      sort =   grid.flatten()      # Sorted Flatten Image
      sort.sort()
    percent =(100. - percent)/100.   #get a little percentage
    min_cut=sort[  int(percent/2*len(sort))   ]
    max_cut=sort[  int( (1-percent/2)*len(sort))  ]


  elif dic["scale_cut_type"]=="sigma_clip":
    if not  dic.has_key("sigma_min"):
       dic["sigma_min"],dic["sigma_max"] = dic["sigma"], dic["sigma"]
    if not dic.has_key("median") :   # The stats isn't done yet
      if dic.has_key("whole_image") :
         dic.update( vars(W.imstat) )
      else :
         dic.update( Stat.Stat( grid ,dic=dic )  )

    mean,rms = dic["mean"],dic["rms"]
    s_min,s_max = dic["sigma_min"],dic["sigma_max"]

    min_cut,max_cut= mean - s_min*rms , mean + s_max*rms



  res={"min_cut":min_cut,"max_cut":max_cut}
  return res


def Rescale(grid,dic={}):  # transform 0-1 to 0-1 with a certain function.
  default_dic={"fct":"x"}
  default_dic.update(dic)
  dic = default_dic

  if not dic.has_key("min_cut"):
    dic["min_cut"],dic["max_cut"] = np.min(grid), np.max(grid)

  minc, maxc = dic["min_cut"],dic["max_cut"]
  grid = ( grid - minc ) / ( maxc - minc )
  exec ( "fct = lambda x : "+ dic["fct"] )
  grid = fct(grid)
  grid = grid * (maxc - minc) + minc

  return grid










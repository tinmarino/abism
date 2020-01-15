"""
    ImageFunction works on array to separe matematics and graphics
"""

import numpy as np
import scipy.ndimage # for the median filter
import scipy.interpolate # for LocalMax



import Stat
import BasicFunction as BF
import GuyVariables as G  # check variables
import WorkVariables as W # for verbose



def DoNotPassBorder(grid,point2d):
  """Ensure point is in image"""
  x= point2d[0]
  y= point2d[1]
  if x < 0: x = 0
  if x > grid.shape[0]: x = len(grid)
  if y < 0: y = 0
  if y > grid.shape[1]: y = len(grid)
  return (x, y) , ""


def Order2(a,b):
  if a>=b : return (b,a)
  else : return (a,b)

def Order4(r,grid = None):
  rx1,rx2,ry1,ry2 = r[0], r[1], r[2], r[3]
  if rx1>rx2:
    tmp=rx1
    rx1=rx2
    rx2=tmp
  if ry1>ry2:
    tmp=ry1
    ry1=ry2
    ry2=tmp
  if grid != None :
    rx1 = max(rx1,0)
    ry1 = max(ry1,0)
    rx2 = min(rx2,len(grid)-1 )
    ry2 = min(ry2,len(grid[0])-1)
  return (rx1,rx2,ry1,ry2)


def LocalMax2(grid,center=None,r=None, size=4): # size useless, old
    #CUT
    #center = (r[0]+r[1])/2, (r[2]+r[3])/2
    x0,y0 = int(center[0]) , int(center[1] )
    reindex = center[0]-2, center[1]-2
    x = np.arange(x0-2,x0+2)
    y = np.arange(y0-2,y0+2)
    xx = np.arange(reindex[0],center[0]+2,0.01)
    yy = np.arange(reindex[1],center[1]+2,0.01)
    grid = grid[  center[0]-2:center[0]+2 ,  center[1]-2:center[1]+2]

    # FILT
    mIX =  scipy.ndimage.uniform_filter(grid, size=(3,3) )
    bol1 = np.abs(grid-mIX)>mIX
    grid[bol1] = mIX[bol1]

    # INTERPOLATE
    grid = scipy.interpolate.interp2d(x,y,grid,kind="cubic")
    grid = grid(xx,yy)
    coord =  np.unravel_index(grid.argmax(), grid.shape)

    res =   float(coord[0])/100 +reindex[0], float(coord[1])/100 +reindex[1]  ,  grid[coord[0],coord[1]]
    if W.verbose > 3 : print(" LocalMax@ImageFunction.py : ", res)
    return res

def LocalMax(grid,center=None,size=10,r=None,type="interpolation"): # With bad pixel filter
    """ type = "gravity" # gravity center of the 3*3 box
               "interpolation" # interpolation of the 5*5
    """
    # INIT R
    if r==None : r= ( center[0]-size , center[0]+size+1 , center[1]-size , center[1]+size+1 )

    #CUT
    cut1 = grid[  r[0] :  r[1]  ,  r[2]  :    r[3]  ]

    # FILT BAd PIXELS
    mIX =  scipy.ndimage.uniform_filter(cut1, size=(3,3) )
    bol1 = np.abs(cut1-mIX)>mIX
    cut1[bol1] = mIX[bol1]

    # 1st MAX
    coord1 = np.unravel_index(cut1.argmax(), cut1.shape)
    coord1= (  coord1[0]+  r[0],  coord1[1] + r[2]     )
    if W.verbose > 3 : print("LocalMax coord", coord1 , r )


    # INTERPOLATE
    if type == "interpolation":
       xmin = int (max (0          ,coord1[0]-2   )  )
       xmax = int (min (coord1[0]+3, len(grid)    )  )
       ymin = int (max (0          ,coord1[1]-2   )  )
       ymax = int (min (coord1[1]+3, len(grid[0]) )  )
       x = np.arange(xmin,xmax)
       y = np.arange(ymin,ymax)
       cut2 = grid [xmin : xmax, ymin: ymax  ]
       if W.verbose >3 : print("LocalMax shapes:" ,x.shape, y.shape, cut2.shape, xmin, xmax, ymin, ymax)
       interp = scipy.interpolate.interp2d(x,y,cut2,kind="cubic")

       xx = np.arange(xmin, xmax,0.1 )
       yy = np.arange(ymin, ymax,0.1 )
       zz = interp(xx,yy)

       # 2nd Max
       coord2 =  np.unravel_index(zz.argmax(), zz.shape)
       if W.verbose >3 : print("coord, cut ", coord2, cut2 )
       res = xx[coord2[0]]  ,  yy[coord2[1]]  ,  zz[ coord2[0],coord2[1] ]

    # GRAVITY CENTER
    else : # including type == gravity
       xmin = max (0          ,coord1[0]-1)
       xmax = min (coord1[0]+2, len(cut1) )
       ymin = max (0          ,coord1[1]-1)
       ymax = min (coord1[1]+2, len(cut1[0]) )
       x = np.arange(xmin,xmax)
       y = np.arange(ymin,ymax )
       cut2 = cut1 [xmin : xmax, ymin: ymax  ]
       X,Y = np.meshgrid(x,y)
       norm = np.sum(cut2)
       coord2 = np.sum( X*cut1 ) /norm , np.sum ( Y *cut1 ) /norm
       if W.verbose >3 : print("coord1, cut ", coord2, cut2 )
       res = coord2[0]+r[0]  ,  coord2[1]+r[2]  ,  cut2[ coord2[0],coord2[1] ]





    #res =  grid[coord[0],coord[1]],( float(coord[0])/100 +reindex[0], float(coord[1])/100 +reindex[1])

    if W.verbose > 3 : print(" LocalMax@ImageFunction.py : ", res)
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

def FindMaxWithBin(*arg): #arg =  grid and r : 3*3 median filter
  grid = arg[0]
  if len(arg) == 1 : r = 0,len(grid) , 0, len(grid[0])
  else : r = arg[1]
  cutted  = grid[ r[0] : r[1] , r[2] : r[3] ]
  cutted  = scipy.ndimage.median_filter(cutted, size=(3,3) )
  coord = np.unravel_index(cutted.argmax(), cutted.shape)
  return coord[0]+r[0] , coord[1] + r[2]


def FindMaxWithIncreasingSquares(grid,center): # center is th ecenter click
  size_max=20
  return



def DecreasingGravityCenter(grid,r=None,binfact=2,radiusmin=4): # call with radius each time samller
  """ Get the ce nter of gravity with decreasing squares around the previous gravity center """

  G=GravityCenter(grid,r=r)
  rx1,rx2,ry1,ry2=r # need to do that to avoid error mess 'tuple' object do not support item assignment
  if (r[1]-r[0] > radiusmin):
    dist   = float((r[1]-r[0]))/2/binfact
    if W.verbose > 2 : print("DecreasingGravityCenter" ,"r",r )
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
   (x,y)=centermax     #center should be the max pixel.
   i,j=int(x),int(y)       # RETURN  float
   max2 = grid[i,j]/2
   if direction =='average':
      res=FWHM(grid,centermax,direction='x')
      res+=FWHM(grid,centermax,direction='-x')
      res+=FWHM(grid,centermax,direction='y')
      res+=FWHM(grid,centermax,direction='-y')
      res/=4
      return res +0.5
   else:
      while (grid[i][j]>max2):
         if W.verbose>3 : print('FWHM :i,j,I=',i,j,grid[i][j],direction)
         if direction=='x':i+=1
         if direction=='-x':i-=1
         if direction=='y':j+=1
         if direction=='z':j-=1
         if grid[i][j]>grid[int(x)][int(y)]/2 : break
      fwhm = np.sqrt( (j-y)**2+(i-x)**2 )*2
      if W.verbose >3 : print("FWHM2:",fwhm)
      return  fwhm


def PointIntensity(grid,point):  #point is the coord of the exact point you need to assess intensity from linear assuption of nearest pixels,  seems to be slow tooo
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


def PixelMax(grid,r=None):   # array.float , 2 float , 1 float     RETURN center, max (=2+1floats)
  if r ==None :  r = 0,len(grid) , 0, len(grid[0])
  cut1 = grid[r[0] : r[1] , r[2] : r[3] ]
  x,y = np.unravel_index(cut1.argmax(), cut1.shape)
  return (r[0]+x,r[2]+ y),cut1[x,y]


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
  if (grid[x-1][y] < grid[x][y]/10
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
   if 'pread_y' in params.has_key:
    r99u = 3.14 * params['spread_x']
    r99v = 3.14 * params['spread_y']
   else:
    r99u = 3.14 * params['spread_x']
    r99v = 3.14 * params['spread_x']

  ###############
  # MOFFAT
  if 'Moffat' in fit_type : #r99 = r90
    ""
    #r99u= params['spread_x'] * np.sqrt( (1-%)**(1/(1-params['exponent'])) -1 )
    ap = 5  # 5 times the spread, for aperture,
    if params["exponent"]< 1 :  ap = 10
    elif params["exponent"] > 3 :
         if params["exponent"] > 4 :
           if params["exponent"] > 10 :
             if False : pass
             else :  ap= 1.
           else : ap = 3.
         else : ap = 4.
    if '2D' in fit_type :  # r99 = r90
        r99u,r99v = params['spread_x'] * ap ,params['spread_y'] * ap
    else :
        r99v,r99u= params['spread_x'] * ap ,  params['spread_x'] * ap

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
  if 'theta' in params:
    r99x = r99u * abs(np.cos(params["theta"]))  + r99v *  abs(np.sin(params["theta"]) )
    r99y = r99u * abs(np.sin(params["theta"]))  + r99v *  abs(np.cos(params["theta"]) )
  else :
    r99x,r99y = r99u,r99v

  if W.verbose>3 : print("------>EnergyRadius(ImageFunction.py)->",(r99x,r99y)            )
  return (r99x,r99y),(r99u,r99v)






def FwhmFromFit(param,fit_type) : # and phot  all explicit  return fwhm_x, fwhm_y (0 or 1)
  """from spread and exponent and fit_type, that is explicit"""

  ##########"
  # GAUSSIAN
  if ('Gaussian' in fit_type):
    if not "2D" in fit_type :
       try :  param["spread_y_hole"]=param["spread_x_hole"]
       except : pass
    photometry= np.pi*param['intensity']*param['spread_x']*param['spread_y']
    if "hole" in fit_type : photometry-= np.pi*param['intensity_hole']*param['spread_x_hole']*param['spread_y_hole']
    fwhm_x=1.66510922*param['spread_x'] # 2 * sqrt( log(2) )
    fwhm_y=1.66510922*param['spread_y']


  ###########
  #### MOFFAT
  elif ("Moffat" in fit_type) :
    if not "2D" in fit_type :
         param["spread_y"] = param["spread_x"]
         param["theta"] = 99
    if param['exponent']>1:
         photometry= np.pi*param['intensity']*param['spread_x']*param["spread_y"] /   ( param['exponent']-1 )
    else : # fit diverges
         x = np.arange(int(param["center_x"]-50) ,int( param["center_x"]+50+1) )
         y = np.arange(int(param["center_y"]-50) ,int( param["center_y"]+50+1) )
         Y,X = np.meshgrid(x,y)
         cut = BF.Moffat2D((X,Y),param)
         photometry = np.sum(cut)


    fwhm_x =2* abs(param['spread_x'])* np.sqrt(  (0.5)**(-1/param['exponent'])-1)
    fwhm_y =2* abs(param['spread_y'])* np.sqrt(  (0.5)**(-1/param['exponent'])-1)


  ##########
  ## BESSEL
  elif ('Bessel1' in fit_type) :
    if not "2D" in fit_type :
         param["spread_y"] = param["spread_x"]

    photometry= 4 * np.pi* param['intensity']*param['spread_x']*param["spread_y"]
    fwhm_x = 2 * param['spread_x'] * 1.61
    fwhm_y = 2 * param['spread_y'] * 1.61


  elif fit_type =='None':
      photometry = 99
      fwhm_x,fwhm_y = 99,99




  return {"fwhm_x":fwhm_x,"fwhm_y":fwhm_y,"photometry_fit":photometry}





def EightRectangleNoise(grid,r,return_rectangle=0,dictionary={'size':4,'distance':1}):
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
        #tmp=Stat.RectanglePhot(grid,(ax1,ax2,ay1,ay2),dic={"get":["number_count","sum","rms"]})  # bad pixels
        #background.append((tmp["sum"]/tmp["number_count"]))   #rectangle phot return the sum and the number_count # bite bad pixel

        background.append(  np.mean(grid[ ax1 : ax2+1 , ay1 : ay2+1 ])  )
        if W.verbose >3 : print("One background :", background[-1] , '\n\n\n\n')
        rms.append(     np.std(grid[ ax1 : ax2+1 , ay1 : ay2+1 ])   )
        if return_rectangle : # we draw the rectangles
            center,width,height = (  ((ax1+ax2)/2,(ay1+ay2)/2), (ax2-ax1),(ay2-ay1) )
            p.append( (center, width, height) )
  background.sort()
  background=np.mean(background[2:6])
  rms=np.median(rms)
  if W.verbose>3 : print('----->8rectsbackground', background)
  if return_rectangle :return background, 'uselesse', p
  return {'background':background, 'rms':rms}



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


def RadialLine(grid, point1_and_point2,return_point=0):
  # we get profile around a line, return 2 vectors
  (x1,y1),(x2,y2) = point1_and_point2
  vect_r = ((x2-x1),(y2-y1))
  lenght = np.sqrt(vect_r[1]**2+vect_r[0]**2) #of the line
  (xmin,xmax),(ymin,ymax) = Order2(x1,x2),Order2(y1,y2) # the extreme points of the line
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
  res = sorted(zip(ab,od))
  res = np.array(res)
  #res[np.abs(IX-mIX)>(method[2]-1)*mIX] = mIX[np.abs(IX-mIX)>(method[2]-1)*mIX]
  if return_point :
    X,Y = X[od.nonzero()],Y[od.nonzero()]
    res2 = sorted(zip(ab,X,Y))
    res2.sort()
    res2 = np.array(res2)
    return res[:,0],res[:,1],(res2[:,1].astype("int"),res2[:,2].astype("int") )   # abscice ordonate, points in array
  else :
    return res[:,0],res[:,1]  # abscice ordonate


def XProfile(grid,center,r=None,direction='X'):  #we supose that r is ordere for the display og the strahl funciton
  if r == None : r = (0,len(grid)-1 ,   "useless","useless")
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

def EllipticalAperture(grid,dic={},interp=False,full_answer=False,xy_answer=True): # photomtery, return bol or dic
  """ rdic = ru rv theta x0 y0
  return a dic,
      dic[bol] = are you in aperture
      dic[coord_x] = X[bol]
      dic[coord_y] = are you in aperture
        SO you can fit grid[bol]  = Basicfct((x,y),params see in StrehlFunciton folder how I use it (written october 30 2013)

  or if we interpolate, return directly some values (phot, rms, number_count, fractional
  interp is dividing each pixel by 10*10 pixelsn seems enought to me
     dic : center_x, center_y , ru,rv, theta
          ru , rv in pixels
         centers in pixels from the begining of the array x = row, y = column
  if full answer return dic : number_count, sum, bol,bol2, interp_grid,
  """
  if dic == {} : return 0*grid
  res = {}

  x0,y0,ru,rv,theta = dic["center_x"],dic["center_y"],dic["ru"],dic["rv"],dic["theta"],
  cos = np.cos( theta )
  sin = np.sin( theta )

  a=(  (cos/ru)**2 + (sin/rv)**2 )
  b=(  (sin/ru)**2 + (cos/rv)**2 )
  c=(  np.sin( 2 *theta )  * ( 1./rv**2 - 1./ ru**2 ) )

  x=np.arange(-x0,len(grid)-x0  ) # invert IDK why
  y=np.arange(-y0,len(grid[0])-y0  )


  if not interp :
      Y,X = np.meshgrid(y,x) #  need to be in this order , tested with event ellipser!

      bol= a*X**2 + b*Y**2 + c*X*Y <1
      if full_answer :
         res.update( Stat.Stat(grid[bol],get=["sum","number_count","rms"]))
         res["bol"] = bol
         return res
      else : # no full_answer
         res["bol"] = bol
      if xy_answer :
         res["coord_x"] = X[bol]
         res["coord_y"] = Y[bol]


  else : # including interpolate
      binn = 0.1
      xx=np.arange(-x0,len(grid)-x0,binn  )
      yy=np.arange(-y0,len(grid[0])-y0,binn  )
      XX,YY = np.meshgrid(xx,yy) # need to be in this order , tested

      interp_fct = interpolate.interp2d(x,y,grid,kind="cubic")
      interp_grid = interp_fct(xx,yy)
      bol2= a*XX**2 + b*YY**2 + c*XX*YY <1

      stats = Stat.Stat(interp_grid[bol],get=["sum","number_count"])
      res = {"interp_grid":interp_grid,"bol2":bol2,"bol":bol}
      res["sum"]          =stats["sum"]*binn**2
      res["number_count"] = stats["number_count"] * binn**2

      if xy_answer :
         res["coord_x"] = X[bol]
         res["coord_y"] = Y[bol]

  ######
  # REturn X and y index of bol



  return res




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

  if W.verbose >3 : print("ContrastMap initiated " )
  for xi in x :
     ell_dic.update({"ru":xi,"rv":ratio*xi})
     yi = EllipticalAperture(grid,dic=ell_dic,interp=False,full_answer=True) # photomtery, return bol or dic
     #if xi < 2 :
     #   yi = EllipticalAperture(grid,dic=ell_dic,interp=True ,full_answer=True) # photomtery, return bol or dic
     #else :
     #   yi = EllipticalAperture(grid,dic=ell_dic,interp=False,full_answer=True) # photomtery, return bol or dic
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
  if W.verbose > 3 : print("Contrast Map :",x,y,tdic)
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
     res["my_photometry"] = res["phot"] - len(obj.array[bol_e])*res["my_background"] # todo , remove bad pixels at least,


     if W.verbose > 2 : print("phot1 :", res["phot"] )
     if W.verbose > 2 : print("phot2 :", res["my_photometry"] )
     if W.verbose > 2 : print("back :", res["my_background"] , "\n" )




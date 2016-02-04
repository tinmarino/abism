import scipy.optimize
import numpy as np

"""
IDEA: fit Y = F(X,A) where A is a dictionnary describing the
parameters of the function.

note that the items in the dictionnary should all be scalar!
"""

def polyN(x, params):
    """
    example of a function which parameters are defined by a
    dictionary: a polynomial function.

    In this particular case, params={'A0':1.0, 'A2':2.0} returns
    x->1+2*x**2. The coefficient do not have to start at 0 and do not
    need to be continuous. Actually, the way the function is written,
    it will accept any 'Ax' where x i a float.
    """
    res = 0
    for k in params:
        res += params[k]*np.array(x)**float(k[1:])
    return res

def radial2dgrid(radius,sample,center=[0,0]):

    x = np.linspace(-radius,radius,sample)+center[1]
    y = np.linspace(-radius,radius,sample)+center[0]
    xi1 = np.tile(x,sample)
    xx = xi1.reshape(sample,sample)
    yi1 = np.repeat(y,sample)
    yy = yi1.reshape(sample,sample)
    radgrid = np.sqrt(xx**2+yy**2)
    return xi1,yi1,radgrid



    
def fitFunc(pfit, pfitKeys, x, y, err=None, func=None,
            pfix=None, verbose=False,dic=None):
    """
    interface to leastsq from scipy:
    - x,y,err are the data
    - pfit is a list of the paramters
    - pfitsKeys are the keys to build the dict
    pfit and pfix (optional) and combines the two
    in 'A', in order to call F(X,A)
    """
    if dic != None : 
       func = lambda x,param : func(x,param,dic=dic) 
    params = {}
    # build dic from parameters to fit and their values:
    for i,k in enumerate(pfitKeys):
        params[k]=pfit[i]
    # complete with the non fitted parameters:
    for k in pfix:
        params[k]=pfix[k]
    if err is None:
        err = np.ones(np.array(y).shape)
    # return residuals
    try:
        # assumes y is a numpy array
        y = np.array(y)
        res= ((func(x,params)-y)/err).flatten()
    except:
        # much slower: this time assumes y (and the result from func) is
        # a list of stuff, each convertible in np.array
        res = []
        tmp = func(x,params)
        for k in range(len(y)):
            df = (np.array(tmp[k])-np.array(y[k]))/np.array(err[k])
            try:
                res.extend(list(df))
            except:
                res.append(df)
        res= np.array(res)
        
    if verbose:
        print 'CHI2:', (res**2).sum()/float(reduce(lambda x,y: x+y,
                    [1 if np.isscalar(i) else len(i) for i in y])-len(pfit)+1)
    return res
        
def leastsqFit(func, x, params, y, err=None, fitOnly=None,bounds=None, 
               verbose=0, doNotFit=[], epsfcn=1e-7,
               ftol=1e-4, fullOuput=True,dic=None):
    """
    returns bestparam, uncertainties, chi2_reduced, func(x, bestparam), dic{covariance matrix...} 
    - params is a Dict containing the first guess.

    - fits 'y +- err = func(x,params)'. errors are optionnal.

    - fitOnly is a LIST of keywords to fit. By default, it fits all
      parameters in 'params'. Alternatively, one can give a list of
      parameters not to be fitted, as 'doNotFit='

    - bounds is a DICTIONARy of the bounds for the fitting staff  like {"theta":(-01,3.24),"spread":(0,None) } 

    - dic is a stupid dic, to pass to the function, need to be optional 

    - doNotFit has a similar purpose: for example if params={'a0':,
      'a1': 'b1':, 'b2':}, doNotFit=['a'] will result in fitting only
    the 'b1' and 'b2'. WARNING: if you name parameter 'A' and another one 'AA',
    you cannot use doNotFit to exclude only 'A' since 'AA' will be excluded as
    well... 
    
    """
    fitFunc_dic = fitFunc
    if dic != None : 
       fit_Func_dic = lambda *arg : fitFunc(*arg,dic=dic) 
    verb=0
    if verbose>3 : verb=1
    # fit all parameters by default
    if fitOnly is None:
        if len(doNotFit)>0:
            fitOnly = filter(lambda x: x not in doNotFit, params.keys())
        else:
            fitOnly = params.keys()

    # build fitted parameters vector:
    pfit = [params[k] for k in fitOnly]

    # built fixed parameters dict:
    pfix = {}
    for k in params.keys():
        if k not in fitOnly:
            pfix[k]=params[k]

    if verb:
        print '---> leastsqFit@FitFunction FITTED parameters:', fitOnly
        
    pfix_mem = pfix
    rec_bounds = bounds
    bounds_to_fit=[[None,None]]*len(fitOnly) # now it is a list 
    """the Old one""" 
    if False :  # False to get the good one with limits
       plsq, cov, info, mesg, ier = \
              scipy.optimize.leastsq(fitFunc_dic, pfit,
                    args=(fitOnly,x,y,err,func,pfix, verb),
                    full_output=True, epsfcn=epsfcn, ftol=ftol)

        ###
	## WITH THE BOUNDARIES 
	###"

    else  : # BOUNDARIES  
       """ with boundaries for theta"""
       from leastsqbound import leastsqbound
       if "theta" in fitOnly :  
            bounds_to_fit[fitOnly.index("theta")] = (-0.1,3.24) 
       if "theta_hole" in fitOnly :  
            bounds_to_fit[fitOnly.index("theta_hole")] = (-0.1,3.24) 
       if "spread" in fitOnly :  
            bounds_to_fit[fitOnly.index("spread")] = (-0.1,None) 
       if "spread_x" in fitOnly :  
            bounds_to_fit[fitOnly.index("spread_x")] = (-0.1,None) 
       if "spread_y" in fitOnly :  
            bounds_to_fit[fitOnly.index("spread_x")] = (-0.1,None) 
       if "spread_x_hole" in fitOnly :  
            bounds_to_fit[fitOnly.index("spread_x_hole")] = (-0.1,None) 
       if "spread_y_hole" in fitOnly :  
            bounds_to_fit[fitOnly.index("spread_y_hole")] = (-0.1,None) 
       if rec_bounds != None : 
         for key in rec_bounds.keys() :
	    if key in fitOnly : # becauser could be in notToFit
               bounds_to_fit[fitOnly.index(key)] = rec_bounds[key]

    ################	
    # ACTUAL FIT 
       plsq, cov, info, mesg, ier = \
                       leastsqbound(fitFunc_dic, pfit, bounds=bounds_to_fit,
                       args=(fitOnly,x,y,err,func,pfix, verb),
                       full_output=True, epsfcn=epsfcn, ftol=ftol)
    
    # best fit -> agregate to pfix
    for i,k in enumerate(fitOnly):
        pfix[k] = plsq[i]

    # reduced chi2
    model = func(x,pfix)
    chi2 = (np.array(fitFunc_dic(plsq, fitOnly, x, y, err, func, pfix))**2).sum()
    reducedChi2 = chi2/float(reduce(lambda x,y: x+y,
                  [1 if np.isscalar(i) else len(i) for i in y])-len(pfit)+1)

    # uncertainties:
    uncer = {}
    for k in pfix.keys():
        if not k in fitOnly:
            uncer[k]=0 # not fitted, uncertatinties to 0
        else:
            i = fitOnly.index(k)
            if cov is None:
                uncer[k]=-1
            else:
                uncer[k]= np.sqrt(np.abs(np.diag(cov)[i]*reducedChi2))

    if verb:
        print '-'*20
        print 'REDUCED CHI2=', reducedChi2
        tmp = pfix.keys(); tmp.sort()
        for k in tmp:
            print k, '=', pfix[k],
            if uncer[k]!=0:
                print '+/-', uncer[k]
            else:
                print ''
    # result:
    return pfix, uncer, chi2, model ,  {"cov":cov,"plsq":plsq,"pfit":pfit,"fitOnly":fitOnly,"bounds":bounds} 








         ##############
	 #   END      #
	 ##############

def sin(x,params):
    res= np.sin(x)  +params["K"]
    return res 
def sinusoid(x,params):
    res = params['C']+params['V']*np.sin(x+params['phi'])
    return res
def gaussian(x,params):
    res = params['C']+params['A']*np.exp(-(x-params['x0'])**2/params['sigma']**2)
    return res
def bessel1(x,params) :
    from scipy.special import jn    
    x-=params['x0']
    res = params['C']+params['A']* (2*jn(1,x/params['sigma'])*params['sigma']/x)**2
    return res
def tanhip(x,params): 
  res= params['A']*np.tanh(params['B']*x)+params['C']
  return res

    #xt = x[0:x.shape[0]/2]
    #yt = x[x.shape[0]/2:]
    ## le yt+params vient du fait que l'affichage y va du haut vers le bas    
    #xp = (xt-params['x0'])*np.cos(params['theta'])-(yt+params['y0'])*np.sin(params['theta'])
    #yp = (xt-params['x0'])*np.sin(params['theta'])+(yt+params['y0'])*np.cos(params['theta'])
    #res = params['C']+params['A']*np.exp(-(xp**2/params['sigmax']**2+yp**2/params['sigmay']**2))
    #return res
def example():
    """
    very simple example
    """
    X = [ 0,   1,   2,   3  ]
    Y = [-0.1, 1.1, 4.1, 8.9]
    E = [ 0.1, 0.1, 0.1, 0.1]
    #best, unc, chi2, model =\
    #      leastsqFit(polyN, X, 
    #                 {'A0':0., 'A1':0.,'A2':0.1},
    #                 Y, err=E, fitOnly=['A2', 'A0'])
    best, unc, chi2, model =\
          leastsqFit(polyN, X, 
                     {'A0':0., 'A1':0.,'A2':0.1},
                     Y, err=E, doNotFit=['A1'])
    print 'CHI2=', chi2
    for k in best.keys():
        print k, '=', best[k],
        if unc[k]>0:
            print '+/-', unc[k]
        else:
            print ''
    print 'Y=', Y
    print 'MODEL=', model
    return
def example2(): #sinuzoide
    """ sinusoide """
    sample = 100
    x = np.linspace(0,2*np.pi,sample)
    params = {'C':0.2,'V':0.3,'phi':0.5*np.pi}
    y = sinusoid(x,params)+np.random.random(sample)*0.1-0.5
    erry = np.ones(sample)*0.05
    best, unc, chi2, model =leastsqFit(sinusoid,x,{'C':0.1,'V':0.2,'phi':0.1*np.pi},y, err=erry,verbose=True)
    plt.figure(1)
    ax1 = plt.subplot(111)
    ax1.plot(x,y)
    ax1.plot(x,model)
    for k in best.keys():
        print k, '=', best[k],
        if unc[k]>0:
            print '+/-', unc[k]
        else:
            print ''

def example3(): # gaussian+ strehl
    """ gaussian + strehl"""
    sample = 40
    x = np.linspace(-2,2,sample)
    step=0.08
    params = {'C':0,'A':1,'x0':0,'sigma':0.27}
    y = bessel1(x,params)+0.1*np.random.random(sample)
    erry = np.ones(sample)*0.05
    #best, unc, chi2, model =leastsqFit(gaussian,x,{'C':0.2,'A':10.4,'x0':0.3,'sigma':0.7},y, err=erry,verbose=True)
    res =leastsqFit(bessel1,x,{'C':0,'A':0.6,'x0':0,'sigma':0.4},y, err=erry,verbose=True)
    plt.figure(1)
    from scipy.special import jn    
    Be = lambda x,B : (2*jn(1,x/B)*B/x)**2 /B**2 *res[0]['sigma']**2 
    ax1 = plt.subplot(121)
    ax1.bar(x,(y-res[0]['C'])/Be(0.001,0.2),step,color='pink')
    ax1.plot(x,(res[3]-res[0]['C'])/Be(0.001,0.2),color='black',linewidth=3)   
    plt.ylim(-0.2,1)
    plt.xlim(-1.5,1.5)
    ax2= plt.subplot(122)
    ax2.plot(x,Be(x,0.2)/Be(0.001,0.2))
    plt.xlim(-1.5,1.5)
    plt.ylim(-0.2,1)
    for k in res[0].keys():
        print k, '=', res[0][k],
        if res[1][k]>0:
            print '+/-', res[1][k]
        else:
            print ''
    return res[3]       

def example4():
    sample = 100 
    noiseamp = 0.5
    params = {'C':0.5,'A':5.5,'theta':0.67*np.pi,'x0':0.0,'y0':-2.0,'sigmax':2.0,'sigmay':1.0}
    paramsguess = {'C':0.3,'A':3.5,'theta':0.43*np.pi,'x0':-1.0,'y0':0.0,'sigmax':1.0,'sigmay':3.0}
    x,y,grid = radial2dgrid(5.0,sample)
    xconc = np.concatenate((x,y))
    print 'x',type(x),'y',type(y),'conc',type(xconc) 
    ima = gaussian2(xconc,params)+np.random.random(sample*sample)*noiseamp*params['A']
    errima = np.ones(sample*sample)*0.05
    fig1 = plt.figure(1)
    ax1 = plt.subplot(121)
    ax1.imshow(ima.reshape(sample,sample))
    # now the fitting 
    best, unc, chi2, model =leastsqFit(gaussian2,xconc,paramsguess,ima,err=errima,verbose=True) 
    print     best, unc, chi2, model
    ax2 = plt.subplot(122)
    ax2.imshow(model.reshape(sample,sample))
#example4()    

def example5():
    """ A*tanh(Bx)+C """
    sample = 100
    x = np.linspace(-2,2,sample)
    params = {'A':3,'B':10,'C':3}
    y = tanhip(x,params)+np.random.random(sample)
    erry = np.ones(sample)
    best, unc, chi2, model =leastsqFit(tanhip,x,{'A':3,'B':0.9,'C':3},y, err=erry,verbose=True)
    plt.figure(1)
    ax1 = plt.subplot(111)
    ax1.plot(x,y)
    ax1.plot(x,model)
    print best
    for k in best.keys():
        print k, '=', best[k],
        if unc[k]>0:
            print '+/-', unc[k]
        else:
            print ''
def example6():  # err= np.inf   test if err = 0 if it is like inf or like 0 
    x=np.arange(-2,2,0.1)
    y = np.sin(x)+1
    y[10:] = np.sin(x[10:]) 
    err = x*0 +1
    err[10:] = x[10:]*0 + np.inf 
    params = {"K":0}
    res= leastsqFit(sin,x,params,y, err=err,verbose=True)
    print res 
    return res

def degen(points,params):
  res = 0*points 
  res[points>0]= params["x1"] + (1-params["y1"])* points + (2-params["z1"])*points**2
  res[points<=0]= (3-params["x2"]) + (4-params["y2"])* points + (5-params["z2"])*points**2
  return res 


def example7(): # made for cov ?  it is reading the order in fitOnly  
  x=np.arange(-10,10,0.1)
  y= 0*x
  err = x*0 +1
  params = {"x1":1,"y1":1,"z1":1,"x2":1,"y2":1,"z2":1}
  res= leastsqFit(degen,x,params,y, err=err,verbose=True)

  keys = res[4]["fitOnly"]
  cov = res[4]["cov"]
  stg_head=","
  string=""
  for i in range(len(cov) ):
    stg_head+=keys[i] +","
    string+=keys[i] +","
    for j in range(i+1) :
      string += "%.3f"%( cov[i,j] /np.sqrt( cov[i,i] * cov[j,j] ) )+","
    string=string[:-1]+"\n" # remove last "," and pass line 

  stg_head=stg_head[:-1]+"\n"
  string = stg_head+string
  print string 
  #print res 
  #return res




def plot2dgaussian_old():
    import matplotlib.pyplot as plt
    import BasicFunction as BF
    sample = 50 
    params = {"background":10,"intensity":300,'theta':(np.pi/2),'center_x':2.0,'center_y':-2.0,'spread_x':5.0,'spread_y':1.0}
    x,y,grid = radial2dgrid(5.0,sample)
    points = np.meshgrid(x,y) 
    ima = BF.Gaussian2D(points,params)
    ima.reshape(50,50) 
    print type(ima), ima.shape 
    fig1 = plt.figure()
    ax1 = plt.subplot(111)
    ax1.imshow(ima) 
    #ax1.imshow(ima.reshape(sample,sample))
    plt.show() 


def example8() : # plot2dgaussian() and fit it, to check theta  ? leastsqbound is much better !!!
    import matplotlib.pyplot as plt
    import BasicFunction as BF

    ######
    # CREATE GAUSSIAN PSF 
    print globals()
    if not ("params" in globals()) : 
      params = {"background":10,"intensity":300,'theta':np.pi,'center_x':100,'center_y':100,'spread_x':50,'spread_y':60}
    X,Y=np.arange(0,512),np.arange(0,512)
    y,x = np.meshgrid(Y,X)                    # We have to inverse because of matrix way 
    ima = BF.Gaussian2D((x,y),globals()["params"])
    ima+= np.random.random(ima.shape) *5 
    print type(ima), ima.shape  , np.std(ima) 


    if not "ax" in globals() : 
      params = {"background":0,"intensity":100,'theta':1,'center_x':75,'center_y':100,'spread_x':100,'spread_y':100}
      err = ima**0.5
      res= leastsqFit(BF.Gaussian2D,(y,x),params,ima, err=err,verbose=9)
    
    if "ax" in globals():
      ax.imshow(ima) 

    else : 
      fig1 = plt.figure()
      ax1 = plt.subplot(121)
      ax1.imshow(ima) 
      ax1 = plt.subplot(122)
      ax1.imshow(res[3]) 
      #ax1.imshow(ima.reshape(sample,sample))
      plt.show() 
    return ima 

def call8():
  import matplotlib.pyplot as plt
  global ax , params 
  fig = plt.figure() 
  num=1
  for theta in [0,0.16,0.33,0.5,1,1.3,1.7,1.8,2]:
    params = {"background":0,"intensity":100,'theta':theta,'center_x':200,'center_y':300,'spread_x':25,'spread_y':60}
    ax = fig.add_subplot(3,3,num) 
    example8() 
    plt.xlabel(theta) 
    num+=1
  plt.show() 
  return 

def call8_2(): # for making fits image 
  import matplotlib.pyplot as plt
  import pyfits 
  global ax , params 
  fig = plt.figure() 
  num=1
  params = {"background":0,"intensity":100,'theta':30,'center_x':200,'center_y':300,'spread_x':25,'spread_y':60}
  ax = fig.add_subplot(1,1,1) 
  ima = example8() 
  hdu = pyfits.PrimaryHDU(ima)
  hdu.writeto('gaussian2D.fits',clobber=True) # overrighr
  
def MakeImage():
    import pyfits 
    import BasicFunction as BF
    X,Y=np.arange(0,512),np.arange(0,512)
    y,x = np.meshgrid(Y,X)                    # We have to inverse because of matrix way 
    res=0*x

    params = {"background":10,"intensity":300,'theta':np.pi,'center_x':64,'center_y':64,'spread_x':10,'spread_y':15}

    for center_x in [0,  50, 100, 150, 200, 250, 300, 350, 400, 450, 500 , 22, 35,57,293,382,239, 388,290,125,128]:
      params["center_x"]= center_x 
      ima = BF.Gaussian2D((x,y),params)
      res+=ima

    params = {"background":10,"intensity":300,'theta':np.pi,'center_x':-64,'center_y':192,'spread_x':10,'spread_y':15}

    for spread in [5,10,15,50]:
      params["center_x"]+=128
      params["spread_y"]= spread
      ima = BF.Gaussian2D((x,y),params)
      res+=ima
      
    params = {"background":10,"intensity":300,'theta':np.pi,'center_x':-64,'center_y':320,'spread_x':10,'spread_y':15}

    for theta in [0 , 1./6*np.pi , 1./3*np.pi , 1./2*np.pi]:
      params["center_x"]+=128
      params["theta"]=theta 
      ima = BF.Gaussian2D((x,y),params)
      res+=ima

    params = {"background":10,"intensity":300,'theta':np.pi,'center_x':-64,'center_y':448,'spread_x':10,'spread_y':40}

    for theta in [ 0, 1./6*np.pi  ,1./4*np.pi , 1/2.*np.pi ]:
      params["center_x"]+=128
      params["theta"]=theta 
      ima = BF.Gaussian2D((x,y),params)
      res+=ima

    res+= np.random.random(res.shape) *5 
    print type(res), res.shape  , np.std(res) 
    hdu = pyfits.PrimaryHDU(res)
    hdu.writeto('my_gaussians2D.fits',clobber=True) # overrighr
  
    return 


#MakeImage()


#call8_2() 






""" this module is imported from this web site : 
http://www.ster.kuleuven.be/~pieterd/python/html/plotting/interactive_colorbar.html
it aims to create a colorbar with some events and connecxions, 
if you have some troubles to digest that, just take some laxative"""

import pylab as plt
import numpy as np
from scipy.ndimage import gaussian_filter
import NormalizeMy

import MyGui as MG # to draw 

#import GuyVariables as G
try : import GuyVariables as G 
except : print "WARNING draggable colorbar.py could not load Gui>Variables" 

class DraggableColorbar(object):
    def __init__(self, cbar, mappable):
        self.cbar = cbar  # the colorbar 
        self.mappable = mappable # the imshow 
        self.press = None
	try : self.cycle = G.all_cmaps 
	except : 
           self.cycle = sorted([i for i in dir(plt.cm) if hasattr(getattr(plt.cm,i),'N')])
	# added by martin 
	self.old = {}
	self.stretch = "linear"



    def connect(self):
        """connect to all the events we need"""
        self.cidpress = self.cbar.patch.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.cbar.patch.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.cbar.patch.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)
        self.keypress = self.cbar.patch.figure.canvas.mpl_connect(
            'key_press_event', self.key_press)

    def on_press(self, event):
        """on button press we will see if the mouse is over us and store some data"""
        if event.inaxes != self.cbar.ax: return
        self.press = event.x, event.y

    def key_press(self, event):
        #if event.inaxes != self.cbar.ax: return
	
	self.old["cmap"] = (self.cbar.get_cmap().name) 
        index = self.cycle.index(self.old["cmap"]) # index and cycle are made cmap = cycle[index]
        if event.key=='down':
            index += 1
        elif event.key=='up':
            index -= 1
        if index<0:
            index = len(self.cycle)
        elif index>=len(self.cycle):
            index = 0
        cmap = self.cycle[index]

	MG.Draw(cmap=cmap)
        #self.mappable.get_axes().set_title(cmap)
	# for Abism, try to change color button, but just try because importation is not possible out of ABism   
	try : 
	  G.cu_color.set(cmap) 
	except : pass
	  #print "DraggableColorBar.py I changed color but not G.cu_color variable nevermind"


    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if self.press is None: return
        if event.inaxes != self.cbar.ax: return
	self.old["norm"] = self.cbar.norm
        xprev, yprev = self.press
        dx = event.x - xprev
        dy = event.y - yprev
        self.press = event.x,event.y
        #print 'x0=%f, xpress=%f, event.xdata=%f, dx=%f, x0+dx=%f'%(x0, xpress, event.xdata, dx, x0+dx)
        scale = self.cbar.norm.vmax - self.cbar.norm.vmin
        perc = 0.1  # initially 0.03
        if event.button==1:
            self.cbar.norm.vmin -= (perc*scale)*np.sign(dy)
            self.cbar.norm.vmax -= (perc*scale)*np.sign(dy)
        elif event.button==3:
            self.cbar.norm.vmin -= (perc*scale)*np.sign(dy)
            self.cbar.norm.vmax += (perc*scale)*np.sign(dy)
	MG.Draw(min=self.cbar.norm.vmin, max= self.cbar.norm.vmax) 



    def on_release(self, event):
        """on release we reset the press data"""
        self.press = None
        #MG.Draw(cbar=False) 


    def disconnect(self):
        """disconnect all the stored connection ids"""
        self.cbar.patch.figure.canvas.mpl_disconnect(self.cidpress)
        self.cbar.patch.figure.canvas.mpl_disconnect(self.cidrelease)
        self.cbar.patch.figure.canvas.mpl_disconnect(self.cidmotion)












def example():
  np.random.seed(1111)
  
  # Create empty image
  nx, ny = 256, 256
  image = np.zeros((ny, nx))
  
  # Set number of stars
  n = 10000
  
  # Generate random positions
  r = np.random.random(n) * nx
  theta = np.random.uniform(0., 2. * np.pi, n)
  
  # Generate random fluxes
  f = np.random.random(n) ** 2
  
  # Compute position
  x = nx / 2 + r * np.cos(theta)
  y = ny / 2 + r * np.sin(theta)
  
  # Add stars to image
  # ==> First for loop and if statement <==
  for i in range(n):
      if x[i] >= 0 and x[i] < nx and y[i] >= 0 and y[i] < ny:
          image[y[i], x[i]] += f[i]
  
  # Convolve with a gaussian
  image = gaussian_filter(image, 1)
  # Add noise
  image += np.random.normal(3., 0.01, image.shape)
  img = plt.imshow(image,cmap=plt.cm.spectral)
  cbar = plt.colorbar(format='%05.2f')
  cbar.set_norm(NormalizeMy.MyNormalize(vmin=image.min(),vmax=image.max(),stretch='linear'))
  cbar = DraggableColorbar(cbar,img)
  cbar.connect()
  
  plt.show()

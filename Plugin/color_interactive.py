from Tkinter import *
import colorsys
import numpy as np # for the np.arrange to load the ultimate row befora

try :
  import GuyVariables as G 
  import InitGui as IG
  imported = True
except : 
  print "Not in ABSIM, cannot load modules" 
  imported = False
  

# END OF IMPORTATIO


def Main() : 
  global H      ; H=0
  global nrow   ; nrow=20
  global ncol   ; ncol=20
  global tk 

  tk = Tk() 

  Constructor(tk) 
  print "ookokok"
  Loop(True) 

  print "ookokok"
  tk.mainloop() 


def Constructor(tk) : 
  """ Initiate the GUI """
  global w # to know where we are 
  tk.title("Chose HLS color") 

  l = Label(tk,text="L\nI\nG\nH\nT\nN\nE\nS\nS") 
  l.pack(side=LEFT,expand=0,fill=Y)
 
  # HUE
  sub_frame = Frame(tk)
  sub_frame.pack(side=BOTTOM,fill=X)

  l = Label(tk,text="SATURATION") 
  l.pack(side=BOTTOM,expand=0,fill=X)


  # fill sub_frame 
  w = Scale(sub_frame, from_=0, to=1,resolution=0.01,orient=HORIZONTAL,command = lambda tmp : Loop(False)  )
  w.pack(side=TOP,expand=1,fill=X)

  l = Label(sub_frame,text="HUE") 
  l.pack(side=TOP,expand=0,fill=X)


def Loop(init): 
  """init is a bol . do we init create the grid if we init 
  and just change color and command otherwise
  """
  global H 
  print "I loop", init 
  global MyButton
  if init : 
     sub_grid = Frame(tk) 
     sub_grid.pack(side=TOP,expand=TRUE,fill=BOTH) 
     MyButton = []
  else : 
     H=w.get()  
     print "lauch"

  for row in np.arange(nrow,-1,-1): 
    if init : button_col= []
    for col in np.arange(ncol,-1,-1) :  
      L=float(row)/nrow*255
      S= float(col)/ncol *(-1)  
      r,g,b =  colorsys.hls_to_rgb(H,L,S) 
      color = IToH  (r,g,b ) 

      button_info = [  color  , {"H":H,"L":L,"S":S} ]
      arg= {"bg": color   ,    "command": lambda i=button_info : Print(color=i[0],HLS=i[1])   }

      if init: 
          button = Button(sub_grid,**arg) 
          button.grid(row=row,column=col)   
          button_col.append(button) 
      else : # including just changing 
          MyButton[row][col].config(**arg)  


    if init : MyButton.append(button_col) 




def Print(color="",HLS={}):
  print color, HLS
  if imported: 
    G.bg[0]=color
    IG.BgCl() 

def IToH(r,g,b) : # just cut  
  """float to hexadecimal """
  def ItoH1(r) : 
    r = max(0,r) 
    r = min(255,r) 
    r = int(r) 
    res = format(r,"2x").replace(" ","0") 
    return res 
  return "#" + ItoH1(r) + ItoH1(g) + ItoH1(b)  

def HtoI(color) : # hexa to int  
  """hexadecimal to float """
  r = int(color[1:3],16)
  g = int(color[3:5],16)
  b = int(color[5:7],16)
  return r,g,b



Main() 
  

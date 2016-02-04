#!/usr/bin/python 
import sys
import os

# Improve Python path 
path=os.path.dirname( os.path.abspath(__file__)  ) 
#print "path" , path 

matches = []
for root, dirnames, filenames in os.walk(path):
    sys.path.append(root)


# import USed staff 
import MyGui as MG
#import GlobalDefiner  ; GlobalDefiner.Main() 

import GuyVariables as G
import WorkVariables as W




#print "Abism.py, modules used :", sys.modules.keys()

W.image_name='no_image_name'
W.sys_argv = sys.argv


try: 
   if not sys.argv[1].find(".fits") == -1 : W.image_name = sys.argv[1]
except : pass

if '-i' in W.sys_argv: W.image_name=W.sys_argv[W.sys_argv.index('-i')+1]
if '-p' in W.sys_argv: path=W.sys_argv[W.sys_argv.index('-p')+1]
if '-b' in W.sys_argv: substract_fits=W.sys_argv[W.sys_argv.index('-b')+1]    


 


# PATH
W.path = os.path.dirname( os.path.abspath(__file__)  ) 




if '-a' in sys.argv:
  if  image_fits=='doesnt exits': print "give me an image.fits or don""'""t run automatic"
  else:myapp=MyGui.MyWindow('useless',image_fits,sys.argv)
    

else: # Including with tkinter     


  app=MG.MyWindow()


  

# Background
    #root.configure(background="yellow")
# Background Image 
    #background_image=PhotoImage("cloud.png")
    #background_label = Label(root, image=background_image)
    #background_label.place(x=0, y=0, relwidth=1, relheight=1) 

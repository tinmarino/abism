from numpy import *
try : from Tkinter import *
except  : from tkinter import *

import WorkVariables as W # for verbose
import GuyVariables as G  #for the agruments of buttons type

class MyCalculator:
  def __init__(self,frame):
    self.frame = frame


    self.top_frame= Frame(self.frame,**G.fr_arg)  # for the buttons not the answer
    for i in range(5) :
       self.top_frame.columnconfigure(i,weight=1) # to expand the buttons

    if W.verbose >2 :  print("cal color " , self.top_frame["bg"])
    self.top_frame.pack(side=TOP,expand=1,fill=X)
    self.memory =""

    self.CreateCal()
    return


  def Click(self,key):
    if key == 'C':
      self.entry.delete(0, END) # clear self.entry
    elif key == 'log':
      self.entry.insert(END, "log10(")
    elif key == 'exp':
      self.entry.insert(END, "exp(")
    elif key =='=':
      # avoid division by integer
      if '/' in self.entry.get() and '.' not in self.entry.get():
        self.entry.insert(END, ".0")
      try : self.result = eval(self.entry.get())
      except : self.entry.insert(END, "--> Error!")
      try : self.label.pack_forget()
      except : pass
      self.label = Label(self.frame,text=self.result,**G.lb_arg)
      self.label["fg"] = "red"
      self.label.pack(side=BOTTOM,expand=1,fill=X)
    else:
      self.entry.insert(END, key)
    return

  def CreateCal(self):
    btn_list = [
    '7', '8', '9', '*', 'C',
    '4', '5', '6', '/', 'log',
    '1', '2', '3', '-', 'exp',
    '0', '.', '=', '+', 'E' ]
    # create all buttons with a loop
    r = 1
    c = 0
    for b in btn_list:
      rel = 'raised'
      cmd = lambda x=b: self.Click(x)
      Button(self.top_frame,text=b,
          padx=0,pady=0,justify=CENTER,
          relief=rel,command=cmd).grid(row=r,column=c,sticky="nwse")
      c += 1
      if c > 4:
        c = 0
        r += 1

    self.entry = Entry(self.top_frame, width=30, bg="yellow")
    self.entry.grid(row=0, column=0, columnspan=5,sticky="nswe")
    self.entry.bind('<Return>',lambda event : self.Click("=") )
    return





import GuyVariables as G
from Tkinter import *


def Calculator(): # On LeftTopFrame
    if G.tutorial:
                   text="This button create a Calculator in the G.LabelFrame. You can put the cursor in the text entry and type with the keyboard and press enter to get the result or clisk on the button and '=' returns the answer. Numpy is automatically import as *"
		   text+="\n\nProgrammers a memory would be user firendly, but anyway, nobody will use this calculator, bc or python or awk are much  better..."
		   MG.TutorialReturn({"title":"Calculator",
		   "text":text,
		   })
		   return
    G.cal_bool = not G.cal_bool



    # CONSTRUCT
    if G.cal_bool :

      # FRAME
      G.CalculatorFrame = Frame( G.LeftTopFrame ,**G.fr_arg )
      G.CalculatorFrame.pack(side=TOP,expand=0, fill=X)
      # TITLE
      Label(G.CalculatorFrame,text="Calculator",**G.frame_title_arg).pack(side=TOP,anchor="w")
      G.all_frame.append("CalculatorFrame")
      import Calculator as Cal
      Cal.MyCalculator( G.CalculatorFrame )


    # DESTROY
    elif "CalculatorFrame" in vars(G)  :
      G.CalculatorFrame.destroy()
      if G.in_arrow_frame == "cal_title" : G.arrtitle.destroy()


    # Change tool menu label
    for i in range(1,10) :
       j = G.tool_menu.menu.entrycget(i,"label")
       if "Calculator" in j:
         if G.cal_bool : G.tool_menu.menu.entryconfig(i,label=u'\u25b4 '+'Calculator')
	 else        :  G.tool_menu.menu.entryconfig(i,label=u'\u25be '+'Calculator' )
	 break


    return


"""
    Helper console to run python code in the loop
    For devloppers now (maybe one day embed jupyter kernel in main window
"""
import tkinter as Tk
import threading
import time
import sys
import select
import traceback

from util import log
import back.util_back as W
import front.util_front as G


"""
    This file and function must import everyone I cound need,
    It is an interactive console, made for debugging purpose, using a Tk Frame
    and the eval (or exec) function, to be able to acces Gui and Work varaibles
    while the program is executing, without a true debugger.

    Before 2016, I wrote that :

    A text window is opened, write python command and click on run. These commands know the variables presents in MyGui.py and the module it imports (like WorkVariable, W or GuiVariable, G) , the secret is just a: \n exec string in globals() locals(); \n\nTip : To know if a variable is in W or G : \nfor i in vars(W) : \n  if 'pixel_scale' in i : print(i, vars(i) \n          ",)
"""


def PythonConsole():  # The called function
    ""
    if G.interaction_type == "shell":  # in console

        def worker():
            while 1:
                time.sleep(1)
                try:
                    key_input = my_raw_input("-->")
                    if (key_input == "quit") or (key_input == "break"):
                        break
                    else:
                        try:
                            arith = eval(key_input)
                        except:
                            exec(key_input, globals())
                except Exception as err:
                    traceback.print_exc()
                    log(0, "I tried, I didn't succed command :, try again ")

                if "key_input" in vars():
                    log(0, "You asked for : " + '"' + key_input + '"')

        # Launch worker
        w = threading.Thread(name='console_tread', target=worker)
        w.start()

    else:  # including interaction = tkinter
        # Creating a new window
        window_run = Tk.Tk()
        window_run.title('Python console')

        # Create Text Frame
        def MyText(frame, new=0):  # if not new, Clear it
            if not new:
                G.text_user.pack_forget()
            G.text_user = Tk.Text(frame, bg=G.bg[0])
            G.text_user.insert(Tk.INSERT, "")
            G.text_user.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True)
            G.text_user.focus_force()
            return G.text_user

    # TEXT
    frame = Tk.Frame(window_run)
    frame.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True)
    MyText(frame, new=1)

    # BUTTON
    bu_frame = Tk.Frame(window_run, bg="purple")
    bu_frame.pack(side=Tk.BOTTOM, expand=0, fill=Tk.X)
    but_list = []
    but_list.append(  # Run button
        Tk.Button(bu_frame, text="Run", background="DeepSkyBlue",
                  command=lambda:
                  Run(G.text_user.get("1.0", Tk.END)), **G.bu_arg)
    )
    but_list.append(  # Clear button
        Tk.Button(bu_frame, text="Clear",
                  command=lambda: MyText(frame), **G.submenu_args)
    )
    but_list.append(  # Quit button
        Tk.Button(bu_frame, text='QUIT', background='red',
                  command=window_run.destroy, **G.bu_arg)
    )

    for bu in but_list:
        bu.pack(side=Tk.LEFT, expand=1, fill=Tk.X)

    window_run.mainloop()
    return


def Run(String):  # Run the string in python
    ""
    # EXECUTE
    if String == "help":
        stg = "quit() # to disable interative shell "
        stg += "\nimport sys ; sys.exit() # to kill Abism "
    else:
        exec(String, globals())

    out.close()


def my_raw_input(message):  # Take input from Console if debbuger is in cosole mode (and not Tk)
    sys.stdout.write(message)

    select.select([sys.stdin], [], [])
    return sys.stdin.readline()


def PD(dic):  # print(dictionary for RunCommand, (verbose))
    for k in dic.keys():
        print('%.20s    %.20s' % (k, dic[k]))

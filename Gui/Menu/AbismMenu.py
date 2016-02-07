from Tkinter import *
import GuyVariables as G

import MyGui as MG
import ColorGui             # To change the bg and fg, this is in fucntion,
                            # because obviously it is called more than calling

"""
    TODO : make 4, 5 good appearance profiles.
"""

def AbismMenu(args):                # Menu entry to configure ABSIM
    G.abism_menu=Menubutton(G.MenuBar,**args)
    G.abism_menu.menu=Menu(G.abism_menu,**G.submenu_args)

    # BACKGROUND FOREGROUND
    def AppearanceMenu(parent_menu,who="bg",label="Background") :
      def CrazyColor(who="bg") :
         import color_interactive
         tmp = ( lambda x, who=who : ColorGui.BgCl(color=x,who=who )   )
         color_interactive.Main( func = tmp   )

      appearance_menu= Menu(parent_menu)

      vars(G)["cu_appearance_"+who]=StringVar(); vars(G)["cu_appearance_"+who].set( vars(G)[who][0])
      lst =[["White","#ffffff"],["Grey1","#d0d0d0"] ,
            ["Grey2","#b0b0b0"],["Black","#000000"],
            "\n",
            ["Red","#ff7070"], ["Blue","#b4a6ff"],
     ["Green","#69ff4d"],["DarkGeen","#0a280d"],
     "\n",
     ["Yellow","#ffff73"],
     ["Cyan","#8cffff"],["Purple","#cc55ff"],
        ]
      for i in lst :
          if i == "\n" :
            appearance_menu.add_command(columnbreak=1)
          else :
            appearance_menu.add_radiobutton(
                label=i[0],
                command=lambda i=i: ColorGui.BgCl(color=i[1], who=who),
                variable=vars(G)["cu_appearance_"+who], value = i[1]  ,
            )

      appearance_menu.add_command(
                label="More",
            command=lambda who=who : CrazyColor(who=who) ,
            )


      parent_menu.add_cascade(menu=appearance_menu,label=label,underline=0)
      return


    # PANED
    def PanedConfigMenu(parent_menu,label=""):
        pconfig_menu= Menu(parent_menu)

        # SAS COLOR
        def CrazyColor() :
            import color_interactive
            tmp = lambda x : PanedConfig( {"bg":x} )
            color_interactive.Main( func = tmp )


        G.cu_p1=StringVar(); G.cu_p1.set(G.paned_dic["sashwidth"])
        G.cu_p2=StringVar(); G.cu_p2.set(G.paned_dic["sashrelief"])
        G.cu_p3=StringVar(); G.cu_p3.set(G.paned_dic["bg"])


        lst1 =[
              ["lbl" , "WIDTH"],
              [str(0),0] , [str(2),2] , [str(4),4] , [str(6),6] ,"\n",
        ]


        lst2= [
              ["lbl" , "COLOR" ],
              ["White","#ffffff"],["Grey1","#d0d0d0"] ,
              ["Grey2","#b0b0b0"],["Black","#000000"],
              "\n",
              ["Red","#ff7070"], ["Blue","#b4a6ff"],
              ["Green","#69ff4d"],["DarkGeen","#0a280d"],
              "\n",
              ["Yellow","#ffff73"],
              ["Cyan","#8cffff"],["Purple","#cc55ff"],
              ["More", "uselefsss" ],
              ]

        lst3= [
                ["lbl"    , "relief" ],
                ["FLAT"   , "flat"   ],
                ["RAISED" , "raised" ],
                ["SUNKEN" , "sunken" ],
                ["GROOVE" , "groove" ],
                ["RIDGE " , "ridge"  ],
                "\n",
                ]

        for j in [  [1,"sashwidth"] , [3,"sashrelief"]  , [2,"bg"] ] :
            for i in locals()["lst"+str(j[0])] :
                k = (i,j)
                if i == "\n" :
                    pconfig_menu.add_command(columnbreak=1)
                elif i[0] == "lbl" :
                    pconfig_menu.add_command(label=i[1],bg=None,state=DISABLED)

                elif "More" in str(i[0]) :
                    pconfig_menu.add_command( label="More color",command=  CrazyColor )
                else :
                    pconfig_menu.add_radiobutton(
                        label=i[0],
                        command= lambda k=k : PanedConfig({k[1][1]:k[0][1]})  ,# k=(i,j)
                        variable = vars(G)[ "cu_p" + str(j[0]) ], value = i[1]  ,
                    )



        parent_menu.add_cascade(menu=pconfig_menu,label=label,underline=0)
        return


    def AppearanceMenu1():  # MORE
        more_menu = Menu(G.abism_menu,**G.submenu_args)

        more_lst = [
                [ "Color", lambda : AppearanceMenu(more_menu,who="bg",label="Background Color")   ],  # background color
                [ "Color", lambda : AppearanceMenu(more_menu,who="fg",label="Foreground Color")   ],  # foreground color
                [ "Color", lambda : PanedConfigMenu(more_menu,label="Config Sash") ],
        ]
        for i in more_lst :
            i[1]()
        G.abism_menu.menu.add_cascade(menu=more_menu,label="Appearance",underline=0)
        return




    lst = [
            [ "About ABISM", MG.AboutAbism ],
            [ "Quick Guide", lambda : MG.See(pdf="quick_guide.pdf") ],
            [ "Advanced Manual", lambda : MG.See(pdf="advanced_manual.pdf") ],
            [ "Appearance", AppearanceMenu1  ],
            [ "Quit", MG.Quit  ],
    ]
    for i in lst :
        if "Appearance" in i[0] :
           i[1]()
        else :
           G.abism_menu.menu.add_command(label= i[0], command = i[1] )


    G.abism_menu['menu'] = G.abism_menu.menu
    return G.abism_menu





    if (type(String) is str or type(String) is unicode) and String != "" :
        if W.verbose>0 : print "Opening file : " + String
        W.image_name = String
        InitImage()


    title=W.image_name.split('/')  # we cut the title
    G.parent.title('Abism (' + title[-1]+')')


    return

import GuyVariables as G
import MyGui as MG
import InitGui as IG

from Tkinter import *



def ViewMenu(args):
    G.scale_menu=Menubutton(G.MenuBar, **args)
    G.scale_menu.menu=Menu(G.scale_menu, **G.submenu_args)


    ###############"
    ## COLOR
    def Color() :
        if G.scale_menu_type== "cascade" :
          color_menu = Menu(G.scale_menu, **G.submenu_args)
        else :
          color_menu = G.scale_menu.menu
	color_menu.add_command(label="COLOR", bg=None, state=DISABLED)
           # if we don't want cascade, we just add in the menu

        G.cu_color=StringVar(); G.cu_color.set(G.scale_dic[0]["cmap"]) # because image not loaded yet



        ###########"
        # My colors
        lst = [
                 ["Jet", "jet"],
                 ['Black&White', 'bone'],
          ['Spectral', 'spectral'],
          ["RdYlBu", "RdYlBu"],
          ["BuPu", "BuPu"]
       ]
        for i in lst :
          color_menu.add_radiobutton(label=i[0],
            command=lambda i=i: MG.Scale(dic={"cmap":i[1]}, run="G.cu_cut.set('"+i[1] +"')"   ),
            variable=G.cu_color, value=i[1]) # we use same value as label


        ########
        # Contour
        color_menu.add_command(label='Contour',
            command=lambda  : MG.Scale(dic={"contour":'not a bool'}  )
     )


        #################
        # more colors
        more_color_menu = Menu(color_menu, **G.submenu_args)
        num=0
        for i in G.all_cmaps :
            num+=1
            more_color_menu.add_radiobutton(label=i,
              command=lambda i=i: MG.Scale(dic={"cmap":i}),
              variable=G.cu_color, value=i) # we use same value as label

            if num%30==0  :

              more_color_menu.add_radiobutton(label=i,
                command=lambda i=i : MG.Scale(dic={"cmap":i}),
                variable=G.cu_color, value=i, columnbreak=1) # we use same value as label
        color_menu.add_cascade(menu=more_color_menu, label="More colors", underline=0)



        if G.scale_menu_type== "cascade" :
           G.scale_menu.menu.add_cascade(menu=color_menu, underline=0, label="Color")
        else :
           G.scale_menu.menu.add_command(columnbreak=1)


    ##############
    ###" SCALE FUNCTION
    def Scale():
        if G.scale_menu_type== "cascade" : scale_menu = Menu(G.scale_menu, **G.submenu_args)
        else :
          scale_menu = G.scale_menu.menu
	scale_menu.add_command(label="FCT", bg=None, state=DISABLED)

        G.cu_scale=StringVar(); G.cu_scale.set(G.scale_dic[0]["stretch"])
        lst = [  ["Lin", "x", "linear"], ["Sqrt", "x**0.5", "sqrt"], ["Square", "x**2", "square"], ["Log", "np.log(x+1)/0.69", "log"], ["Arcsinh", "", "arcsinh" ]   ]
        for i in lst :
          scale_menu.add_radiobutton(label=i[0]   ,
            command=lambda i=i : MG.Scale( dic={"fct":i[1], "stretch":i[2]}, run="G.cu_scale.set('"+ i[2] +"')" ) ,
            variable=G.cu_scale, value=i[2]) # we use same value as label


        if G.scale_menu_type== "cascade" :
           G.scale_menu.menu.add_cascade(menu=scale_menu, underline=0, label="Fct")
        else :
           G.scale_menu.menu.add_command(columnbreak=1)

    #G.bu_scale['menu'] = G.bu_scale.menu
    #G.bu_scale.bind("<Button-1>", lambda event : MG.Scale(dic={"tutorial":1, "fct":"truc"}) )


    ##############
    ##  CUT TYPE
    def Cut() :
        if G.scale_menu_type== "cascade" : cut_menu = Menu(G.scale_menu, **G.submenu_args)
        else :
          cut_menu = G.scale_menu.menu
	cut_menu.add_command(label="CUTS", bg=None, state=DISABLED)

        G.cu_cut=StringVar(); G.cu_cut.set("RMS")
        # label , scale_cut_type, key, value
        lst = [  ["RMS", "sigma_clip", "sigma", 3], ["99.95%", "percent", "percent", 99.95],
                 ["99.9%", "percent", "percent", 99.9], ["99.5%", "percent", "percent", 99.5],
                 ["99%", "percent", "percent", 99.], ["90%", "percent", "percent", 90],
                 ["None", "None", "truc", "truc"] ,
          #["Manual", "manual", "truc", "truc"] ,  ]
          ]
        for i in lst :
          cut_menu.add_radiobutton(label=i[0],
            command=lambda i=i : MG.Scale(dic={"scale_cut_type":i[1], i[2]:i[3]}, run="G.cu_cut.set('"+i[0] +"')"  ),
            variable=G.cu_cut, value=i[0]) # we use same value as label

        cut_menu.add_radiobutton(label="Manual",
            command= IG.ManualCut,
            variable=G.cu_cut, value="Manual") # we use same value as label

        if G.scale_menu_type== "cascade" :
           G.scale_menu.menu.add_cascade(menu=cut_menu, underline=0, label="Cut")
        else :
           G.scale_menu.menu.add_command(columnbreak=1)

    #G.bu_cut['menu'] = G.bu_cut.menu
    #G.bu_cut.bind("<Button-1>", lambda event : MG.Scale(dic={"tutorial":1, "scale_cut_type":"truc"}) )

    Color()
    Scale()
    Cut()
    G.scale_menu['menu'] = G.scale_menu.menu

    return G.scale_menu




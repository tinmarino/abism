import Tkinter as Tk

import GuyVariables as G
import WorkVariables as W

import MyGui as MG  # TODO must be removed
import MenuBar      # TODO must removed that too


def AnalysisMenu(args):
    G.analysis_menu= Tk.Menubutton(G.MenuBar, **args)
    G.analysis_menu.menu=Tk.Menu(G.analysis_menu, **G.submenu_args)

    def FitType():
        fit_menu = G.analysis_menu.menu
        fit_menu.add_command(label="Fit Type", bg=None, state=Tk.DISABLED)

        G.cu_fit = Tk.StringVar()
        G.cu_fit.set(W.type["fit"].replace("2D", ""))
        lst1 = [
             ["Gaussian"      ,  "Gaussian"        ,  lambda: MG.FitType("Gaussian"      )],
             ["Moffat"        ,  "Moffat"          ,  lambda: MG.FitType("Moffat"        )],
             ["Bessel1"       ,  "Bessel1"         ,  lambda: MG.FitType("Bessel1"       )],
             #["Gaussian_hole" ,  "Gaussian_hole"   ,  lambda: MG.FitType("Gaussian_hole" )],
             ["None"          ,  "None"            ,  lambda: MG.FitType("None"          )],
             ]
        for i in lst1:
           fit_menu.add_radiobutton(
               label=i[0], command= i[2],
               variable=G.cu_fit, value=i[1]) # we use same value as label

        # MORE OPTIONS
        if not G.more_bool:
            G.analysis_menu.menu.add_command(
                label=u'\u25be '+'More Options', command=MenuBar.MoreWidget)

        else:
            G.analysis_menu.menu.add_command(
                label=u'\u25b4 '+'Less Options',
                command=MenuBar.MoreWidget)


        G.analysis_menu.menu.add_command(columnbreak=1)
        return


    def PickType():
        pick_menu = G.analysis_menu.menu
        pick_menu.add_command(label="Pick Object(s)",
                              bg=None,
                              state=Tk.DISABLED)

        # more options
        G.cu_pick = Tk.StringVar()
        G.cu_pick.set(W.type["pick"])
        lst2 = [
             ["PickOne"   , "one"     ,lambda: Pick.RefreshPick("one")],
             ["Binary Fit", "binary"  ,lambda: Pick.RefreshPick("binary")],
             #["Tight Binary", "tightbinary"  ,lambda: Pick.RefreshPick("tightbinary") ] ,
             ["PickMany"  , "many"    ,lambda: Pick.RefreshPick("many")],
             ["No Pick"   , "nopick"  ,lambda: Pick.RefreshPick("nopick")],
        ]
        lst3 = [
             #["Ellipse"   , "ellipse" ,lambda: Pick.RefreshPick("ellipse") ] ,
             #["Annulus"   , "annulus" ,lambda: Pick.RefreshPick("annulus") ],
             ]

        for i in lst2:
            pick_menu.add_radiobutton(
                 label=i[0], command=i[2],
                 variable=G.cu_pick, value=i[1]) # we use same value as label



    FitType()
    PickType()
    G.analysis_menu['menu'] = G.analysis_menu.menu
    return G.analysis_menu

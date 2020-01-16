"""
    Abism main GUI
"""


# Standard
import sys
from os import system
import warnings
import threading
from time import sleep
import re

# Tkinter
from tkinter import *
from tkinter.filedialog import askopenfilename
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas

# Fancy
import matplotlib
import matplotlib.font_manager as fm
import pyfits
import numpy as np

# Gui
import InitGui as IG  # draw the GUI
import Pick  # to connect PickOne per defautl
import DraggableColorbar
import NormalizeMy

# Plugin
import ReadHeader as RH

# ArrayFunction
import Scale
import Stat
import ImageFunction as IF  # Function on images


# Variables
from GlobalDefiner import MainVar
import GuyVariables as G
import WorkVariables as W


def MyWindow():
    """Create main window loop"""
    # Namespace
    G.parent = Tk()

    # Init main variables
    MainVar()
    # Init main tk window
    IG.WindowInit()
    # Init matplotlib figure
    LaunchImageInit()

    # Loop
    G.parent.mainloop()


def LaunchImageInit():
    """Create the image"""
    def Create():
        G.fig = matplotlib.figure.Figure()  # figsize=(6,6))
        G.figfit = matplotlib.figure.Figure(
            figsize=(5, 2.5))  # figsize=(4,1), dpi=100
        G.figresult = matplotlib.figure.Figure(figsize=(3, 2.5))

    def Size():
        G.fig.subplots_adjust(left=0.07, right=0.93, top=0.95, bottom=0.05)
        G.figfit.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.2)
        G.figresult.subplots_adjust(
            left=0.1, right=0.9, top=1.05, bottom=-0.15)

    def Color():
        G.fig.set_facecolor(G.bg[0])
        G.figfit.set_facecolor(G.bg[0])
        G.figresult.set_facecolor(G.bg[0])

    def Canvas():
        #############
        # IMAGE
        G.ImageFrame.rowconfigure(0, weight=100)
        G.ImageFrame.rowconfigure(1, weight=1)  # not resize the toolbar
        G.ImageFrame.columnconfigure(0, weight=1)  # not resize the toolbar
        G.ImageCanvas = FigureCanvas(G.fig, master=G.ImageFrame)
        G.ImageCanvas.get_tk_widget()["bg"] = G.bg[0]
        # to have no little border use to know if I have focus
        G.ImageCanvas.get_tk_widget()["highlightthickness"] = 0
        G.ImageCanvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        G.all_frame.append("G.ImageCanvas.get_tk_widget()")
        Label(G.ImageFrame, text="Image", **G.frame_title_arg).place(x=0, y=0)

        ###########
        # TOOLBAR
        G.ToolbarFrame = Frame(G.ImageFrame)
        G.ToolbarFrame.grid(row=1, column=0, sticky="nsew")
        G.toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2Tk(
            G.ImageCanvas, G.ToolbarFrame)
        # G.toolbar.grid(row=1,column=0,sticky="nsew")
        G.toolbar.pack()
        G.toolbar["bg"] = G.bg[0]
        for i in G.toolbar.winfo_children():
            i["bg"] = G.bg[0]
        G.all_frame.append("G.toolbar")

        # "
        #  FIT
        G.FitFrame.rowconfigure(0, weight=100)
        G.FitFrame.rowconfigure(1, weight=1)
        G.FitFrame.columnconfigure(0, weight=1)  # not resize the toolbar
        G.dpfit = FigureCanvas(G.figfit, master=G.FitFrame)
        G.dpfit.get_tk_widget()["bg"] = G.bg[0]
        G.dpfit.get_tk_widget()["highlightthickness"] = 0
        G.dpfit.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        G.all_frame.append("G.dpfit.get_tk_widget()")
        Label(G.FitFrame, text="Photometric Profile",
              **G.frame_title_arg).place(x=0, y=0)
        ToolbarFit(init=True)

        #######
        # STAR
        G.ResultFrame.rowconfigure(0, weight=100)
        G.ResultFrame.rowconfigure(1, weight=1)
        G.ResultFrame.columnconfigure(0, weight=1)  # not resize the toolbar
        G.dpresult = FigureCanvas(G.figresult, master=G.ResultFrame)
        G.dpresult.get_tk_widget()["bg"] = G.bg[0]
        G.dpresult.get_tk_widget()["highlightthickness"] = 0
        G.dpresult.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        G.all_frame.append("G.dpresult.get_tk_widget()")
        Label(G.ResultFrame, text="2d shape", **
              G.frame_title_arg).place(x=0, y=0)
        ToolbarResult(init=True)

    def Call():
        # in case the user launch the program without giving an image as arg
        if W.image_name != "no_image_name":
            InitImage()
    Create()
    Size()
    Color()
    Canvas()
    Call()


def ToolbarFit(init=False):
    """Create toolbar"""
    if init:
        if G.toolbar_fit_bool:
            photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")
        else:
            photo = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
        G.fit_frame_arrow = Button(
            G.FitFrame, command=ToolbarFit, image=photo, **G.bu_arg)
        G.fit_frame_arrow.image = photo  # keep a reference
        G.fit_frame_arrow.place(relx=1., rely=1., anchor="se")
        return

    G.toolbar_fit_bool = not G.toolbar_fit_bool

    # CREATE
    if G.toolbar_fit_bool:
        photo = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
        G.fit_frame_arrow['image'] = photo
        G.fit_frame_arrow.image = photo  # keep a reference
        if not "toolbar_fit" in vars(G):
            G.toolbar_fit = matplotlib.backends.backend_tkagg.NavigationToolbar2Tk(
                G.dpfit, G.FitFrame)
        G.toolbar_fit.grid(row=1, column=0, sticky="nsew")

        # COLOR
        G.toolbar_fit["bg"] = G.bg[0]
        for i in G.toolbar_fit.winfo_children():
            i["bg"] = G.bg[0]
        G.all_frame.append("G.toolbar_fit")

        # ARROW
        ToolbarFit(init=True)

    # DESTROY
    else:  # including not toolbar_bool and not init
        photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")
        G.fit_frame_arrow['image'] = photo
        G.fit_frame_arrow.image = photo  # keep a reference
        G.toolbar_fit.grid_forget()
        ToolbarFit(init=True)


def ToolbarResult(init=False):
    """Create result frame"""
    if init:
        if G.toolbar_result_bool:
            photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")
        else:
            photo = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
        G.result_frame_arrow = Button(
            G.ResultFrame, command=ToolbarResult, image=photo, **G.bu_arg)
        G.result_frame_arrow.image = photo  # keep a reference
        G.result_frame_arrow.place(relx=1., rely=1., anchor="se")
        return

    G.toolbar_result_bool = not G.toolbar_result_bool

    # CREATE
    if G.toolbar_result_bool:
        photo = PhotoImage(file=W.path + "/Icon/arrow_up.gif")
        G.result_frame_arrow['image'] = photo
        G.result_frame_arrow.image = photo  # keep a reference
        if not "toolbar_result" in vars(G):
            G.toolbar_result = matplotlib.backends.backend_tkagg.NavigationToolbar2Tk(
                G.dpresult, G.ResultFrame)
        G.toolbar_result.grid(row=1, column=0, sticky="nsew")

        # COLOR
        G.toolbar_result["bg"] = G.bg[0]
        for i in G.toolbar_result.winfo_children():
            i["bg"] = G.bg[0]
        G.all_frame.append("G.toolbar_result")
        ToolbarResult(init=True)

    # DESTROY
    else:  # including not toolbar_bool and not init
        photo = PhotoImage(file=W.path + "/Icon/arrow_down.gif")
        G.result_frame_arrow['image'] = photo
        G.result_frame_arrow.image = photo  # keep a reference
        G.toolbar_result.grid_forget()
        ToolbarResult(init=True)


def InitImage(new_fits=True):
    """Init image: cube_change when this is jsu ta change in the frame of the cube"""
    ######################
    # CLEAR OLD  CANVAS and Colorbar WITH CLF
    try:  # not done if one image was previously loaded , means if used "open" button
        G.cbar.disconnect()
        del G.cbar
        G.fig.clf()
    except BaseException:
        W.log(2, 'InitImage, cannot delete cbar')

    # LOAD IMAGE AND HEADER
    if new_fits:
     # FITS IMAGE
     # if re.match(".*\.fits",W.image_name):
        G.png_bool = False
        W.hdulist = pyfits.open(W.image_name)

        W.Im0 = W.hdulist[0].data  # define the 2d image : W.Im0
        W.Im0[np.isnan(W.Im0)] = 0  # delete the np.nan
        RH.CallHeaderClass(W.hdulist[0].header)          # HEADER

    # NON FITS IMAGE
    if False:
        # image is 600*600*3 whereas a cube is 9*500*500
        G.png_bool = True
        from PIL import Image
        im = Image.open(W.image_name)
        W.Im0 = np.asarray(im)
        W.log(3, "Image_name", W.image_name, "\n\n")
        W.Im0 = W.Im0.transpose([2, 0, 1])
        hdu = pyfits.PrimaryHDU(W.Im0)
        W.hdulist = pyfits.HDUList([hdu])
        RH.CallHeaderClass({"INSTRUMENT": "Personal Image"})

     ####################
     ### CUBES         ##
     ####################
    if len(W.hdulist[0].data.shape) == 3:
        # if not G.png_bool and (len(W.hdulist[0].data.shape)==3):# for CUBES
        if new_fits:
            W.cube_num = W.hdulist[0].data.shape[0] - \
                1  # we start with the last index
        # should run if abs(G.cube_num)<len(G.hdulist)
        if abs(W.cube_num) < len(W.hdulist[0].data[:, 0, 0]):
            if W.cube_bool == 0:  # to load cube frame
                W.cube_bool = 1
                IG.Cube()
            W.Im0 = W.hdulist[0].data[W.cube_num]

        else:
            W.cube_num = W.hdulist[0].data.shape[0] - 1
            W.log(1, '\nERROR InitImage@MyGui.py :' + W.image_name
                + ' has no index ' + str(W.cube_num) +
                "Go back to the last cube index :"
                + str(W.cube_num) + "\n")
        G.cube_var.set(int(W.cube_num + 1))

    else:  # including image not a cube, we try to destroy cube frame
        W.cube_bool = 0
        IG.Cube()

     ##############################
     # VARIABLES AND LABELS
     ##############################
    if new_fits:
        ScienceVariable()

     ######################
     # SCALE  image
     ########################

    if re.match(r".*\.fits", W.image_name):
        # much faster also draw_artist can help ?
        G.current_image = W.Im0.astype(np.float32)
        W.log(3, "dic init", G.scale_dic[0])
        Scale(dic=G.scale_dic[0], load=1)  # not to draw the image.
    else:
        G.current_image = W.Im0

    # "
    #     DISPLAY  the image HERE the origin = lower change everything in y
    G.ax1 = G.fig.add_subplot(111)
    if not G.png_bool:
        drawing = G.ax1.imshow(G.current_image,
                               vmin=G.scale_dic[0]["min_cut"], vmax=G.scale_dic[0]["max_cut"],
                               cmap=G.scale_dic[0]["cmap"], origin='lower')
    else:  # This is not a fits image
        drawing = G.ax1.imshow(G.current_image,
                               cmap=G.scale_dic[0]["cmap"])

    #############################
    #   COMPASS
    ############################
    try:
        RemoveCompass()
    except BaseException:
        pass
    DrawCompass()

    ####
    # COLORBAR, TOOLBAR update , colorabr disconnected at begining, next to clf()
    G.toolbar.update()
    G.cbar = G.fig.colorbar(drawing, pad=0.02)
    # G.cbar.set_norm(NormalizeMy.MyNormalize(vmin=image.min(),vmax=image.max(),stretch='linear'))
    G.cbar = DraggableColorbar.DraggableColorbar(G.cbar, drawing)
    G.cbar.connect()

    ################
    # IMAGE GET INTENSITY  in G.toolbarframe
    def z(x, y):
        return W.Im0[y, x]

    def z_max(x, y):
        return IF.PixelMax(W.Im0, r=(y - 10, y + 11, x - 10, x + 11))[1]

    def format_coordinate(x, y):
        x, y = int(x), int(y)
        return "zmax=%5d, z=%5d, x=%4d, y=%4d" % (z_max(x, y), z(x, y), x, y)

    G.ax1.format_coord = format_coordinate

    ######################
    # DRAW FIG AND COLOR BAR
    ######################
    G.fig.canvas.draw()

    #####################
    ###  SOME  CLICKS #
    #####################
    Pick.RefreshPick("one")  # assuming that the default PIck is setted yet

    # I don't know why I need to pu that at the end but it worls like that
    # # does not work it put in Science Variables
    if new_fits:
        G.label_bool = 0
        IG.LabelResize()

    return


def DrawCompass():
    """Draw WCS compass to see 'north'"""
    W.log(3, "MG, what do I know from header", vars(W.head))
    if not (("CD1_1" in vars(W.head)) and ("CD2_2" in vars(W.head))):
        W.log(0, "WARNING WCS Matrix not detected,",
              "I don't know where the north is")
        W.head.CD1_1 = W.head.pixel_scale * 3600
        W.head.CD2_2 = W.head.pixel_scale * 3600

    if not (("CD1_2" in vars(W.head)) and ("CD2_1" in vars(W.head))):
        W.head.CD1_2, W.head.CD2_1 = 0, 0

    north_direction = [-W.head.CD1_2, -W.head.CD1_1] / \
        np.sqrt(W.head.CD1_1**2 + W.head.CD1_2**2)
    east_direction = [-W.head.CD2_2, -W.head.CD2_1] / \
        np.sqrt(W.head.CD2_1**2 + W.head.CD2_2**2)

    # CALCULATE ARROW SIZE
    coord_type = "axes fraction"
    if coord_type == "axes fraction":    # for the arrow in the image, axes fraction
        arrow_center = [0.95, 0.1]  # in figura fraction
        # -  because y is upside down       think raw collumn
        north_point = arrow_center + north_direction / 10
        east_point = arrow_center + east_direction / 15

    # for the arrow IN the image coords can be "data" or "figure fraction"
    elif coord_type == "data":
        # in figure fraction
        arrow_center = [0.945 * len(W.Im0), 0.1 * len(W.Im0)]
        # -  because y is upside down       think raw collumn
        north_point = [arrow_center + north_direction / 20 *
                       len(W.Im0), arrow_center - north_direction / 20 * len(W.Im0)]
        east_point = [north_point[1] + east_direction /
                      20 * len(W.Im0), north_point[1]]
    W.north_direction = north_direction
    W.east_direction = east_direction
    W.log(3, "north", north_point, east_point,
          arrow_center, north_direction, east_direction)

    #################
    # 2/ DRAW        0 is the end of the arrow
    if W.head.wcs_bool:
        G.north = G.ax1.annotate("",
                                 # we invert to get the text at the end of the arrwo
                                 xy=arrow_center, xycoords=coord_type,
                                 xytext=north_point, textcoords=coord_type, color="purple",
                                 arrowprops=dict(
                                     arrowstyle="<-", facecolor="purple", edgecolor="purple"),
                                 # connectionstyle="arc3"),
                                 )
        G.east = G.ax1.annotate("",
                                xy=arrow_center, xycoords=coord_type,
                                xytext=east_point, textcoords=coord_type, color="red",
                                arrowprops=dict(
                                    arrowstyle="<-", facecolor='red', edgecolor='red'),
                                # connectionstyle="arc3"),
                                )
        G.north_text = G.ax1.annotate(
            "N", xy=north_point, textcoords=coord_type, color='purple')
        G.east_text = G.ax1.annotate(
            "E", xy=east_point, textcoords=coord_type, color='red')


def RemoveCompass():
    G.ax1.texts.remove(G.north)
    G.ax1.texts.remove(G.east)
    G.ax1.texts.remove(G.north_text)
    G.ax1.texts.remove(G.east_text)


def __automatic__():   # Not finished, not called
    center, pixel_max = IF.GoodPixelMax(W.Im0, 'bidon')
    # FindStarCenter
    W.log(3, 'center,pixel_max : ', center, pixel_max)
    # FWHM
    FWHM = IF.FWHM(W.Im0, center)
    W.log(3, FWHM)
    StrehlMeter(center, 10 * FWHM)  # the image is in G


def ScienceVariable():
    # BPM
    if "bpm_name" in vars(W):
        hdu = pyfits.open(W.bpm_name)
        W.Im_bpm = hdu[0].data
    else:
        W.Im_bpm = 0 * W.Im0 + 1
    # Sorted image
    W.sort = W.Im0.flatten()
    W.sort.sort()
    # STAT
    vars(W.imstat).update(Stat.Stat(W.Im0))

    # Image parameters
    if "ManualFrame" in vars(G):
        for i in G.image_parameter_list:
            vars(G.tkvar)[i[1]].set(vars(W.head)[i[1]])
        # to restore the values in the unclosed ImageParameters Frame
        IG.GetValueIP("", destroy=False)
    # LABELS
    IG.ResetLabel(expand=True)
    FitType(W.type["fit"])


def Histopopo():
    """This is drawing the histogram of pixel values. It may be usefull.
    Programmers, We can implement a selection of the scale cut of the image
    with a dragging the vertical lines., with a binning of the image,
    this could even be in real time.
    """
    matplotlib.font_manager.FontEntry(fname="DejaVuSans")
    font0 = matplotlib.font_manager.FontProperties()
    G.figfit.clf()
    G.ax2 = G.figfit.add_subplot(111)
    G.ax2.format_coord = lambda x, y: ""  # not see x y label in the toolbar

    #plt.rcParams['mathtext.fontset'] = "regular"
    # plt.rcParams['mathtext.default']="regular"
    font = {'family': 'sans-serif', 'sans-serif': ['Helvetica'],
            'weight': 'normal', 'size': 12}
    #matplotlib.rc('font', **font)
    G.ax2.set_xticklabels(G.ax2.get_xticks(), font)
    G.ax2.set_xticklabels(G.ax2.get_xticks(), font)
    # ,label='Encircled Energy')
    G.ax2.axvline(x=G.scale_dic[0]["min_cut"],
                  color='black', linestyle='-', linewidth=2)
    # ,label='Encircled Energy')
    G.ax2.axvline(x=G.scale_dic[0]["max_cut"],
                  color='black', linestyle='-', linewidth=2)
    # G.ax2.set_title("HISTOGRAM")
    G.ax2.set_xticklabels(
        W.sort, fontproperties=fm.FontProperties(family="Helvetica"))
    G.hist = G.ax2.hist(W.sort, 100, log=True)  # n, bin, patches

    # LABELS Because pb of font
    #G.ax2.set_xticks((  0,np.max(G.hist[0]) ))
    #G.ax2.set_yticks((  0,np.max(W.Im0) ))

    warnings.simplefilter("ignore")
    G.figfit.canvas.draw()
    warnings.simplefilter("default")
    return


def Quit():
    """Kill process"""
    W.log(1, 'Closing Abism, Goodbye. Come back soon.' + "\n" + 100 * '_' + 3 * "\n")
    G.parent.destroy()
    sys.exit(1)


def Restart():
    """ TODO move me to Global Definer, WritePref and ReadPref
        Pushing this button will close ABISM and restart it the same way it was launch before.
        Programmers: this is made to reload the Software if a modification in the code were made.
    """

    #################
    # prepare arguments
    arg = W.sys_argv

    # IMAGE_NAME
    matching = [s for s in arg if ".fits" in s]
    if len(matching) > 0:
        arg[arg.index(matching[0])] = W.image_name
    else:
        arg.insert(1, W.image_name)

    # COLOR MAP
    try:
        cmap = G.cbar.cbar.get_cmap().name
    except BaseException:
        cmap = "jet"  # if no image loaded
    if not isinstance(cmap, str):
        cmap = "jet"
    for i in [
            ["--verbose", W.verbose],
        ["--bg", G.bg[0]],
        ["--fg", G.fg[0]],

        # SCALE DIC
        ["--cmap", cmap],
        ["--scale_dic_stretch", G.scale_dic[0]["stretch"]],
        ["--scale_dic_scale_cut_type", G.scale_dic[0]["scale_cut_type"]],
        ["--scale_dic_percent", G.scale_dic[0]["percent"]],


        # FRAME
        ["--parent", G.parent.geometry()],
        ["--TextPaned", G.TextPaned.winfo_width()],
        ["--DrawPaned", G.DrawPaned.winfo_width()],
        ["--LabelFrame", G.LabelFrame.winfo_width()],
        ["--LeftBottomFrame", G.LeftBottomFrame.winfo_height()],
        ["--LeftTopFrame", G.LeftTopFrame.winfo_height()],
        ["--ImageFrame", G.ImageFrame.winfo_height()],
        ["--RightBottomPaned", G.RightBottomPaned.winfo_height()],
        ["--FitFrame", G.FitFrame.winfo_width()],
        ["--ResultFrame", G.ResultFrame.winfo_width()],
        ["--ImageName", W.image_name],
    ]:
        if not i[0] in arg:
            arg.append(i[0])
            arg.append('"' + str(i[1]) + '"')
        else:
            arg[arg.index(i[0]) + 1] = '"' + str(i[1]) + '"'

    ###########
    # PREPARE STG command line args
    stg = "python "
    for i in arg:
        stg += " " + i
    stg += " &"  # To keep the control of the terminal
    W.log(0, "\n\n\n" + 80 * "_" + "\n",
          "Restarting ABISM with command:\n" + stg + "\nplease wait")

    ##########
    # DESTROY AND LAUNCH
    G.parent.destroy()  # I destroy Window,
    system(stg)         # I call an other instance
    sys.exit(1)         # I exit the current process.
    # As the loop is now opened, this may not be necessary but anyway it is safer


def Clear():
    """Clear the image frames and reinitiate its.
    Made as button callback  in order to delete some arrows,
        for example with the pick many mode.
    """

    try:
        G.AnswerFrame.destroy()
    except BaseException:
        pass
    LaunchImageInit()


def Save(first=1):
    """Save results of Strehl logging
    first: time you save, to print(header and staff)
    """
    try:
        from os import popen
        date = popen("date").read().split()
        pwd = popen("pwd").read()

    except BaseException:
        date = ["day", "month", "day", "time", "pff", "year"]
        pwd = "no_pwd"

    # Archive Name
    archive = "Abm_" + W.image_name.split('/')[-1].split('.fits')[0]
    try:
        archive += "_" + date[-1] + "_" + date[1]
        archive += "_" + date[2] + "_" + date[3] + ".txt"
    except BaseException:
        pass

    # Bufferise
    appendBuffer = open(archive, 'a')
    W.log(0, "Writting files in ", archive)
    W.log(0, "in directory : " + pwd)

    # Write
    appendBuffer.write("#Abism -> data from :" + W.image_name)
    appendBuffer.write("#######\n----->1/ Header \n still missing in abism...")
    appendBuffer.write("#######\n----->2/ Strehl Output : \n")

    try:
        _ = W.answer_saved   # check existence
    except BaseException:
        W.answer_saved = W.answer

    try:  # in case we just took PickOne and cannot sort
        for key in sorted(W.answer_saved, key=lambda x: int(x.split(".")[-1])):
            appendBuffer.write(key + " " + str(W.answer_saved[key]) + '\n')
    except BaseException:
        for key in W.answer_saved:
            appendBuffer.write(key + " " + str(W.answer_saved[key]) + '\n')

    #  Terminate
    appendBuffer.write("\n \n")
    appendBuffer.close()


def CubeDisplay(String):
    """Callback for cube button + -"""
    if String == '+':
        W.cube_num += 1
    elif String == '-':
        W.cube_num -= 1
    elif String == '0':
        W.cube_num = float(G.cube_var.get())

    G.cube_var.set(W.cube_num + 1)
    InitImage(new_fits=False)


def Hide(hidden=0):
    """Hide Pane as button callback"""
    W.log(3, "My hidden", hidden)
    if G.hidden_text_bool:
        G.MainPaned.sash_place(0, G.hidden_frame_size, 0)
        G.bu_hide["text"] = u'\u25c2'  # rigth arrow

    else:
        G.hidden_frame_size = G.MainPaned.sash_coord(
            0)[0]  # bakcup the x position of the sash
        G.MainPaned.sash_place(0, 10, 0)
        G.bu_hide["text"] = u'\u25b8'  # left arrow
    G.hidden_text_bool = not G.hidden_text_bool


def SubstractBackground():
    """Subtract A background image
    Choose a FITS image tho subtract to the current image to get read of the sky value or/and the pixel response. This is a VERY basic task that is only subtracting 2 images. It could be improved but image reduction is not the goal of ABISM."""
    String = askopenfilename(
        filetypes=[("fitsfiles", "*.fits"), ("allfiles", "*")])
    W.image_bg_name = String     # image_background_name
    W.hdulist_bg = pyfits.open(String)
    W.Im0_bg = W.hdulist_bg[0].data
    if (not W.Im0.shape == W.Im0_bg.shape):
        W.Log(0, 'ERROR : Science image and Background image should have the same shape')
    else:
        W.Im0 -= W.Im0_bg
        InitImage()


def FitType(name):  # strange but works
    """if name=="tutorial":
               if G.tutorial:
                           text="\nDifferent fit types: A Moffat fit is setted by default. You can change it. Gaussian, Moffat,Bessel are three parametrics psf. Gaussian hole is a fit of two Gaussians with the same center by default but you can change that in more option in file button. The Gaussian hole is made for saturated stars. It can be very useful, especially because not may other software utilize this fit.   "
                           text+="\n\nWhy is the fit type really important? The photometry and the peak of the objects utilize the fit. For the photometry, the fit measure the aperture and the maximum is directly taken from the fit. So changing the fit type can change by 5 to 10% your result."
                           text+="\n\nWhat should I use? For strehl <10% Gaussian, for Strehl>50% Bessel, between these, Moffat. "
                           text+="\n\nProgrammers: Strehl@MyGui.py calls SeeingPSF@ImageFunction.py which calls BasicFunction.py.\n To do : fastly analyse the situation and choose a fit type consequently."
                           TutorialReturn({"title":"Choose Fit Type",
                           "text":text,
                           })
                           return
               else : return # include no G.tutorial"""
    W.type["fit"] = name
    G.cu_fit.set(name.replace("2D", ""))  # to change radio but, check
    try:
        if W.aniso_var.get() == 0:
            W.type["fit"] = W.type["fit"].replace('2D', '')
        elif W.aniso_var.get() == 1 and not '2D' in W.type["fit"]:
            W.type["fit"] += '2D'
    except BaseException:
        if W.type["fit"].find('2D') == -1:
            W.type["fit"] += '2D'
    if not W.type["fit"].find('None') == -1:
        W.type["fit"] = 'None'

    # Saturated
    if "Gaussian_hole" in W.type["fit"]:
        try:
            if W.same_center_var.get() == 0:
                W.type["fit"] = W.type["fit"].replace('same_center', '')
                if W.verbose > 0:
                    print(
                        " same_center : We asssume that the saturation is centered at the center of th object")
            elif not 'same_center' in W.type["fit"]:
                W.type["fit"] += "same_center"
                if W.verbose > 0:
                    print(
                        "not same_center : We asssume that the saturation isn't centered at the center of th object")
        except BaseException:
            if not 'same_center' in W.type["fit"]:
                W.type["fit"] += "same_center"
    if W.verbose > 0:
        print('Fit Type = ' + W.type["fit"])

    # same psf
    if W.same_psf_var.get() == 0:
        W.same_psf = 0
        if W.verbose > 0:
            print(" same_psf : We will fit the binary with the same psf")
    elif W.same_psf_var.get() == 1:
        W.same_psf = 1
        if W.verbose > 2:
            print(" not same_psf : We will fit each star with independant psf")

    # change the labels
    #G.fit_type_label["text"] = W.type["fit"]

    return


def VarSet(var, value):  # change the value of a WorkVariable
    string = var + '=' + '"' + value + '"'
    if W.verbose > 0:
        print("-----> VarSet : Change the value from:", string)
    exec(string)
    return


def Scale(dic={}, load=0, run=""):
    """Change contrast and color , load if it is loaded with InitImage
    remember that we need to update G.scael_dic in case we opne a new image, but this is not really true"""
    W.log(2, "Scale called ", dic)
    if "tutorial" in dic:
        if G.tutorial:
            if "cmap" in dic:
                text = "A menu button will be displayed and in this, there is waht is called some radio buttons, which permits to select a color for the image. And there is at the bottom a button for plotting the contours of objects. You have for colors from bright to faint:\n\n"
                text += "->jet: red,yellow,green,blue\n"
                text += "->Black&White: White,Black\n"
                text += "->spectral:red,yellow,green,blue, purple\n"
                text += "->RdYlBu: blue, white, red\n"
                text += "->BuPu: purple, white\n"
                text += "->Contour: This will display the 3 and 5 sigma contours of the objects on the image. To delete the contours that may crowd your image, just click again on contour.\n"
                TutorialReturn({"title": "Image Color",
                                "text": text,
                                })
            elif "fct" in dic:
                text = "A menu button with some radio button is displayed. Chose the function that will transforme the image according to a function. This function is apllied to the images values rescaled from 0 to 1 and then the image is mutliplied again fit the true min and max cut made.\n\n"
                text += "Programmers, This function is trabsforming G.current_image when the true image is stocked under W.Im0 \nIf you want to add some function look at the InitGuy.py module, a function with some (2,3,4) thresholds (=steps) could be usefull to get stars of (2,3,4) differents color, nothing more, one color for each intensity range. This can be done with if also. "
                TutorialReturn({"title": "Rescale Image Function",
                                "text": text,
                                })
            elif "scale_cut_type" in dic:
                text = "A menu button with some radio button is displayed. You need to chose the cut for scaling the displaued color of the image (ie: the values of the minimum and maximum color). Youhave different way of cutting :\n\n"
                text += "-> None, will take the true max and min values of th image to set the displayed color range. Usefull for saturated objects.\n"
                text += "-> Percentage, set the max (min) color as the maximum (minimum) value of the central percent% values. For example, 95% reject the 2.5% higher values and then take the maximum of the kept values.\n"
                text += "-> RMS, will take make a -1,5 sigma for min and max\n"
                text += "-> Manual, The power is in your hand, a new frame is displayed, enter the min and max value. When satified, please close the frame.\n"
                text += "\n\nProgrammers, a cut setted with the histogram can be nice but not so usefull."
                TutorialReturn({"title": "Cut Image Scale",
                                "text": text,
                                })
            return
        else:
            return  # including no tutorial

    # RUN THE Stff to change radio button for mac
    if run != "":
        if W.verbose > 3:
            print("Scale, run=", run)
        exec(run, globals())

        #######
        # INIT  WITH CURRENT IMAGE parameters.
    # try :
    if not load:
        G.scale_dic[0]["cmap"] = G.cbar.mappable.get_cmap().name  # Image color
        G.scale_dic[0]["min_cut"] = G.cbar.cbar.norm.vmin  # Image color
        G.scale_dic[0]["max_cut"] = G.cbar.cbar.norm.vmax  # Image color

    ###########
    # CONTOURS
    if("contour" in dic) and not isinstance(dic["contour"], bool):
        if W.verbose > 3:
            print("contour ? ", G.scale_dic[0]["contour"])
        G.scale_dic[0]["contour"] = not G.scale_dic[0]["contour"]
        if G.scale_dic[0]["contour"]:
            if "median" not in G.scale_dic[0]:
                tmp = vars(W.imstat)
            mean, rms = tmp["mean"], tmp["rms"]
            c0, c1, c2, c3, c4, c5 = mean, mean + rms, mean + 2 * \
                rms, mean + 3 * rms, mean + 4 * rms, mean + 5 * rms
            G.contour = G.ax1.contour(W.Im0, (c2, c5),
                                      origin='lower', colors="k",
                                      linewidths=3)
            # extent=(-3,3,-2,2))
            if W.verbose > 0:
                print(
                    "---> Contour of 3 and 5 sigma, clik again on contour to delete its.")

        else:  # include no contour  delete the contours
            if not load:
                for coll in G.contour.collections:
                    G.ax1.collections.remove(coll)

    ############
    # UPDATE UPDATE
    if W.verbose > 2:
        print(" MG.scale ,Scale_dic ", G.scale_dic[0])
    dic["contour"] = G.scale_dic[0]["contour"]
    G.scale_dic[0].update(dic)  # UPDATE DIC

    ###########
    # CUT
    if "scale_cut_type" in dic:
        if dic["scale_cut_type"] == "None":
            # IG.ManualCut()
            G.scale_dic[0]["min_cut"] = W.imstat.min
            G.scale_dic[0]["max_cut"] = W.imstat.max
        else:
            import Scale  # otherwise get in conflict with Tkinter
            dictmp = {"whole_image": "useless"}
            dictmp.update(G.scale_dic[0])
            tmp = Scale.MinMaxCut(W.Im0, dic=dictmp)
            G.scale_dic[0]["min_cut"] = tmp["min_cut"]
            G.scale_dic[0]["max_cut"] = tmp["max_cut"]
        if W.verbose > 2:
            "I called Scale cut "

    ######
    # SCALE FCT
    if "stretch" not in G.scale_dic[0]:  # in case
        G.scale_dic[0]["stretch"] = "linear"

    ###############
    #  RELOAD THE IMAGE
    if not load:
        Draw()

     ##########
     # RELOAD PlotStar
        try:
            PlotStar2()
        except BaseException:
            pass  # in case you didn't pick the star yet
    return


def Draw(min=None, max=None, cmap=None, norm=False, cbar=True):
    if min is not None:
        G.scale_dic[0]["min_cut"] = min
        G.scale_dic[0]["max_cut"] = max
    if cmap is not None:
        G.scale_dic[0]["cmap"] = cmap

    cmap = G.scale_dic[0]["cmap"]
    min, max = G.scale_dic[0]["min_cut"], G.scale_dic[0]["max_cut"]

    mynorm = NormalizeMy.MyNormalize(
        vmin=min, vmax=max, stretch=G.scale_dic[0]["stretch"], vmid=min - 5)
    G.cbar.mappable.set_cmap(cmap)
    G.cbar.cbar.set_cmap(cmap=cmap)
    G.cbar.cbar.set_norm(mynorm)
    G.cbar.mappable.set_norm(mynorm)

    G.cbar.cbar.patch.figure.canvas.draw()
    G.fig.canvas.draw()

    try:  # if no fig result, and if not work nevermind
        for i in (G.figresult_mappable1, G.figresult_mappable2):
            i.set_norm(mynorm)
            i.set_cmap(cmap)
        G.figresult.canvas.draw()
    except BaseException:
        if W.verbose > 2:
            print("MyGui, Draw cannot draw in figresult")
    # except : pass


def FigurePlotOld(x, y, dic={}):
    """ x and y can be simple list
    or also its can be list of list for a multiple axes
    dic : title:"string", logx:bol, logy:bol, xlabel:"" , ylabel:""
    """
    #from matplotlib import pyplot as plt
    if W.verbose > 3:
        print("MG.FigurePlotCalled")
    from matplotlib import pyplot as plt  # necessary if we are in a sub process
    default_dic = {"warning": 0, "title": "no-title"}
    default_dic.update(dic)
    dic = default_dic

    def SubPlot(x, y):
        nx, ny = 7, 5
        if "logx" in dic:
            ax.set_xscale("log")
        if "logy" in dic:
            ax.set_yscale("log")
        if "xlabel" in dic:
            ax.set_xlabel(dic["xlabel"])
        if "ylabel" in dic:
            ax.set_ylabel(dic["ylabel"])

        ax.plot(x, y)

        ax2 = ax.twiny()
        ax2.set_xticks(np.arange(nx))
        xlist = np.linspace(0, x[-1] * W.head.pixel_scale, nx)
        xlist = [int(1000 * u) for u in xlist]
        ax2.set_xticklabels(xlist, rotation=45)
        ax2.set_xlabel(u"Distance [mas]")

        ax3 = ax.twinx()
        ax3.set_yticks(np.arange(ny))
        ylist = np.linspace(0, y[0], ny)
        ylist = [int(u) for u in ylist]
        ax3.set_yticklabels(ylist)
        ax3.set_ylabel(u"number count per pixel")
        ############
        # TWIN axes

    # MyProcess() :
    if W.verbose > 3:
        print("___________________________________________\n",
              threading.currentThread().getName(), "Starting------------------\n")

    global ax
    G.contrast_fig.clf()
    # tfig.canvas.set_window_title(dic["title"])

    if not (isinstance(x[0], list)):  # otherwise multiple axes
        if W.verbose > 3:
            print("MG.FigurePlot, we make a single plot")
        ax = G.contrast_fig.add_subplot(111)
        #from mpl_toolkits.axes_grid1 import host_subplot
        #ax = host_subplot(111)
        SubPlot(x, y)
        # if dic.has_key("title") :
        #   plt.title(dic["title"])
        if not dic["warning"]:
            warnings.simplefilter("ignore")
        if W.verbose > 3:
            print("I will show ")
        G.contrast_fig.canvas.draw()
        if not dic["warning"]:
            warnings.simplefilter("default")
        # tfig.show()
    if W.verbose > 3:
        print("___________________________________________\n",
              threading.currentThread().getName(), "Exiting------------------\n")

    #w = threading.Thread(name='figure_tread', target=MyProcess)
    # w.start()
    return


def FigurePlot(x, y, dic={}):
    """ x and y can be simple list
    or also its can be list of list for a multiple axes
    dic : title:"string", logx:bol, logy:bol, xlabel:"" , ylabel:""
    """
    #from matplotlib import pyplot as plt
    W.log(3, "MG.FigurePlotCalled")
    from matplotlib import pyplot as plt  # necessary if we are in a sub process
    default_dic = {"warning": 0, "title": "no-title"}
    default_dic.update(dic)
    dic = default_dic

    def SubPlot(x, y):
        nx, ny = 7, 5
        if "logx" in dic:
            ax.set_xscale("log")
        if "logy" in dic:
            ax.set_yscale("log")
        if "xlabel" in dic:
            ax.set_xlabel(dic["xlabel"])
        if "ylabel" in dic:
            ax.set_ylabel(dic["ylabel"])

        ax.plot(x, y)

        ax2 = ax.twiny()
        ax2.set_xticks(np.arange(nx))
        xlist = np.linspace(0, x[-1] * W.head.pixel_scale, nx)
        xlist = [int(1000 * u) for u in xlist]
        ax2.set_xticklabels(xlist, rotation=45)
        ax2.set_xlabel(u"Distance [mas]")

        ax3 = ax.twinx()
        ax3.set_yticks(np.arange(ny))
        ylist = np.linspace(0, y[0], ny)
        ylist = [int(u) for u in ylist]
        ax3.set_yticklabels(ylist)
        ax3.set_ylabel(u"number count per pixel")
        ############
        # TWIN axes

    W.log(3, 50 * '_', "\n", threading.currentThread().getName(),
          "Starting------------------\n")

    global ax
    G.contrast_fig.clf()
    # tfig.canvas.set_window_title(dic["title"])

    if not isinstance(x[0], list):  # otherwise multiple axes
        W.log(3, "MG.FigurePlot, we make a single plot")
        ax = G.contrast_fig.add_subplot(111)
        #from mpl_toolkits.axes_grid1 import host_subplot
        #ax = host_subplot(111)
        SubPlot(x, y)
        if not dic["warning"]:
            warnings.simplefilter("ignore")
        W.log(3, "I will show ")
        G.contrast_fig.canvas.draw()
        if not dic["warning"]:
            warnings.simplefilter("default")
        # tfig.show()

    # Over
    W.log(3, '_' * 50 + "\n",
          threading.currentThread().getName(),
          'Exiting' + 20 * '-' + "\n")

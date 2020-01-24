import numpy as np

from abism.back import ImageFunction as IF
from abism.back.fit_helper import leastsqFit
import abism.back.fit_template_function as BF
from abism.back.image import ImageInfo, get_array_stat


from abism.util import log, get_verbose, get_root, get_state, EA
import abism.front.util_front as G
import abism.back.util_back as W


###############
# PICK ONE
###############



def PsfFit(grid, center=(0, 0), max=1, full_answer=True):
    """full_answer get the photometry and the background
    Clean me and the rest will follow
    """
    # In enhanced fit type
    fit_type = get_state().fit_type
    fit_type = enhance_fit_type(fit_type)

    # In center and bound
    (x0, y0), (rx1, rx2, ry1, ry2) = center, list(map(int, W.r))
    log(3, "PsfFit: ", rx1, rx2, ry1, ry2, 'center :', center)

    # Get working grid
    my_max = max
    X, Y = np.arange(int(rx1), int(rx2)+1), np.arange(int(ry1), int(ry2)+1)
    y, x = np.meshgrid(Y, X)        # We have to inverse because of matrix way
    IX = grid[rx1:rx2+1, ry1:ry2+1]  # the cutted image

    # Mask bad pixel (TODO look at that)
    IX, mIX = IF.FindBadPixel(IX)
    eIX = (IX-mIX).std() * np.ones(IX.shape)

    # Get fwhm
    my_fwhm = IF.FWHM(grid, center)


    # FIRST Geuss
    doNotFit = []
    if get_state().noise_type == 'None' or get_state().noise_type == 'manual':
        doNotFit.append('background')

    local_median = np.median(grid[int(x0)-1:int(x0)+2, int(y0)-1: int(y0+2)])

    suposed_param = {
        'center_x': x0,
        'center_y': y0,
        'spread_x': 0.83 * (my_fwhm),
        'intensity': my_max,
        'background': 0
    }

    fit_bounds = {
        "center_x": [x0 - 10, x0 + 10],
        "center_y": [y0 - 10, y0 + 10],
        "spread_x": [-0.1, None],
        "spread_y": [-0.1, None],
        # "exponent" :[1.2, 6 ],
        "background": [None, my_max],
        "instensity": [local_median, 2.3 * my_max - local_median],

             }

    ############
    #  FIT
    #############

    verbose = get_verbose() > 1

    if (fit_type == "Gaussian2D"):
        tmp = {"spread_y": suposed_param["spread_x"], "theta": 0.1}
        suposed_param.update(tmp)

    elif(fit_type == 'Gaussian'):
        pass

    elif (fit_type == 'Moffat'):  # 1.5 = /np.sqrt(1/2**(-1/b)-1)
        suposed_param.update({'spread_x': 1.5*my_fwhm, 'exponent': 2})

    elif (fit_type == "Moffat2D"):    # 0.83 = sqrt(ln(2))
        tmp = {
            "spread_y": suposed_param["spread_x"], "theta": 0.1, "exponent": 2}
        suposed_param.update(tmp)

    elif (fit_type == 'Bessel1'):
        pass

    elif (fit_type == "Bessel12D"):    # 0.83 = sqrt(ln(2))
        tmp = {"spread_y": suposed_param["spread_x"], "theta": 0.1}
        suposed_param.update(tmp)

    # we consider 2D or not, same_center or not
    elif ("Gaussian_hole" in fit_type):
        suposed_param.update({'center_x_hole': x0, 'center_y_hole': y0, 'spread_x_hole': 0.83*(
            my_fwhm)/2, 'spread_y_hole': 0.83*my_fwhm/2, 'intensity_hole': 0, 'theta': 0.1, 'theta_hole': 0.1})
        if not ("2D" in fit_type):
            suposed_param["2D"] = 0
            doNotFit.append("theta")
            doNotFit.append("theta_hole")
            doNotFit.append("spread_y")
            doNotFit.append("spread_y_hole")
        else:
            suposed_param["2D"] = 1
        if ("same_center" in fit_type):
            suposed_param["same_center"] = 1
            doNotFit.append("center_x_hole")
            doNotFit.append("center_y_hole")
        doNotFit.append("2D")
        doNotFit.append("same_center")

    # ACTUAL FIT
    if fit_type != "None":
        res = leastsqFit(
            vars(BF)[fit_type], (x, y), suposed_param, IX,
            err=eIX, doNotFit=doNotFit,
            bounds=fit_bounds, verbose=verbose)
    else:
        # Not fit
        restmp = {
            'center_x': x0, 'center_y': y0,
            'intensity': my_max, "r99x": 5*my_fwhm, "r99y": 5*my_fwhm}
        res = (restmp, 0, 0, IX, 0)


    # Update stuff ToRead
    tmp = {}
    tmp.update(res[0])
    res[0]["fit_dic"] = tmp

    ######
    # DICTIONARY , backup and star improving
    do_improve = not get_state().b_aniso and not get_state().fit_type == 'None'
    if do_improve:
        try:
            res[0]["spread_y"], res[0]["spread_x"] = res[0]["spread"], res[0]["spread"]
            res[1]["spread_y"], res[1]["spread_x"] = res[1]["spread"], res[1]["spread"]
        except:
            res[0]["spread_y"], res[0]["spread_x"] = res[0]["spread_x"], res[0]["spread_x"]
            res[1]["spread_y"], res[1]["spread_x"] = res[1]["spread_x"], res[1]["spread_x"]

    #############
    # FWHM, and PHOT < from fit
    res[0].update(IF.FwhmFromFit(res[0],  fit_type))

    # UPDATE R99X
    (r99x, r99y), (r99u, r99v) = IF.EnergyRadius(
        grid, fit_type, dic=res[0])
    res[0]["number_count"] = r99x * r99y
    res[0]["r99x"], res[0]["r99y"] = r99x, r99y
    res[0]["r99u"], res[0]["r99v"] = r99u, r99v

    return res


def Photometry(grid, background):
    """Make photometry of region
    In: center, r99
        Only one reading variable photometric type
        background
    Returns: photometry, total, number_count
             1. total phtotometric adu (backgound subtracted)
             Other. to estimate error
    Note Background must be called before
    """
    photometry = total = number_count = 0

    r99x, r99y = W.strehl['r99x'], W.strehl['r99y']
    r99u, r99v = W.strehl['r99u'], W.strehl['r99v']
    theta = W.strehl.get('theta', 0)

    x0, y0 = W.strehl['center_x'], W.strehl['center_y']
    ax1, ax2 = int(x0-r99x), int(x0+r99x)
    ay1, ay2 = int(y0-r99y), int(y0+r99y)

    # FIT
    if get_state().phot_type == 'fit':
        W.strehl["my_photometry"] = W.strehl["photometry_fit"]
        log(3, "doing fit  phot in ImageFunction.py ")

    # Rectangle apperture
    elif get_state().phot_type == 'encircled_energy':
        log(3, 'Photometry <- encircled energy (i.e. rectangle)')
        total = np.sum(grid[ax1:ax2, ay1:ay2])
        number_count = 4 * r99x * r99y
        photometry = total - number_count * background

    # Elliptical apperture
    elif get_state().phot_type == 'elliptical_aperture':
        log(3, 'Photometry <- elliptical aperture')
        ellipse_dic = {"center_x": x0, "center_y": y0,
                       "ru": r99u, "rv": r99v, "theta": theta}
        bol = IF.EllipticalAperture(grid, dic=ellipse_dic)["bol"]
        image_elliptic = grid[bol]

        stat = get_array_stat(image_elliptic)
        number_count = stat.number_count
        total = stat.sum
        photometry = total  - number_count * background

    # MANUAL
    elif get_state().phot_type == 'manual':
        stat = get_root().image.RectanglePhot(W.r)
        total = stat.sum
        number_count = stat.number_count
        photometry = total  - number_count * background


    return photometry, total, number_count


def Background(grid):
    # Log
    background_type = get_state().noise_type
    log(3, 'Getting Background with type', background_type)

    res = 0

    # BAckground and rms
    dic = W.strehl
    r = W.r

    # IN RECT
    if get_state().noise_type == 'in_rectangle':  # change noise  from fit
        dic['my_background'] = back / back_count
        rms = 0.
        for i in listrms:
            rms += (i-dic['my_background'])**2
        rms = np.sqrt(rms/(len(listrms)-1))
        dic['rms'] = rms

    # 8 RECTS
    elif get_state().noise_type == '8rects':
        xtmp, ytmp = dic['center_x'], dic['center_y']
        r99x, r99y = dic["r99x"], dic["r99y"]
        restmp = IF.EightRectangleNoise(
            grid, (xtmp-r99x, xtmp+r99x, ytmp-r99y, ytmp+r99y))
        dic['my_background'], dic['rms'] = restmp["background"], restmp['rms']
        log(3, "ImageFunction.py : Background, I am in 8 rects ")

    # MANUAL
    elif get_state().noise_type == "manual":
        dic["my_background"] = get_state().i_background
        dic["rms"] = 0

    # FIT
    elif get_state().noise_type == 'fit':
        if get_state().fit_type == "None":
            log(0, "\n\n Warning, cannot estimate background with fit if fit type = None, return to Annnulus background")
            param = param.copy()
            param.update({"noise": "annulus"})
            return Background(get_root().image.im0, param=param)
        try:
            dic['rms'] = W.psf_fit[1]['background']
        except:
            dic['rms'] = ["No_in_fit"]
        dic['my_background'] = dic["background"]

    # NONE
    elif get_state().noise_type == 'None':
        dic['my_background'] = dic['my_background'] = 0
        # dic['rms'] = 0

    # ELLIPTICAL ANNULUS
    elif get_state().noise_type == "elliptical_annulus":
        W.ell_inner_ratio, W.ell_outer_ratio = 1.3, 1.6
        rui, rvi = 1.3 * W.strehl["r99u"], 1.3 * W.strehl["r99v"]
        ruo, rvo = 1.6 * W.strehl["r99u"], 1.6 * W.strehl["r99v"]

        # CUT
        myrad = max(ruo, rvo) + 2  # In case
        ax1 = int(W.strehl["center_x"] - myrad)
        ax2 = int(W.strehl["center_x"] + myrad)
        ay1 = int(W.strehl["center_y"] - myrad)
        ay2 = int(W.strehl["center_y"] + myrad)
        image_cut = get_root().image.im0[ax1: ax2, ay1: ay2]

        bol_i = IF.EllipticalAperture(
            image_cut, dic={"center_x": myrad, "center_y": myrad, "ru": rui,
                            "rv": rvi, "theta": W.strehl["theta"]})["bol"]

        bol_o = IF.EllipticalAperture(
            image_cut, dic={"center_x": myrad, "center_y": myrad, "ru": ruo,
                            "rv": rvo, "theta": W.strehl["theta"]})["bol"]

        bol_a = bol_o ^ bol_i

        iminfo_cut = ImageInfo(image_cut[bol_a])
        tmp = iminfo_cut.sky()
        dic['rms'] = tmp["rms"]
        dic['my_background'] = tmp["mean"]

    else:
        dic['rms'] = -99
        dic['my_background'] = -99

    return dic

    ###############
    # BINARY
    ###############


def BinaryPsf(grid, search=False):  # slowlyer
    """search = True means we search the maximum """
    fit_type = get_state().fit_type
    fit_type = enhance_fit_type(fit_type)
    ########
    # " FIRST GUESS
    max0 = G.star1
    max1 = G.star2

    # distance between two pooints
    star_distance = np.sqrt((max0[0]-max1[0])**2 + (max0[1]-max1[1])**2)
    my_center = [(max0[0]+max1[0])/2, (max0[1]+max1[1])/2]
    dist0 = min(IF.FWHM(grid, max0), star_distance / 2)
    dist1 = min(IF.FWHM(grid, max1), star_distance / 2)

    ###########
    # make the bounds
    bd_x0 = (max0[0] - star_distance/2, max0[0] + star_distance/2)
    bd_y0 = (max0[1] - star_distance/2, max0[1] + star_distance/2)

    bd_x1 = (max1[0] - star_distance/2, max1[0] + star_distance/2)
    bd_y1 = (max1[1] - star_distance/2, max1[1] + star_distance/2)

    ########
    # DEFINE fitting space
    fit_range = star_distance + 5 * max(dist0, dist1)  # range of the fit
    rx1, rx2 = int(my_center[0] - fit_range /
                   2),  int(my_center[0] + fit_range/2)
    ry1, ry2 = int(my_center[1] - fit_range /
                   2),  int(my_center[1] + fit_range/2)

    rx1, rx2, ry1, ry2 = IF.Order4((rx1, rx2, ry1, ry2), grid=get_root().image.im0)
    log(3, "----->IF.BinaryPSF :", "The fit is done between points ",
          (rx1, ry1), " and ", (rx2, ry2), "with fit", fit_type)
    X, Y = np.arange(int(rx1), int(rx2)+1), np.arange(int(ry1), int(ry2)+1)
    y, x = np.meshgrid(Y, X)
    IX = grid[int(rx1):int(rx2+1), int(ry1):int(ry2+1)]
    IX, mIX = IF.FindBadPixel(IX)  # ,r=r)
    # the error
    eIX = (IX-mIX).std()
    eIX *= np.ones(IX.shape)
    log(3, "Binary shapes :", X.shape, Y.shape, IX.shape, eIX.shape)

    ###################
    ## Supposed params and bounds #
    ###################
    W.suposed_param = {'x0': max0[0], 'x1': max1[0], 'y0': max0[1], 'y1': max1[1],
                       'spread_x0': 0.83*(dist0), 'spread_x1': 0.83*dist1,
                       'spread_y0': 0.83*(dist0), 'spread_y1': 0.83*dist1,
                       'intensity0': grid[int(max0[0])][int(max0[1])],
                       'intensity1': grid[int(max1[0])][int(max1[1])],
                       'background': 0, "theta": 1}

    James = {
        # 'x0':bd_x0,
        # 'x1':bd_x1,
        # 'y0':bd_y0,
        # 'y1':bd_y1,
        'spread_x0': (-0.1, None),
        'spread_x1': (-0.1, None),
        'spread_y0': (-0.1, None),
        'spread_y1': (-0.1, None),
        'intensity0': (-0.1, None),
        'intensity1': (-0.1, None),
        'background': (0, None),
        "theta": (-0.1, 3.24)}  # becasue James Bound hahahah, These are the fitting limits of the varaibles . WARNING    we put the intensity positive becasue in a binary fit situation you know.... who knows

    ###########
    # DO NOT FIT, dic_for_fit
    if (not "Gaussian" in fit_type) and (not "Moffat" in fit_type):
        log(0, "WARNING : There is no bessel, None, and Gaussian hole fit "
              "type for binary fi, fit type is set to gaussian")
        fit_type = "Gaussian"

    if "Moffat" in fit_type:
        W.suposed_param['b0'], W.suposed_param['b1'] = 1.8, 1.8
        if not '2D' in fit_type:
            doNotFit.append("b1")
        James['b0'] = (1, 10)
        James['b1'] = (1, 10)

    doNotFit = []
    dic_for_fit = {
        "same_psf": get_state().b_same_psf,
        "aniso": get_state().b_aniso,
    }

    if get_state().b_same_psf:
        doNotFit.append("spread_x1")
        doNotFit.append("spread_y1")
        if not "2D" in fit_type:
            doNotFit.append("spread_y0")
            doNotFit.append("theta")
        if "Moffat" in fit_type:
            doNotFit.append("b1")
    else:  # not same psf
        if not "2D" in fit_type:
            doNotFit.append("spread_y0")
            doNotFit.append("spread_y1")
            doNotFit.append("theta")

    ##########
    # print()
    log(3, "Binary FiT, supposed parameters : ", W.suposed_param)
    log(3, "fit type is : ", fit_type)
    log(3, "anisoplanetism=" + str(bool(dic_for_fit["aniso"])),
          "same_psf="+str(bool(dic_for_fit["same_psf"])))

    #####################
    # FIT FIT  ahora si que si
    res = leastsqFit(
        lambda x, y: vars(BF)[fit_type.replace(
            "2D", "")+"2pt"](x, y, dic=dic_for_fit),
        (x, y), W.suposed_param, IX,
        err=eIX, doNotFit=doNotFit,
        bounds=James,
        verbose=get_verbose() > 1,
    )

    ##############
    # Restore not fitted variables
    def Restore(list, to_change, reference):
        list[0][to_change] = list[0][reference]
        list[1][to_change] = list[1][reference]
        return list

    if get_state().b_same_psf:
        res = Restore(res, "spread_x1", "spread_x0")
        res = Restore(res, "spread_y1", "spread_y0")
        if not "2D" in fit_type:
            res = Restore(res, "spread_y0", "spread_x0")
        if "Moffat" in fit_type:
            res = Restore(res, "b1", "b0")
    else:  # not same psf
        if not "2D" in fit_type:
            res = Restore(res, "spread_y0", "spread_x0")
            res = Restore(res, "spread_y1", "spread_x1")

    # BACKKUP DIC
    tmp = {}
    tmp.update(res[0])
    res[0]["fit_dic"] = tmp

    # FWHM , Photo < from fit
    dic_copy0 = res[0].copy()
    dic_copy1 = res[0].copy()
    for key in res[0].keys():
        if "0" in key:
            dic_copy0[key.replace("0", "")] = dic_copy0[key]
        elif "1" in key:
            dic_copy1[key.replace("1", "")] = dic_copy1[key]
        # nevermind the center x0 and x1
    try:
        dic_copy0["exponent"] = dic_copy0["b0"]
    except:
        pass
    try:
        dic_copy1["exponent"] = dic_copy1["b1"]
    except:
        pass

    tmp = IF.FwhmFromFit(dic_copy0, fit_type)
    res[0].update({"fwhm_x0": tmp["fwhm_x"],
                   "fwhm_y0": tmp["fwhm_y"],
                   "photometry_fit0": tmp["photometry_fit"],
                   })
    tmp = IF.FwhmFromFit(dic_copy1, fit_type)
    res[0].update({"fwhm_x1": tmp["fwhm_x"],
                   "fwhm_y1": tmp["fwhm_y"],
                   "photometry_fit1": tmp["photometry_fit"]
                   })

    if False:
        if "Gaussian" in fit_type:
            if "2D" in fit_type:
                photometry0 = np.pi*res[0]['intensity0'] * \
                    res[0]['spread_x0']*res[0]['spread_y0']
                photometry1 = np.pi*res[0]['intensity1'] * \
                    res[0]['spread_x1']*res[0]['spread_y1']
            else:
                photometry0 = np.pi*res[0]['intensity0']*res[0]['spread_x0']**2
                photometry1 = np.pi*res[0]['intensity1']*res[0]['spread_x1']**2

        if "Moffat" in fit_type:
            if "2D" in fit_type:
                photometry0 = np.pi * \
                    res[0]['intensity0']*res[0]['spread_x0'] * \
                    res[0]['spread_y0']/(res[0]['b0']-1)
                photometry1 = np.pi * \
                    res[0]['intensity1']*res[0]['spread_x1'] * \
                    res[0]['spread_y1']/(res[0]['b1']-1)
            else:
                photometry0 = np.pi*res[0]['intensity0'] * \
                    res[0]['spread_x0']**2/(res[0]['b0']-1)
                photometry1 = np.pi*res[0]['intensity1'] * \
                    res[0]['spread_x1']**2/(res[0]['b1']-1)

        if "hole" in fit_type:
            photometry -= np.pi*res[0]['intensity_hole'] * \
                res[0]['spread_x_hole']*res[0]['spread_y_hole']

        res[0]['center_x'], res[0]['center_y'] = my_center[0], my_center[1]  # to draw
        res[0]["photometry0"], res[0]["photometry1"] = photometry0, photometry1

    res[0]["my_photometry0"], res[0]["my_photometry1"] = res[0]["photometry_fit0"], res[0]["photometry_fit1"]

    return res


def TightBinaryPsf(grid, search=False):  # slowlyer
    """search = True means we search the maximum """

    fit_type = get_state().fit_type
    fit_type = enhance_fit_type(fit_type)

    ########
    # " FIRST GUESS
    max0 = G.star1
    max1 = G.star2

    # distance between two pooints
    star_distance = np.sqrt((max0[0]-max1[0])**2 + (max0[1]-max1[1])**2)
    my_center = [(max0[0]+max1[0])/2, (max0[1]+max1[1])/2]
    dist0 = min(IF.FWHM(grid, max0), star_distance / 2)
    dist1 = min(IF.FWHM(grid, max1), star_distance / 2)

    ###########
    # make limits od fit
    bd_x0 = (max0[0] - star_distance/2, max0[0] + star_distance/2)
    bd_y0 = (max0[1] - star_distance/2, max0[1] + star_distance/2)

    bd_x1 = (max1[0] - star_distance/2, max1[0] + star_distance/2)
    bd_y1 = (max1[1] - star_distance/2, max1[1] + star_distance/2)

    ########
    # DEFINE fitting space
    fit_range = star_distance + 5 * max(dist0, dist1)  # range of the fit
    # the error
    rx1 = int(my_center[0] - fit_range / 2)
    rx2 = int(my_center[0] + fit_range / 2)
    ry1 = int(my_center[1] + fit_range / 2)
    ry2 = int(my_center[1] - fit_range / 2)
    log(3, "----->IF.BinaryPSF :",
          "The fit is done between points ",
          (rx1, ry1), " and ", (rx2, ry2),
          "with fit", fit_type)
    X, Y = np.arange(int(rx1), int(rx2)+1), np.arange(int(ry1), int(ry2)+1)
    y, x = np.meshgrid(Y, X)
    IX = grid[rx1:rx2+1, ry1:ry2+1]
    IX, mIX = IF.FindBadPixel(IX)  # ,r=r)
    eIX = (IX-mIX).std()
    eIX *= np.ones(IX.shape)

    ###################
    ## Supposed params and bounds #
    ###################
    W.suposed_param = {'x0': max0[0], 'x1': max1[0], 'y0': max0[1], 'y1': max1[1],
                       'spread_x0': 0.83*(dist0), 'spread_x1': 0.83*dist1,
                       'spread_y0': 0.83*(dist0), 'spread_y1': 0.83*dist1,
                       'intensity0': grid[max0[0]][max0[1]], 'intensity1': grid[max1[0]][max1[1]],
                       'background': 0, "theta": 1}

    cut1 = get_root().image.im0[G.star1[0]-2:G.star1[0]+2, G.star1[1]-2:G.star1[1]+2]
    min1 = np.median(cut1)
    max1 = np.max(cut1)
    max1 = 2*max1 - min1

    cut2 = get_root().image.im0[G.star2[0]-2:G.star2[0]+2, G.star2[1]-2:G.star2[1]+2]
    min2 = np.median(cut2)
    max2 = np.max(cut2)
    max2 = 2*max2 - min2
    James = {
        'x0': (G.star1[0]-2, G.star1[0]+2),
        'x1': (G.star2[0]-2, G.star2[0]+2),
        'y0': (G.star1[1]-2, G.star1[1]+2),
        'y1': (G.star2[1]-2, G.star2[1]+2),
        'spread_x0': (-0.1, None),
        'spread_x1': (-0.1, None),
        'spread_y0': (-0.1, None),
        'spread_y1': (-0.1, None),
        'intensity0': (min1, max1),
        'intensity1': (min2, max2),
        'background': (None, None),
        "theta": (-0.1, 3.24)}  # becasue James Bound hahahah, These are the fitting limits of the varaibles . WARNING    we put the intensity positive becasue in a binary fit situation you know.... who knows

    ###########
    # DO NOT FIT, dic_for_fit
    if "Bessel" in fit_type:
        log(0, "WARNING : no bessel 2pt fit type now,fit type is set to gaussian")
        fit_type = "Gaussian"

    if "Moffat" in fit_type:
        W.suposed_param['b0'], W.suposed_param['b1'] = 1.8, 1.8
        James['b0'] = (1, 3)
        James['b1'] = (1, 3)

    doNotFit = []
    dic_for_fit = {"same_psf": get_state().b_same_psf, "aniso": 0}
    if "2D" in fit_type:
        dic_for_fit["aniso"] = 1

    if get_state().b_same_psf:
        doNotFit.append("spread_x1")
        doNotFit.append("spread_y1")
        if not get_state().b_aniso:
            doNotFit.append("spread_y0")
            doNotFit.append("theta")
        if "Moffat" in fit_type:
            doNotFit.append("b1")
    else:  # not same psf
        if not get_state().b_aniso:
            doNotFit.append("spread_y0")
            doNotFit.append("spread_y1")
            doNotFit.append("theta")

    ##########
    # print()
    log(3, "Binary FiT, supposed parameters : ", W.suposed_param)
    log(3, "fit type is : ", fit_type)
    log(3, "anisoplanetism=" +
              str(bool(dic_for_fit["aniso"])), "same_psf="+str(bool(dic_for_fit["same_psf"])))

    #####################
    # FIT FIT  ahora si que si
    res = leastsqFit(
        lambda x, y: vars(BF)[fit_type.replace(
            "2D", "")+"2pt"](x, y, dic=dic_for_fit),
        (x, y), W.suposed_param, IX,
        err=eIX, doNotFit=doNotFit,
        bounds=James,
        verbose=get_verbose() > 1,
    )

    ##############
    # Restore not fitted variables
    def Restore(list, to_change, reference):
        list[0][to_change] = list[0][reference]
        list[1][to_change] = list[1][reference]
        return list

    if get_state().b_same_psf:
        res = Restore(res, "spread_x1", "spread_x0")
        res = Restore(res, "spread_y1", "spread_y0")
        if not "2D" in fit_type:
            res = Restore(res, "spread_y0", "spread_x0")
        if "Moffat" in fit_type:
            res = Restore(res, "b1", "b0")
    else:  # not same psf
        if not "2D" in fit_type:
            res = Restore(res, "spread_y0", "spread_x0")
            res = Restore(res, "spread_y1", "spread_x1")

    # BACKKUP DIC
    tmp = {}
    tmp.update(res[0])
    res[0]["fit_dic"] = tmp

    # FWHM , Photo < from fit
    dic_copy0 = res[0].copy()
    dic_copy1 = res[0].copy()
    for key in res[0].keys():
        if "0" in key:
            dic_copy0[key.replace("0", "")] = dic_copy0[key]
        elif "1" in key:
            dic_copy1[key.replace("1", "")] = dic_copy1[key]
        # nevermind the center x0 and x1
    dic_copy0["exponent"] = dic_copy0["b0"]
    dic_copy1["exponent"] = dic_copy1["b1"]

    tmp = IF.FwhmFromFit(dic_copy0, fit_type)
    res[0].update({"fwhm_x0": tmp["fwhm_x"],
                   "fwhm_y0": tmp["fwhm_y"],
                   "photometry_fit0": tmp["photometry_fit"],
                   })
    tmp = IF.FwhmFromFit(dic_copy1, fit_type)
    res[0].update({"fwhm_x1": tmp["fwhm_x"],
                   "fwhm_y1": tmp["fwhm_y"],
                   "photometry_fit1": tmp["photometry_fit"]
                   })

    if False:
        if "Gaussian" in fit_type:
            if "2D" in fit_type:
                photometry0 = np.pi*res[0]['intensity0'] * \
                    res[0]['spread_x0']*res[0]['spread_y0']
                photometry1 = np.pi*res[0]['intensity1'] * \
                    res[0]['spread_x1']*res[0]['spread_y1']
            else:
                photometry0 = np.pi*res[0]['intensity0']*res[0]['spread_x0']**2
                photometry1 = np.pi*res[0]['intensity1']*res[0]['spread_x1']**2

        if "Moffat" in fit_type:
            if "2D" in fit_type:
                photometry0 = np.pi * \
                    res[0]['intensity0']*res[0]['spread_x0'] * \
                    res[0]['spread_y0']/(res[0]['b0']-1)
                photometry1 = np.pi * \
                    res[0]['intensity1']*res[0]['spread_x1'] * \
                    res[0]['spread_y1']/(res[0]['b1']-1)
            else:
                photometry0 = np.pi*res[0]['intensity0'] * \
                    res[0]['spread_x0']**2/(res[0]['b0']-1)
                photometry1 = np.pi*res[0]['intensity1'] * \
                    res[0]['spread_x1']**2/(res[0]['b1']-1)

        if "hole" in fit_type:
            photometry -= np.pi*res[0]['intensity_hole'] * \
                res[0]['spread_x_hole']*res[0]['spread_y_hole']

        res[0]['center_x'], res[0]['center_y'] = my_center[0], my_center[1]  # to draw
        res[0]["photometry0"], res[0]["photometry1"] = photometry0, photometry1

    res[0]["my_photometry0"], res[0]["my_photometry1"] = res[0]["photometry_fit0"], res[0]["photometry_fit1"]

    return res

    ################
    # ELLIPSE CANVAS
    ###############


def EllipseEventBack():
    """Return: background from ellipse <int(adu)>"""
    obj = G.ellipse
    rui, rvi = obj.ru, obj.rv     # inner annulus
    ruo, rvo = 2*obj.ru, 2 * obj.rv  # outer annulus

    ell_i = IF.EllipticalAperture(
        get_root().image.im0,
        dic={"center_x": obj.x0, "center_y": obj.y0, "ru": rui,
             "rv": rvi, "theta": obj.theta})  # inner

    ell_o = IF.EllipticalAperture(
        get_root().image.im0,
        dic={"center_x": obj.x0, "center_y": obj.y0, "ru": ruo,
             "rv": rvo, "theta": obj.theta})  # outter

    # annulus  inside out but not inside in
    bol_a = ell_o["bol"] ^ ell_i["bol"]

    image_cut = get_root().im0[bol_a]
    stat = get_array_stat(image_cut)

    stat["mean"]


def EllipseEventPhot():
    """Elliptical phot
    Returns: photometry, total, number_count
    """
    obj = G.ellipse

    ###########
    # CAlculate Ellipse stats (phot) update phot
    dic = {"center_x": obj.x0, "center_y": obj.y0,
           "ru": obj.ru, "rv": obj.rv, "theta": obj.theta}
    ellipse_stat = IF.EllipticalAperture(
        obj.array, dic=dic, full_answer=True)

    number_count, total = ellipse_stat['sum'], ellipse_stat['number_count']
    photometry = total - get_state().get_answer(EA.BACKGROUND)

    # SAve photo
    get_state().add_answer(EA.PHOTOMETRY, photometry)
    return photometry, total, number_count


def EllipseEventMax():  # receive EllipseEvent
    obj = G.ellipse

    rad = max(obj.ru, obj.rv)
    r = (obj.x0-rad, obj.x0+rad+1, obj.y0-rad, obj.y0+rad+1)
    local_max = IF.LocalMax(get_root().image.im0, r=r)  # With bad pixel filter

    ######
    # Update
    W.strehl.update({"center_x": local_max[0],
                     "center_y": local_max[1],
                     "intensity": local_max[2],
                     })
    return

    ###############
    # ANNULUS CANVAS
    #################


def AnnulusEventPhot(obj):  # Called by Gui/Event...py  Event object
    res = {}

    center_x = obj.x0  # from image to array but coord in array type
    center_y = obj.y0
    theta = obj.theta

    if obj.outter_u < obj.inner_u:  # put outter radius after inner
        tmp = obj.inner_u
        obj.inner_u = obj.outter_u
        obj.outter_u = tmp

    # DEIFINE THE Bollean of being inside the elliptical aperture
    ru = obj.ru
    rv = obj.ru * obj.rapport
    bol_e = EllipticalAperture(obj.array, dic={"center_x": center_x, "center_y": center_y, "ru": ru, "rv": rv, "theta": theta})[
        "bol"]  # ellipse , photomretry

    ru, rv = obj.inner_u, obj.inner_u*obj.rapport
    bol_i = EllipticalAperture(obj.array, dic={
                               "center_x": center_x, "center_y": center_y, "ru": ru, "rv": rv, "theta": theta})["bol"]  # inner

    ru, rv = obj.outter_u, obj.outter_u*obj.rapport
    bol_o = EllipticalAperture(obj.array, dic={
                               "center_x": center_x, "center_y": center_y, "ru": ru, "rv": rv, "theta": theta})["bol"]  # outter

    bol_a = bol_o ^ (bol_i)  # annulus  inside out but not inside in
    phot, number_count = np.sum(obj.array[bol_e]), len(obj.array[bol_e])
    back, number_back = np.sum(obj.array[bol_a]), len(obj.array[bol_a])

    # PHOT and back
    iminfo_cut = ImageInfo(obj.array[bol_a])
    res["background_dic"] = iminfo_cut.sky()
    res["my_background"] = res["background_dic"]["mean"]
    res["phot"] = np.sum(obj.array[bol_e])
    res["my_photometry"] = res["phot"] - \
        len(obj.array[bol_e])*res["my_background"]

    log(2, "phot1 :", res["phot"])
    log(2, "phot2 :", res["my_photometry"])
    log(2, "back :", res["my_background"], "\n")


# TODO refactor all that in the discriminator
def enhance_fit_type(name):  # strange but works
    fit_type = name
    try:
        if get_state().b_aniso and not '2D' in fit_type:
            fit_type += '2D'
        elif not get_state().b_aniso:
            fit_type = fit_type.replace('2D', '')
    except BaseException:
        if fit_type.find('2D') == -1:
            fit_type += '2D'
    if not fit_type.find('None') == -1:
        fit_type = 'None'

    log(0, 'Fit Type = ' + fit_type)
    return fit_type



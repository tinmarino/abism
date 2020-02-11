"""
    Helper to make a 2D function (i.e Gaussian) fit an array
IDEA: fit Y = F(X,A) where A is a dictionnary describing the
parameters of the function.

note that the items in the dictionnary should all be scalar!
"""
from functools import reduce

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize

from abism.back.leastsqbound import leastsqbound

from abism.util import log, get_state


def polyN(x, params):
    """
    example of a function which parameters are defined by a
    dictionary: a polynomial function.

    In this particular case, params={'A0':1.0, 'A2':2.0} returns
    x->1+2*x**2. The coefficient do not have to start at 0 and do not
    need to be continuous. Actually, the way the function is written,
    it will accept any 'Ax' where x i a float.
    """
    res = 0
    for k in params:
        res += params[k]*np.array(x)**float(k[1:])
    return res


def radial2dgrid(radius, sample, center=[0, 0]):
    """Conver circle to grid"""
    x = np.linspace(-radius, radius, sample)+center[1]
    y = np.linspace(-radius, radius, sample)+center[0]
    xi1 = np.tile(x, sample)
    xx = xi1.reshape(sample, sample)
    yi1 = np.repeat(y, sample)
    yy = yi1.reshape(sample, sample)
    radgrid = np.sqrt(xx**2+yy**2)
    return xi1, yi1, radgrid


def fitFunc(pfit, pfitKeys, x, y, err=None, func=None,
            pfix=None, verbose=False):
    """
    interface to leastsq from scipy:
    - x,y,err are the data
    - pfit is a list of the paramters
    - pfitsKeys are the keys to build the dict
    pfit and pfix (optional) and combines the two
    in 'A', in order to call F(X,A)
    """
    # Stop it
    if get_state().b_is_timed_out:
        get_state().b_is_timed_out = False
        raise TimeoutError

    params = {}
    # build dic from parameters to fit and their values:
    for i, k in enumerate(pfitKeys):
        params[k] = pfit[i]
    # complete with the non fitted parameters:
    for k in pfix:
        params[k] = pfix[k]
    if err is None:
        err = np.ones(np.array(y).shape)
    # return residuals
    try:
        # assumes y is a numpy array
        y = np.array(y)
        res = ((func(x, params)-y)/err).flatten()
    except:
        # much slower: this time assumes y (and the result from func) is
        # a list of stuff, each convertible in np.array
        res = []
        tmp = func(x, params)
        for k in range(len(y)):
            df = (np.array(tmp[k])-np.array(y[k]))/np.array(err[k])
            try:
                res.extend(list(df))
            except:
                res.append(df)
        res = np.array(res)

    # Log
    l_chi = [1 if np.isscalar(i) else len(i) for i in y]
    chi2 = (res**2).sum()
    chi2 /= float(reduce(lambda x, y: x+y, l_chi)-len(pfit)+1)
    log(1, 'CHI2:', chi2)

    # Return
    return res


def leastsqFit(func, x, params, y, err=None, fitOnly=None,
               verbose=False, doNotFit=[], epsfcn=1e-7,
               ftol=1e-4, fullOuput=True, bounds={}):
    """
    - params is a Dict containing the first guess.

    - bounds = {"theta":[-0.1,3.24]} even if after it will be a list with same indexation as fitOnly

    - fits 'y +- err = func(x,params)'. errors are optionnal.

    - fitOnly is a LIST of keywords to fit. By default, it fits all
      parameters in 'params'. Alternatively, one can give a list of
      parameters not to be fitted, as 'doNotFit='

    - doNotFit has a similar purpose: for example if params={'a0':,
      'a1': 'b1':, 'b2':}, doNotFit=['a'] will result in fitting only
    the 'b1' and 'b2'. WARNING: if you name parameter 'A' and another one 'AA',
    you cannot use doNotFit to exclude only 'A' since 'AA' will be excluded as
    well...

    returns bestparam, uncertainties, chi2_reduced, func(x, bestparam)
    """
    # fit all parameters by default
    if fitOnly is None:
        if len(doNotFit) > 0:
            fitOnly = [x for x in params.keys() if x not in doNotFit]
        else:
            fitOnly = [*params]

    # build fitted paramete rs vector:
    pfit = [params[k] for k in fitOnly]

    # built fixed parameters dict:
    pfix = {}
    for k in params.keys():
        if k not in fitOnly:
            pfix[k] = params[k]

    log(1, '[dpfit] FITTED parameters:', fitOnly)

    # NO BOUNDS
    if bounds == {}:
        # actual fit
        plsq, cov, info, mesg, ier = \
            scipy.optimize.leastsq(fitFunc, pfit,
                                   args=(fitOnly, x, y, err,
                                         func, pfix, verbose),
                                   full_output=True, epsfcn=epsfcn, ftol=ftol)

    # WITH BOUNDS
    else:  # including bounds != {}
        bounds_to_fit = [[None, None]]*len(fitOnly)  # now it is a list
        for key in bounds.keys():
            if key in fitOnly:  # becauser could be in notToFit
                bounds_to_fit[fitOnly.index(key)] = bounds[key]

        plsq, cov, info, mesg, ier = \
            leastsqbound(fitFunc, pfit, bounds=bounds_to_fit,
                         args=(fitOnly, x, y, err, func, pfix, verbose),
                         full_output=True, epsfcn=epsfcn, ftol=ftol)

    # best fit -> agregate to pfix
    for i, k in enumerate(fitOnly):
        pfix[k] = plsq[i]

    # reduced chi2
    model = func(x, pfix)
    chi2 = (np.array(fitFunc(plsq, fitOnly, x, y, err, func, pfix))**2).sum()
    reducedChi2 = chi2/float(reduce(lambda x, y: x+y,
                                    [1 if np.isscalar(i) else len(i) for i in y])-len(pfit)+1)

    # uncertainties:
    uncer = {}
    for k in pfix:
        if not k in fitOnly:
            uncer[k] = 0  # not fitted, uncertatinties to 0
        else:
            i = fitOnly.index(k)
            if cov is None:
                uncer[k] = -1
            else:
                uncer[k] = np.sqrt(np.abs(np.diag(cov)[i]*reducedChi2))

    if verbose:
        log(1, '-'*20)
        log(1, 'REDUCED CHI2=', reducedChi2)
        tmp = sorted([*pfix])
        for k in tmp:
            log(1, k, '=', pfix[k],)
            if uncer[k] != 0:
                log(1, '+/-', uncer[k])
            else:
                log(1, '')
    # result:
    return pfix, uncer, reducedChi2, model, {
        "reduced_chi2": reducedChi2, "cov": cov, "plsq": plsq, "pfit": pfit,
        "fitOnly": fitOnly, "bounds": bounds}


def sinusoid(x, params):

    res = params['C']+params['V']*np.sin(x+params['phi'])

    return res


def gaussian(x, params):

    res = params['C']+params['A'] * \
        np.exp(-(x-params['x0'])**2/params['sigma']**2)
    return res


def bessel1(x, params):
    from scipy.special import jn
    x -= params['x0']
    res = params['C']+params['A'] * \
        (2*jn(1, x/params['sigma'])*params['sigma']/x)**2
    return res


def tanhip(x, params):
    res = params['A']*np.tanh(params['B']*x)+params['C']
    return res


def gaussian2(xy, params):
    xt = xy[0]
    yt = xy[1]
    xp = (xt-params['x0'])*np.cos(params['theta']) - \
        (yt-params['y0'])*np.sin(params['theta'])
    yp = (xt-params['x0'])*np.sin(params['theta']) + \
        (yt-params['y0'])*np.cos(params['theta'])
    res = params['noise']+params['amplitude'] * \
        np.exp(-(xp**2/params['sigmax']**2+yp**2/params['sigmay']**2))
    return res

    #xt = x[0:x.shape[0]/2]
    #yt = x[x.shape[0]/2:]
    # le yt+params vient du fait que l'affichage y va du haut vers le bas
    #xp = (xt-params['x0'])*np.cos(params['theta'])-(yt+params['y0'])*np.sin(params['theta'])
    #yp = (xt-params['x0'])*np.sin(params['theta'])+(yt+params['y0'])*np.cos(params['theta'])
    #res = params['C']+params['A']*np.exp(-(xp**2/params['sigmax']**2+yp**2/params['sigmay']**2))
    # return res


def example():
    """
    very simple example
    """
    X = [0,   1,   2,   3]
    Y = [-0.1, 1.1, 4.1, 8.9]
    E = [0.1, 0.1, 0.1, 0.1]
    # best, unc, chi2, model =\
    #      leastsqFit(polyN, X,
    #                 {'A0':0., 'A1':0.,'A2':0.1},
    #                 Y, err=E, fitOnly=['A2', 'A0'])
    best, unc, chi2, model =\
        leastsqFit(polyN, X,
                   {'A0': 0., 'A1': 0., 'A2': 0.1},
                   Y, err=E, doNotFit=['A1'])
    log(1, 'CHI2=', chi2)
    for k in best.keys():
        log(1, k, '=', best[k],)
        if unc[k] > 0:
            log(1, '+/-', unc[k])
        else:
            log(1, '')
    log(1, 'Y=', Y)
    log(1, 'MODEL=', model)
    return


def example2():
    """ sinusoide """
    sample = 100
    x = np.linspace(0, 2*np.pi, sample)
    params = {'C': 0.2, 'V': 0.3, 'phi': 0.5*np.pi}
    y = sinusoid(x, params)+np.random.random(sample)*0.1-0.5
    erry = np.ones(sample)*0.05
    best, unc, chi2, model = leastsqFit(
        sinusoid, x, {'C': 0.1, 'V': 0.2, 'phi': 0.1*np.pi}, y, err=erry, verbose=True)
    plt.figure(1)
    ax1 = plt.subplot(111)
    ax1.plot(x, y)
    ax1.plot(x, model)
    for k in best.keys():
        print(k, '=', best[k],)
        if unc[k] > 0:
            print('+/-', unc[k])
        else:
            print('')


def example3():
    """ gaussian + strehl"""
    sample = 40
    x = np.linspace(-2, 2, sample)
    step = 0.08
    params = {'C': 0, 'A': 1, 'x0': 0, 'sigma': 0.27}
    y = bessel1(x, params)+0.1*np.random.random(sample)
    erry = np.ones(sample)*0.05
    #best, unc, chi2, model =leastsqFit(gaussian,x,{'C':0.2,'A':10.4,'x0':0.3,'sigma':0.7},y, err=erry,verbose=True)
    best, unc, chi2, model = leastsqFit(
        bessel1, x, {'C': 0, 'A': 0.6, 'x0': 0, 'sigma': 0.4}, y, err=erry, verbose=True)
    plt.figure(1)
    from scipy.special import jn
    def Be(x, B): return (2*jn(1, x/B)*B/x)**2 / B**2 * best['sigma']**2
    ax1 = plt.subplot(121)
    ax1.bar(x, (y-best['C'])/Be(0.001, 0.2), step, color='pink')
    ax1.plot(x, (model-best['C'])/Be(0.001, 0.2), color='black', linewidth=3)
    plt.ylim(-0.2, 1)
    plt.xlim(-1.5, 1.5)
    ax2 = plt.subplot(122)
    ax2.plot(x, Be(x, 0.2)/Be(0.001, 0.2))
    plt.xlim(-1.5, 1.5)
    plt.ylim(-0.2, 1)
    for k in best.keys():
        print(k, '=', best[k],)
        if unc[k] > 0:
            print('+/-', unc[k])
        else:
            print('')
    return model


def example4():
    sample = 100
    noiseamp = 0.5
    params = {'C': 0.5, 'A': 5.5, 'theta': 0.67*np.pi,
              'x0': 0.0, 'y0': -2.0, 'sigmax': 2.0, 'sigmay': 1.0}
    paramsguess = {'C': 0.3, 'A': 3.5, 'theta': 0.43*np.pi,
                   'x0': -1.0, 'y0': 0.0, 'sigmax': 1.0, 'sigmay': 3.0}
    x, y, grid = radial2dgrid(5.0, sample)
    xconc = np.concatenate((x, y))
    print('x', type(x), 'y', type(y), 'conc', type(xconc))
    ima = gaussian2(xconc, params)+np.random.random(sample *
                                                    sample)*noiseamp*params['A']
    errima = np.ones(sample*sample)*0.05
    fig1 = plt.figure(1)
    ax1 = plt.subplot(121)
    ax1.imshow(ima.reshape(sample, sample))
    # now the fitting
    best, unc, chi2, model = leastsqFit(
        gaussian2, xconc, paramsguess, ima, err=errima, verbose=True)
    print(best, unc, chi2, model)
    ax2 = plt.subplot(122)
    ax2.imshow(model.reshape(sample, sample))
# example4()


def example5():
    """ A*tanh(Bx)+C """
    sample = 100
    x = np.linspace(-2, 2, sample)
    params = {'A': 3, 'B': 10, 'C': 3}
    y = tanhip(x, params)+np.random.random(sample)
    erry = np.ones(sample)
    best, unc, chi2, model = leastsqFit(
        tanhip, x, {'A': 3, 'B': 0.9, 'C': 3}, y, err=erry, verbose=True)
    plt.figure(1)
    ax1 = plt.subplot(111)
    ax1.plot(x, y)
    ax1.plot(x, model)
    log(1, best)
    for k in best.keys():
        log(1, k, '=', best[k],)
        if unc[k] > 0:
            log(1, '+/-', unc[k])
        else:
            log(1, '')


def plot2dgaussian():
    sample = 50
    params = {'C': 0.5, 'A': 5.5, 'theta': 0.13*np.pi,
              'x0': 2.0, 'y0': -2.0, 'sigmax': 2.0, 'sigmay': 1.0}
    x, y, grid = radial2dgrid(5.0, sample)
    xconc = np.concatenate((x, y))
    ima = gaussian2(xconc, params)
    fig1 = plt.figure(1)
    ax1 = plt.subplot(121)

    ax1.imshow(ima.reshape(sample, sample))
# example4()

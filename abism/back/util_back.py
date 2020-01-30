"""
    TODO delete me
"""
from abism.util import log, get_state


class VoidClass:
    """ Placeholder of the most ugly container
    this is for the temporary variables to pass from one function to an other.
    Like W.tmp.lst... carrefull
    Clean  AnswerFrame
    """
tmp = VoidClass()

strehl = {}



# TODO refactor all that in the caller discriminator
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

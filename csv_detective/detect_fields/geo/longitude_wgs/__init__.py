PROPORTION = 0.9


def _is(val):
    '''Renvoie True si val peut etre une longitude'''
    try:
        val = float(val.replace(',', '.'))
        if int(val) == val:
            return False
        return val >= -180 and val <= 180
    except ValueError:
        return False
    except OverflowError:
        return False

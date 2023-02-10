PROPORTION = 0.9


def _is(val):
    '''Renvoie True si val peut etre une latitude'''
    try:
        val = float(val.replace(',', '.'))
        if int(val) == val:
            return False
        return val >= -90 and val <= 90
    except ValueError:
        return False
    except OverflowError:
        return False

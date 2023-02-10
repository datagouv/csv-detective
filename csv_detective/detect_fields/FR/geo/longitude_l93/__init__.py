PROPORTION = 0.9


def _is(val):
    '''Renvoie True si val peut etre une longitude en métropole'''
    try:
        val = float(val.replace(',', '.'))
        if int(val) == val:
            return False
        return val >= -357823 and val <= 1313633
    except ValueError:
        return False
    except OverflowError:
        return False

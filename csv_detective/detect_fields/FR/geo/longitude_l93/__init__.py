from csv_detective.detect_fields.other.float import _is as is_float

PROPORTION = 0.9


def _is(val):
    '''Renvoie True si val peut etre une longitude en métropole'''
    try:
        is_float(val) and float(val) >= -357823 and float(val) <= 1313633
    except ValueError:
        return False
    except OverflowError:
        return False

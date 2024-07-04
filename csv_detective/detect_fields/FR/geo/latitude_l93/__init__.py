from csv_detective.detect_fields.other.float import _is as is_float

PROPORTION = 0.9


def _is(val):
    '''Renvoie True si val peut etre une latitude en Lambert 93'''
    try:
        is_float(val) and float(val) >= 6037008 and float(val) <= 7230728
    except ValueError:
        return False
    except OverflowError:
        return False

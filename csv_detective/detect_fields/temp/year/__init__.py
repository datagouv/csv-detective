
PROPORTION = 1


def _is(val):
    '''Returns True if val can be a year'''
    try:
        val = int(val)
    except ValueError:
        return False
    if (1900 <= val) and (val <= 2100):
        return True
    else:
        return False

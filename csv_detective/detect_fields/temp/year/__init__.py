PROPORTION = 1


def _is(val):
    '''Returns True if val can be a year'''
    try:
        val = int(val)
    except ValueError:
        return False
    return (1800 <= val) and (val <= 2100)

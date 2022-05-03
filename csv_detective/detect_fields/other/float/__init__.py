PROPORTION = 1


def _is(val):
    '''Detects floats'''
    try:
        float(val.replace(' ', '').replace(',', '.'))
        return True
    except ValueError:
        return False


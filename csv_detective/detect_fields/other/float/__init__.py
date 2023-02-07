PROPORTION = 1


def _is(val):
    '''Detects floats'''
    try:
        if '_' in val:
            return False
        float(val.replace(' ', '').replace(',', '.'))
        return True
    except ValueError:
        return False

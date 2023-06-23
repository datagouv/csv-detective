PROPORTION = 1


def _is(val):
    '''Detects floats, assuming that tables will not have scientific
    notations (3e6) or "+" in the string. "-" is still accepted.'''
    try:
        if any([k in val for k in ['_', '+', 'e', 'E']]):
            return False
        float(val.replace(' ', '').replace(',', '.'))
        return True
    except ValueError:
        return False

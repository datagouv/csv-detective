PROPORTION = 1


def _is(val):
    '''Detects integers'''
    if any([v in val for v in ['.', '_', '+']]):
        return False
    try:
        int(val)
        return True
    except ValueError:
        return False

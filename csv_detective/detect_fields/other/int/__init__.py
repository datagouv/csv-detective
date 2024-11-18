PROPORTION = 1


def _is(val):
    '''Detects integers'''
    if (
        not isinstance(val, str)
        or any([v in val for v in ['.', '_', '+']])
        or (val.startswith('0') and len(val) > 1)
    ):
        return False
    try:
        int(val)
        return True
    except ValueError:
        return False

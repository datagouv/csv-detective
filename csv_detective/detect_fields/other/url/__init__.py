
PROPORTION = 1


def _is(val):
    '''Detects urls'''
    if not isinstance(val, str):
        return False
    a = 'http://' in val
    b = 'www.' in val
    c = any([x in val for x in ['.fr', '.com', '.org', '.gouv', '.net']])
    d = not ('@' in val)
    return (a or b or c) and d

import re

PROPORTION = 0.9


def _is(val):
    '''Repere le code RNA'''
    regex = r'^[wW]\d{9}$'
    return bool(re.match(regex, val))

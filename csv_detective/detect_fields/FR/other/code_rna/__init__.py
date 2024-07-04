import re

PROPORTION = 0.9


def _is(val):
    '''Repere le code RNA'''
    return bool(re.match(r'^[wW]\d{9}$', val))

import re

PROPORTION = 1


def _is(val):
    '''Detects twitter accounts'''
    return isinstance(val, str) and bool(re.match(r'^@[A-Za-z0-9_]+$', val))

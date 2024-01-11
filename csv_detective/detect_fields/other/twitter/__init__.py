import re

PROPORTION = 1


def _is(val):
    '''Detects twitter accounts'''
    return bool(re.match(r'^@[A-Za-z0-9_]+$', val))

import re

PROPORTION = 1


def _is(val):
    '''Detects twitter accounts'''
    regex = r'^@[A-Za-z0-9_]+$'
    return bool(re.match(regex, val))

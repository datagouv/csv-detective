import re

PROPORTION = 0.8


def _is(val):
    '''Detects Mongo ObjectIds'''
    return isinstance(val, str) and bool(re.match(r'^[0-9a-fA-F]{24}$', val))

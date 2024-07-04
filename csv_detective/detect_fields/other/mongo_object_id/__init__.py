import re

PROPORTION = 0.8


def _is(val):
    '''Detects Mongo ObjectIds'''
    return bool(re.match(r'^[0-9a-fA-F]{24}$', val))

import re

PROPORTION = 0.8

def _is(val):
    '''Detects Mongo ObjectIds'''
    regex = r'^[0-9a-fA-F]{24}$'
    return bool(re.match(regex, val))
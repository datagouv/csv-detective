import re

PROPORTION = 1


def _is(val):
    '''Detects integers'''
    regex = r'^(\+|-)?[0-9]+(\.0+)?$'
    return bool(re.match(regex, val))


import re

PROPORTION = 0.8


def _is(val):
    '''Detects UUIDs'''
    return bool(re.match(
        r'^[{]?[0-9a-fA-F]{8}' + '-?([0-9a-fA-F]{4}-?)' + '{3}[0-9a-fA-F]{12}[}]?$',
        val
    ))

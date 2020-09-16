import re

PROPORTION = 1

def _is(val):
    '''Detects floats'''
    regex = r'[-+]?[ ]?([0-9]*\.[0-9]+|[0-9]+)'
    #TODO fix '500b0' detected as float
    return bool(re.match(regex, val))


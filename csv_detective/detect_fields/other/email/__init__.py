import re

PROPORTION = 1


def _is(val):
    '''Detects e-mails'''
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$'
    return bool(re.match(regex, val))

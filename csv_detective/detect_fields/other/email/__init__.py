import re

PROPORTION = 1


def _is(val):
    '''Detects e-mails'''
    return isinstance(val, str) and bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$', val))

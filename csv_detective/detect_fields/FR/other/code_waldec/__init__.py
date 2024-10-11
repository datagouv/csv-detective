import re

PROPORTION = 0.9
regex = (
    r'^\d{3}\D\d{1,10}$|^\d\D\d\D\d{10}$|^\d{3}\D{3}\d{1,10}$|^\d{3}\D\d{4}\D\d{1,10}'
    r'$|^\d{3}\D\d{2}[-]\d{3}$|^\d\D\d\D\d{2}\D\d{1,8}$'
)


def _is(val):
    '''Repere le code Waldec'''
    return isinstance(val, str) and bool(re.match(regex, val))

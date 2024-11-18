import re

PROPORTION = 1


def _is(val):
    '''Renvoie True si val peut être une date au format iso, False sinon
    Exemple: 2023-01-15T12:30:45.123456Z'''
    return isinstance(val, str) and bool(
        re.match(
            r'^\d{4}-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])[Tt]'
            r'([0-2])([0-9]):([0-5])([0-9]):([0-5])([0-9])'
            r'(\.\d+)?([Zz]|[-+](0[0-9]|1[0-2]):[0-5][0-9])?$',
            val
        )
    )

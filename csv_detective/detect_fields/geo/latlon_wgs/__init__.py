import re

PROPORTION = 0.9


def _is(val):
    '''Renvoie True si val peut etre une latitude,longitude'''

    return isinstance(val, str) and bool(
        re.match(
            r'^\[?[\+\-]?[0-8]?\d\.\d* ?, ?[\+\-]?(1[0-7]\d|\d{1,2})\.\d+\]?$', val
        )
    )

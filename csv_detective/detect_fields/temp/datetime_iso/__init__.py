from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Renvoie True si val peut être une date au format iso, False sinon
    AAAA-MM-JJ HH-MM-SS avec indication du fuseau horaire

    '''
    a = bool(re.match(r'^\d\d\d\d\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])[tT ][\d:\.]{5,8}([zZ]|[+\-][012]\d[0-5]\d)?$', val))

    return a

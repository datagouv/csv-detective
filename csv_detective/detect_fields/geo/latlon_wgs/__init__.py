from csv_detective.process_text import _process_text
import re

PROPORTION = 0.9

def _is(val):
    '''Renvoie True si val peut etre une latitude,longitude'''

    a = bool(re.match(r'^\[?[\+\-]?[0-8]?\d\.\d* ?, ?[\+\-]?(1[0-7]\d|\d{1,2})\.\d+\]?$', val))

    return a

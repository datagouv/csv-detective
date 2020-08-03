from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Repère les numeros de telephone francais'''

    if len(val)<10: # trop court
        return False

    val = val.replace('.','').replace('-','').replace(' ','')

    regex = r'^(0|\+33|0033)?[0-9]{9}$'
    match_1 = bool(re.match(regex, val))
    return match_1

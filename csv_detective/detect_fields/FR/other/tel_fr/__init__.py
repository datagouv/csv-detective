from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Repère les numeros de telephone francais'''
    # TODO: Cette regex ne marche pas
    regex = r'^(0|\+33|0033)?[0-9]{9}$'
    match_1 = bool(re.match(regex, val))

    regex = r'^(0[1-9]|\+33 [1-9]|00 33 [1-9]|[1-9])( [0-9]{2}){4}$'
    match_2 = bool(re.match(regex, val))

    return match_1 or match_2

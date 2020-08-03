from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Détection les booléens'''
    liste_bool = ['0','1','vrai','faux','true','false','oui','non']
    return val.lower() in liste_bool

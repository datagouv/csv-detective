from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Renvoie True si val peut être un code commune INSEE, False sinon'''
        # TODO : ajouter une regex pour : 'que des chiffres ou bien commence par 2A, 2B puis 3 chiffres'
    if not len(val) in [4,5]:
        return False
    val = val.zfill(5)
    f = open(join(dirname(__file__), 'code_commune_insee.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    return val in liste


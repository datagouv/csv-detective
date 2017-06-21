from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Repère les codes APE700 de l'INSEE'''
    val = _process_text(val).upper()
    f = open(join(dirname(__file__), 'insee_ape700.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    print(val, val in liste)
    return val in liste

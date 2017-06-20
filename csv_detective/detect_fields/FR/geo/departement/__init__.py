from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 0.9

def _is(val):
    '''Match avec le nom des departements'''
    f = open(join(dirname(__file__), 'departement.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    val = _process_text(val)
    return val in liste

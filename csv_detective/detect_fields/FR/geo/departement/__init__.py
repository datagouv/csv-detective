from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 0.9
f = open(join(dirname(__file__), 'departement.txt'), 'r')
codes_departement = f.read().split('\n')
f.close()


def _is(val):
    '''Match avec le nom des departements'''

    val = _process_text(val)
    return val in codes_departement

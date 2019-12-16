from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1
f = open(join(dirname(__file__), 'csp_insee.txt'), 'r')
codes_insee = f.read().split('\n')
f.close()


def _is(val):
    '''Repère les csp telles que définies par l'INSEE'''
    val = _process_text(val)
    return val in codes_insee

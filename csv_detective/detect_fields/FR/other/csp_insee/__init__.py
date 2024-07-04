from os.path import dirname, join
from csv_detective.process_text import _process_text

PROPORTION = 1
f = open(join(dirname(__file__), 'csp_insee.txt'), 'r')
codes_insee = f.read().split('\n')
# removing empty str due to additionnal line in file
del codes_insee[-1]
codes_insee = set(codes_insee)
f.close()


def _is(val):
    '''Repère les csp telles que définies par l'INSEE'''
    val = _process_text(val)
    return val in codes_insee

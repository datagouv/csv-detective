from os.path import dirname, join
from csv_detective.process_text import _process_text

PROPORTION = 0.9
f = open(join(dirname(__file__), 'departement.txt'), 'r')
codes_departement = f.read().split('\n')
# removing empty str du to additionnal line in file
del codes_departement[-1]
codes_departement = set(codes_departement)
f.close()


def _is(val):
    '''Match avec le nom des departements'''

    val = _process_text(val)
    return val in codes_departement

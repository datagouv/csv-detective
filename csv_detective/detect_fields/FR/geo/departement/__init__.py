from os.path import dirname, join
from csv_detective.process_text import _process_text

PROPORTION = 0.9
f = open(join(dirname(__file__), 'departement.txt'), 'r')
departement = f.read().split('\n')
# removing empty str due to additionnal line in file
del departement[-1]
departement = set(departement)
max_len = max({len(p) for p in departement})
f.close()


def _is(val):
    '''Match avec le nom des departements'''
    if len(val) > max_len:
        return False
    val = _process_text(val)
    return val in departement

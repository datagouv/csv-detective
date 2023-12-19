from os.path import dirname, join
from csv_detective.process_text import _process_text

PROPORTION = 0.6
f = open(join(dirname(__file__), 'pays.txt'), 'r')
pays = f.read().split('\n')
pays = set(pays)
max_len = max({len(p) for p in pays})
f.close()


def _is(val):
    '''Match avec le nom des pays'''
    if len(val) > max_len:
        return False
    val = _process_text(val)
    return val in pays

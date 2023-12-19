from os.path import dirname, join
from csv_detective.process_text import _process_text
from unidecode import unidecode

PROPORTION = 0.9
f = open(join(dirname(__file__), 'cantons.txt'), 'r')
cantons = f.read().split('\n')
# removing empty str due to additionnal line in file
del cantons[-1]
cantons = set(cantons)
max_len = max({len(p) for p in cantons})
f.close()


def _is(val):
    '''Match avec le nom des cantons'''
    if len(val) > max_len:
        return False
    val = unidecode(_process_text(val)).upper()
    return val in cantons

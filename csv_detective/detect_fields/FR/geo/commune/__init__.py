from os.path import dirname, join
from csv_detective.process_text import _process_text

PROPORTION = 0.9
f = open(join(dirname(__file__), 'commune.txt'), 'r')
communes = f.read().split('\n')
# removing empty str due to additionnal line in file
del communes[-1]
communes = set(communes)
max_len = max({len(p) for p in communes})
f.close()


def _is(val):
    '''Match avec le nom des communes'''
    if len(val) > max_len:
        return False
    val = val.lower().replace('-', ' ')

    val = _process_text(val)
    return val in communes

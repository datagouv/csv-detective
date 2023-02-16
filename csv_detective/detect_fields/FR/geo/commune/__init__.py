from os.path import dirname, join
from csv_detective.process_text import _process_text

PROPORTION = 0.9
f = open(join(dirname(__file__), 'commune.txt'), 'r')
codes_commune = f.read().split('\n')
# removing empty str du to additionnal line in file
del codes_commune[-1]
codes_commune = set(codes_commune)
f.close()


def _is(val):
    '''Match avec le nom des communes'''
    val = val.lower().replace('-', ' ')

    val = _process_text(val)
    return val in codes_commune

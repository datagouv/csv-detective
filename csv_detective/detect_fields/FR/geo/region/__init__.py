from os.path import dirname, join
from csv_detective.process_text import _process_text

PROPORTION = 1
f = open(join(dirname(__file__), 'region.txt'), 'r')
regions = f.read().split('\n')
# removing empty str due to additionnal line in file
del regions[-1]
regions = set(regions)
f.close()


def _is(val):
    '''Match avec le nom des regions'''
    val = _process_text(val)
    return val in regions

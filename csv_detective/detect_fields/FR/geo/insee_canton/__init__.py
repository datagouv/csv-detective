from os.path import dirname, join
from csv_detective.process_text import _process_text
import re
from unidecode import unidecode

PROPORTION = 0.9
f = open(join(dirname(__file__), 'cantons.txt'), 'r')
cantons = f.read().split('\n')
f.close()


def _is(val):
    '''Match avec le nom des cantons'''

    val = unidecode(_process_text(val)).upper()
    return val in cantons

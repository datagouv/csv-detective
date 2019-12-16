from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 0.9
f = open(join(dirname(__file__), 'commune.txt'), 'r')
codes_commune = f.read().split('\n')
f.close()


def _is(val):
    '''Match avec le nom des communes'''
    val = val.lower().replace('-', ' ')

    val = _process_text(val)
    return val in codes_commune

from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1
f = open(join(dirname(__file__), 'insee_ape700.txt'), 'r')
condes_insee_ape = f.read().split('\n')
f.close()


def _is(val):
    '''Repère les codes APE700 de l'INSEE'''
    val = _process_text(val).upper()
    return val in condes_insee_ape

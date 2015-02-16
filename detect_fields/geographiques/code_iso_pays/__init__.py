# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:51:29 2015

@author: leo_cdo_intern
"""

from os.path import dirname, join
from process_text.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Renvoie True si val peut etre un code iso pays, False sinon'''
    regex = r'[A-Z]{2}'
    if not bool(re.match(regex, val)):
        return False

    f = open(join(dirname(__file__), 'code_iso_pays.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    return val in liste



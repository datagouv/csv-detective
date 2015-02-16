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
    '''Match avec le nom des departements'''
    f = open(join(dirname(__file__), 'departement.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    val = _process_text(val)
    return val in liste

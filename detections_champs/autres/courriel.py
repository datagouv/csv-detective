# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:54:46 2015

@author: leo_cdo_intern
"""

from os.path import dirname, join
from process_text.process_text import _process_text
import re

rel_path = '../../fichiers_de_reference/autres'
path = join(dirname(__file__), rel_path)

def _courriel(val):
    '''Repere les courriel'''
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$'
    return re.match(regex, val)

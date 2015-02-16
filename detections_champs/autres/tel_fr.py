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

def _tel_fr(val):
    '''Repère les numeros de telephone francais'''
    # TODO: Cette regex ne marche pas
    regex = r'^(0|(00|\+)33)[67][0-9]{8}$'
    return re.match(regex, val)

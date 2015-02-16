# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:51:29 2015

@author: leo_cdo_intern
"""

from os.path import dirname, join
from process_text.process_text import _process_text
import re

rel_path = '../../fichiers_de_reference/geographiques'
path = join(dirname(__file__), rel_path)

def _adresse(val):
    '''Repere des adresses'''
    val = _process_text(val)
    a = any([x in val for x in 'rue allee route avenue chemin boulevard bvd ure ilot'.split()])


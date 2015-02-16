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

def _sexe(val):
    '''Repère le sexe'''
    val =_process_text(val)
    return val in ['homme', 'femme', 'h', 'f', 'm', 'masculin', 'feminin']


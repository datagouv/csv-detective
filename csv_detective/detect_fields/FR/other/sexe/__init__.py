# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:54:46 2015

@author: leo_cdo_intern
"""

from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Repère le sexe'''
    val =_process_text(val)
    return val in ['homme', 'femme', 'h', 'f', 'm', 'masculin', 'feminin']


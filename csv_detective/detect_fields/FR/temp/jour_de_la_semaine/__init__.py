# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:53:48 2015

@author: leo_cdo_intern
"""

from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Renvoie True si les cahmps peuvent être des jours de la semaine'''
    val = val.lower()
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    return val in jours



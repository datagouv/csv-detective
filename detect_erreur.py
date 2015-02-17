# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 19:33:04 2015

@author: alexis
"""

def ints_as_floats(table):
    '''Détecte les colonnes contenant des entiers possibles écrits sous forme de float'''
    regex = r'^[0-9]+\.0+$'
    res = table.apply(lambda serie: serie.str.match(regex).all() and any(serie.notnull()))
    return res.index[res]

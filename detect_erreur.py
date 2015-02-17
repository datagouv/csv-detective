# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 19:33:04 2015

@author: alexis
"""

def ints_as_floats(serie):
    '''Détecte les colonnes contenant des entiers possibles écrits sous forme de float'''
    regex = r'^[0-9]+\.0+$'
    
    if all(serie.str.match(regex)) and any(serie.notnull()):
        
        print "La colonne", str(serie.name), " a une seule valeur après la virgule, on la supprime"
        print serie
        print '\n\n\n'
    

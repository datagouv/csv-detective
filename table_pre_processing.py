# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 14:53:15 2015

@author: leo_cdo_intern
"""

def detect_headers(file, sep):
    ''' teste les 5 première ligne pour voir si on a une
        ligne qui ferait un bon header '''
    with open(file, 'r') as myCsvfile:
        for i in range(5):
            header = myCsvfile.readline()
            chaine = header.split(sep)
            if (chaine[-1] not in ['', '\n'] and 
                 all(mot not in ['', '\n'] for mot in chaine[1:-1])):
                return i
    return 0


def entier_a_virgule(serie):
    '''Détecte les colonnes contenant des entiers possibles écrits sous forme de float'''
    regex = r'^[0-9]+\.0+$'
    
    if all(serie.str.match(regex)) and any(serie.notnull()):
        
        print "La colonne", str(serie.name), " a une seule valeur après la virgule, on la supprime"
        print serie
        print '\n\n\n'
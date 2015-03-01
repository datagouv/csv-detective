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
    

def detect_extra_columns(file, sep):
    file.seek(0)
    retour = False
    nb_useless_col = 99999
    
    for i in range(10):
        line = file.readline()
        # regarde si on a un retour
        if retour: 
            assert line[-1] == "\n"
        if line[-1] == "\n":
            retour = True
        
        # regarde le nombre de derniere colonne inutile
        deb = 0 + retour
        line = line[::-1][deb:]
        k = 0
        for sign in line:
            if sign != sep:
                break
            k += 1
        nb_useless_col = min(k, nb_useless_col)
    return nb_useless_col, retour        


def remove_extra_columns(file, detect_extra_columns_results):
    res = detect_extra_columns_results
    to_remove = res[0] + res[1]
    L = file.read().splitlines()
    for line in L: 
        line = line[:-to_remove]
        print line
    import pdb
    pdb.set_trace()



def detect_headers(file, sep):
    ''' Tests 10 first rows for possible header (header not in 1st line)'''
    file.seek(0)
    for i in range(10):
        header = file.readline()
        chaine = header.split(sep)
        if (chaine[-1] not in ['', '\n'] and 
             all([mot not in ['', '\n'] for mot in chaine[1:-1]])):
            return i, header.replace(sep, ';')
    return 0,  'not_found'


def detect_heading_columns(file, sep, ):
    ''' Tests first 10 lines to see if there are empty heading columns'''
    file.seek(0)
    return_int = float('Inf')
    for i in range(10):
        line = file.readline()
        return_int = min(return_int, len(line) - len(line.strip(sep)))
        if return_int == 0:
            return 0
    return return_int


def detect_trailing_columns(file, sep, heading_columns):
    ''' Tests first 10 lines to see if there are empty trailing columns'''
    file.seek(0)
    return_int = float('Inf')
    for i in range(10):
        line = file.readline()
        return_int = min(return_int, len(line.replace('\n', '')) - len(line.replace('\n', '').strip(sep)) - heading_columns)
        if return_int == 0:
            return 0
    return return_int
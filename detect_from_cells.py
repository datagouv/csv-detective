# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 09:47:26 2015

@author: leo_cdo_intern

###############################################################################
Ce script analyse les premières lignes d'un CSV pour essayer de déterminer le 
contenu possible des champs
"""

import pandas as pd
from os.path import join
import re


#############################################################################
############### TESTS POUR DIFFERENTS CHAMPS ##################################
# On fait des test successifs qui ne peuvent renvoyer que False. On renvoie True
# à la fin de la fonction
# Le standard que j'ai adopté est de tout mettre en minuscules, sans accents, 
# sans ponctuation (remplacée par des espaces)

# TODO : Les communes, les noms des départements, les noms des regions


#### PROCESSING DU TEXTE

def _process_text(val):
    '''Met le string val sous sous sa forme normée'''
    val = val.lower()
    val = val.replace('-', ' ')
    val = val.replace("'", ' ')
    val = val.replace('\xc3\xa8', 'e')
    val = val.replace('\xc3\xa9', 'e')
    val = val.replace('\xc3\x8e', 'i')    
    val = val.replace('\xc3\xb4', 'o')
    return val


#### GEOGRAPHIQUES
def _code_postal(val):
    '''Renvoie True si val peut être un code postal, False sinon'''
    if isinstance(val, str) or isinstance(val, unicode): # Si val est un string, on essaye de le convertir en nombre
        if val.isdigit():
            val = int(val)
        else:
            return False
    elif isinstance(val, int):
        pass
    else:
        return False
    if not (val > 1000) and (val < 100000):
        return False    
    f = open('codes_postaux.txt', 'r')
    liste = f.read().split('\n')
    f.close()
    return str(val).zfill(5) in liste
    
def _code_commune_insee(val):
    '''Renvoie True si val peut être un code commune INSEE, False sinon'''
    if not isinstance(val, str):
        val = str(val)
        # TODO : ajouter une regex pour : 'que des chiffres ou bien commence par 2A, 2B puis 3 chiffres'
    if not len(val) in [4,5]:
        return False
    val = val.zfill(5)
    f = open('codes_commune_insee.txt', 'r')
    liste = f.read().split('\n')
    f.close()
    return val in liste

def _code_departement(val):
    '''Renvoie True si val peut être un département, False sinon'''
    if isinstance(val, int) or isinstance(val, float): # Si val est un int, on convertit en string
        val = str(val)
    val = val.zfill(3)
    liste_des_dep = [str(x).zfill(3) for x in range(1,96)] + \
                    ['02A', '02B'] + [str(x).zfill(3) for x in range(971,977)]
    # TODO: Enregistrer la liste des départements dans un fichier texte séparé
    return val in liste_des_dep
        
        
def _region(val):
    '''Match avec le nom des départements'''
    if not (isinstance(val, str) or isinstance(val, unicode)):
        return False
    
    f = open('regions.txt', 'r')
    liste = f.read().split('\n')
    f.close()
    val = _process_text(val)
    return val in liste

def _departement(val):
    '''Match avec le nom des départements'''
    if not (isinstance(val, str) or isinstance(val, unicode)):
        return False
    
    f = open('departements.txt', 'r')
    liste = f.read().split('\n')
    f.close()
    val = _process_text(val)
    return val in liste
    
def _commune(val):
    '''Match avec le nom des départements'''
    if not (isinstance(val, str) or isinstance(val, unicode)):
        return False
    
    f = open('communes.txt', 'r')
    liste = f.read().split('\n')
    f.close()
    val = _process_text(val)
    return val in liste
    

## Traitement du fichier texte
#f = open('regions.txt', 'r')
#text = f.read().split('\n')
#f.close()  
#text = [_process_text(val) for val in text]
#f = open('regions.txt', 'w')
#for x in text:
#    f.write(x + '\n')
#f.close()

#### DATES
def _jour_de_la_semaine(val):
    '''Renvoie True si les cahmps peuvent être des jours de la semaine'''
    if not isinstance(val, str) or isinstance(val, unicode):
        return False
    val = val.lower()
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    return val in jours

def _annee(val):
    '''Renvoie True si les cahmps peuvent être des jours de la semaine'''
    try:
        val = int(val)
    except:
        return False
    if (1900 <= val) and (val <= 2100):
        return True
    else:
        return False

def _date(val):
    '''Renvoie True si val peut être une date, False sinon'''
    if not isinstance(val, str) or isinstance(val, unicode): # Une date doit être un string ou unicode
        return False
    a = bool(re.match(r'^(19|20)\d\d[ -/_](0[1-9]|1[012])[ -/_](0[1-9]|[12][0-9]|3[01])', val)) # matches 1993-12/02
    b = bool(re.match(r'^(0[1-9]|[12][0-9]|3[01])[ -/_](0[1-9]|1[012])[ -/_]([0-9]{2}|(19|20)[0-9]{2}$)', val)) # matches 02/12 03 and 02_12 2003
    c = bool(re.match(r'^(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[012])([0-9]{2}|(19|20){2}$)', val)) # matches 02_05_2003
    d = bool(re.match(r'^(19|20)\d\d(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])', val)) # matches 19931202
    return a or b or c or d

#############################################################################
############### ROUTINE DE TEST CI DESSOUS ##################################

# TODO : Mettre un pourcentage de valeurs justes (au lieu de nécessiter que toutes les valeurs soient justes)

def test_col(serie, test_func):
    '''Teste progressivement une colonne avec la foncition test_func, renvoie True si toutes
    les valeurs de la série renvoient True avec test_func. False sinon.    
    '''
    for range_ in [range(0,1), range(1,5), range(5,50)]: # Pour ne pas faire d'opérations inutiles, on commence par 1, puis 5 puis 50 valeurs
        if all(serie.iloc[range_].apply(test_func)):
            pass
        else:
            return False
    return True

def routine(file):
    '''Renvoie un table avec en colonnes les colonnes du csv et en ligne, les champs testes'''
    table = pd.read_csv(file, sep = ';', nrows = 50)
    table['date'] = '1992_05_25'
    fonctions_test = dict()
    # Geographique
    fonctions_test['code_postal'] = _code_postal
    fonctions_test['code_insee'] = _code_commune_insee
    fonctions_test['code_departement'] = _code_departement
    
    fonctions_test['region'] = _region
    fonctions_test['departement'] = _departement
    fonctions_test['commune'] = _commune

    # Date
    fonctions_test['jour_de_la_semaine'] = _jour_de_la_semaine
    fonctions_test['annee'] = _annee
    fonctions_test['date'] = _date

    
    return_table = pd.DataFrame(columns = table.columns)    
    for key, test_func in fonctions_test.iteritems():
        return_table.loc[key] = table.apply(lambda serie: test_col(serie, test_func))
        
        
    for x in return_table.columns:
        print 'La colonne', x, 'est peut-être :',
        valeurs_possibles = list(return_table[return_table[x]].index)
        print valeurs_possibles
    return return_table

    
if __name__ == '__main__':
    path = '/home/debian/Documents/data/villes'
    file = join(path, 'info_villes.csv')
    print '\n'
    routine(file)


    
        
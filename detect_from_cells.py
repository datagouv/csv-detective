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
    return True
    

def _departement(val):
    '''Renvoie True si val peut être un département, False sinon'''
    if isinstance(val, int) or isinstance(val, float): # Si val est un int, on convertit en string
        val = str(val)
    val = val.zfill(3)
    liste_des_dep = [str(x).zfill(3) for x in range(1,96)] + \
                    ['02A', '02B'] + [str(x).zfill(3) for x in range(971,977)]
    # TODO: Enregistrer la liste des départements dans un fichier texte séparé
    return val in liste_des_dep
        

#### DATES
def _jour_de_la_semaine(val):
    '''Renvoie True si les cahmps peuvent être des jours de la semaine'''
    if not isinstance(val, str) or isinstance(val, unicode):
        return False
    val = val.lower()
    jours = ['lu', 'ma', 'me', 'je', 've', 'sa', 'di']
    if not any([jour in val for jour in jours]):
        return False
        
    return True

 
#def _date(val):
#    '''Renvoie True si val peut être une date, False sinon'''
#    if not isinstance(val, str) or isinstance(val, unicode): # Une date doit être un string ou unicode
#        return False
#    list_of_regex_to_check = ['^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$']
#    a = re.compile('^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$')
#    a.match(string)
    


#############################################################################
############### ROUTINE DE TEST CI DESSOUS ##################################
       
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
    
    fonctions_test = dict()
    fonctions_test['code_postal'] = _code_postal
    fonctions_test['code_insee'] = _code_postal
    fonctions_test['jour_de_la_semaine'] = _jour_de_la_semaine
    fonctions_test['departement'] = _departement
    
    return_table = pd.DataFrame(columns = table.columns)    
    for key, test_func in fonctions_test.iteritems():
        return_table.loc[key] = table.apply(lambda serie: test_col(serie, test_func))
        
    return return_table
    
    
    
    
    
if __name__ == '__main__':
    path = '/home/debian/Documents/data/villes'
    file = join(path, 'info_villes.csv')
    routine(file)


    
        
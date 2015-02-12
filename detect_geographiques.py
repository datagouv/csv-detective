# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:51:29 2015

@author: debian
##############################################################################
Contains : _code_postal, _code_commune_insee, _code_departement, _region, _departement, _commune, _adresse 
"""

from os.path import join
from process_text import _process_text
import re
path = '/home/debian/Documents/projects/csv_detective/fichiers_de_reference/geographique'



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
    f = open(join(path,'codes_postaux.txt'), 'r')
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
    f = open(join(path,'codes_commune_insee.txt'), 'r')
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
    
    f = open(join(path,'regions.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    val = _process_text(val)
    return val in liste


def _departement(val):
    '''Match avec le nom des départements'''
    if not (isinstance(val, str) or isinstance(val, unicode)):
        return False
    
    f = open(join(path,'departements.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    val = _process_text(val)
    return val in liste
    
    
def _commune(val):
    '''Match avec le nom des départements'''
    if not (isinstance(val, str) or isinstance(val, unicode)):
        return False
    
    f = open(join(path,'communes.txt'), 'r')
    liste = f.read().split('\n')
    f.close()
    val = _process_text(val)
    return val in liste


def _adresse(val):
    '''Repère des adresses'''
    if not (isinstance(val, str) or isinstance(val, unicode)):
        return False
    val = _process_text(val)
    a = any([x in val for x in 'rue allee route avenue chemin boulevard bvd ure ilot'.split()])
    
    
    
## Traitement du fichier texte (for dev purposes)
#f = open('csp_insee.txt', 'r')
#text = f.read().split('\n')
#f.close()  
#text = [_process_text(val) for val in text]
#f = open('csp_insee.txt', 'w')
#for x in text:
#    f.write(x + '\n')
#f.close()

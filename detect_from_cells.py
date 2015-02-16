# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 09:47:26 2015

@author: leo_cdo_intern

###############################################################################
Ce script analyse les premières lignes d'un CSV pour essayer de déterminer le
contenu possible des champs


ACTUELLEMENT EN DEVELOPPEMENT : Indactions comment tester tout en bas
"""

import pandas as pd
import chardet
from os.path import join

import detections_champs


from detect_erreur import entier_a_virgule

#############################################################################
############### ROUTINE DE TEST CI DESSOUS ##################################

# TODO : Mettre un pourcentage de valeurs justes (au lieu de nécessiter que toutes les valeurs soient justes)

def detect_delimiter(file):
    '''Trouve le délimitateur du csv'''
    # TODO: add a robust detection:
    # si on a un point virgule comme texte et \t comme séparateur, on renvoit
    # pour l'instant un point virgule
    with open(file, 'r') as myCsvfile:
        header = myCsvfile.readline()
        possible_separators = [";", ",", "|", "\t"]
        sep_count = dict()
        for sep in possible_separators:
            sep_count[sep] = header.count(sep)
    return max(sep_count, key = sep_count.get)


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


def test_col(serie, test_func):
    '''Teste progressivement une colonne avec la foncition test_func, renvoie True si toutes
    les valeurs de la série renvoient True avec test_func. False sinon.
    '''
    serie = serie[serie.notnull()]
    ser_len = len(serie)
    if ser_len == 0:
        return False
    for range_ in [range(0,min(1, ser_len)), range(min(1, ser_len),min(5, ser_len)), range(min(5, ser_len),min(50, ser_len))]: # Pour ne pas faire d'opérations inutiles, on commence par 1, puis 5 puis 50 valeurs
        if all(serie.iloc[range_].apply(test_func)):
            pass
        else:
            return False
    return True


def routine(file):
    '''Renvoie un table avec en colonnes les colonnes du csv et en ligne, les champs testes'''

    if not any([extension in file for extension in ['.csv', '.tsv']]):
        return False

    sep = detect_delimiter(file)
    headers_row = detect_headers(file, sep)
    
#    with open(file, 'r') as myCsvfile:
#        print chardet.detect(myCsvfile.read())
    
    table = pd.read_csv(file, sep = sep, 
                        skiprows = headers_row,
                        nrows = 50, dtype = 'unicode')
    fonctions_test = dict()
    # Geographique
    fonctions_test['code_postal'] = detections_champs.geographiques._code_postal
    fonctions_test['code_commune_insee'] = detections_champs.geographiques._code_commune_insee
    fonctions_test['code_departement'] = detections_champs.geographiques._code_departement
    fonctions_test['code_iso_pays'] = detections_champs.geographiques._code_iso_pays

    fonctions_test['pays'] = detections_champs.geographiques._pays
    fonctions_test['region'] = detections_champs.geographiques._region
    fonctions_test['departement'] = detections_champs.geographiques._departement
    fonctions_test['commune'] = detections_champs.geographiques._commune

    fonctions_test['adresse'] = detections_champs.geographiques._adresse

    # Date
    fonctions_test['jour_de_la_semaine'] = detections_champs.temporels._jour_de_la_semaine
    fonctions_test['annee'] = detections_champs.temporels._annee
    fonctions_test['date'] = detections_champs.temporels._date

    # Autres
    fonctions_test['csp_code_insee'] = detections_champs.autres._code_csp_insee
    fonctions_test['csp_insee'] = detections_champs.autres._csp_insee
    fonctions_test['sexe'] = detections_champs.autres._sexe
    fonctions_test['url'] = detections_champs.autres._url
    fonctions_test['courriel'] = detections_champs.autres._courriel
    fonctions_test['tel_fr'] = detections_champs.autres._tel_fr
    fonctions_test['siren'] = detections_champs.autres._siren
    

    return_table = pd.DataFrame(columns = table.columns)

    for key, test_func in fonctions_test.iteritems():
        try:
            return_table.loc[key] = table.apply(lambda serie: test_col(serie, test_func))
        except Exception, e:
            import pdb
            print str(e)
            pdb.set_trace()
            
    table.apply(entier_a_virgule, axis=1)

    for x in return_table.columns:
        valeurs_possibles = list(return_table[return_table[x]].index)
        if valeurs_possibles != []:
            print '  >>  La colonne', x, 'est peut-être :',
            print valeurs_possibles
    return return_table


if __name__ == '__main__':

    from os import listdir
    from os.path import isfile, join

    ### CONSIGNES : Mettre toutes les data a tester dans le dossier indiqué par path
    # et lancer le script. Il doit afficherc pour chaque fichier dans ce dossier (ne doit contenir que des csv)
    # les colonnes pour lesquelles un match a été trouvé
    path = '/home/debian/Documents/data/test_csv_detector' # 'data'
    all_files = [join(path, f) for f in listdir(path) if isfile(join(path,f)) ]

    for file in all_files:
        print '*****************************************'
        print file
        routine(file)
        print '\n'




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

import detect_fields


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


def test_col(serie, test_func, proportion = 0.9):
    '''Teste progressivement une colonne avec la foncition test_func, renvoie True si toutes
    les valeurs de la série renvoient True avec test_func. False sinon.
    proportion indique le taux de valeurs qui doivent passer le test
    '''
    serie = serie[serie.notnull()]
    ser_len = len(serie)
    if ser_len == 0:
        return False
    if proportion == 1:
        for range_ in [range(0,min(1, ser_len)), range(min(1, ser_len),min(5, ser_len)), range(min(5, ser_len),min(50, ser_len))]: # Pour ne pas faire d'opérations inutiles, on commence par 1, puis 5 puis 50 valeurs
            if all(serie.iloc[range_].apply(test_func)):
                pass
            else:
                return False
        return True
    else:
        try:
            return serie.apply(test_func).sum() > proportion * len(serie)
        except:
            import pdb
            pdb.set_trace()

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
                        
                        
                        
    all_tests = [detect_fields.code_postal,
                 detect_fields.code_commune_insee,
                 detect_fields.code_departement, 
                 detect_fields.code_iso_pays,
                 detect_fields.pays,
                 detect_fields.region,
                 detect_fields.departement,
                 detect_fields.commune,
                 detect_fields.adresse,
                 
                 detect_fields.jour_de_la_semaine,
                 detect_fields.annee,
                 detect_fields.date,
                 
                 detect_fields.code_csp_insee,
                 detect_fields.csp_insee,
                 detect_fields.sexe,
                 detect_fields.url,
                 detect_fields.courriel,
                 detect_fields.tel_fr,
                 detect_fields.siren
                 ]
                 
    test_funcs = dict()
    for test in all_tests:
        name = test.__name__.split('.')[-1]
        test_funcs[name] = {'func' : test._is,
                            'prop' : test.PROPORTION
                            }
    

    return_table = pd.DataFrame(columns = table.columns)

    for key, value in test_funcs.iteritems():
        try:
            return_table.loc[key] = table.apply(lambda serie: test_col(serie, value['func'], value['prop']))
        except Exception, e:
            import pdb
            print str(e)
            pdb.set_trace()
            
    table.apply(entier_a_virgule, axis=1)
    
    
    return_dict = dict()
    for col in return_table.columns:
        valeurs_possibles = list(return_table[return_table[col]].index)
        if valeurs_possibles != []:
            print '  >>  La colonne', col, 'est peut-être :',
            print valeurs_possibles
            return_dict[col] = valeurs_possibles
    return return_dict


if __name__ == '__main__':

    from os import listdir
    from os.path import isfile, join
    import json
    
    ### CONSIGNES : Mettre toutes les data a tester dans le dossier indiqué par path
    # et lancer le script. Il doit afficherc pour chaque fichier dans ce dossier (ne doit contenir que des csv)
    # les colonnes pour lesquelles un match a été trouvé
    
    path = '/home/debian/Documents/data/test_csv_detector' # 'data'
    json_path = '/home/debian/Documents/data/test_csv_detector/jsons'
    
    
    all_files = listdir(path)

    for file in all_files:
        print '*****************************************'
        print file
        
        a = routine(join(path, file))
        if a:
            with open(join(json_path, file.replace('.csv', '.json')), 'wb') as fp:
                json.dump(a, fp)
        print '\n'




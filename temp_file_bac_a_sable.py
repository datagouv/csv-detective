# -*- coding: utf-8 -*-
"""
Created on Mon Feb 16 17:32:10 2015

@author: debian
"""

a = '''
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
'''

a = a.replace("= ", "= {'fonction' : ")
a = a.replace('\n', ", 'proportion' : 1} \n")
print a


from os import listdir
from os.path import isfile, join
path = '/home/debian/Documents/projects/csv_detective/detections_champs/autres'
onlyfiles = [ f for f in listdir(path) if isfile(join(path,f)) ]
for x in onlyfiles:
    if x[-3:] == '.py':
        directory = join(path, x)[:-3]
        print directory
        if not os.path.exists(directory):
            os.makedirs(directory)
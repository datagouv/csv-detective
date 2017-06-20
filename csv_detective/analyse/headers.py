from os import listdir
from os.path import isfile, join
import json

### CONSIGNES : Mettre toutes les data a tester dans le dossier indiqué par path
# et lancer le script. Il doit afficherc pour chaque fichier dans ce dossier (ne doit contenir que des csv)
# les colonnes pour lesquelles un match a été trouvé

# main_path = '/home/debian/Documents/'
main_path = 'C:/git/csv_detective/'    
path = main_path + 'data/test_csv_detector' # 
json_path = main_path + 'data/test_csv_detector/jsons'

num_rows = 50 # nombre de lignes à analyser

# rassemble tous dans une base de donnes
all_files = listdir(json_path)
counter = 0
for file_name in all_files:
    print('*****************************************')
    print(file_name)

    file = open(join(json_path, file_name), 'r')
        data = json.load(file)
    file.close()
    
    headers     
    with open(join(json_path, file_name.replace('.csv', '.json')), 'wb') as fp:
            json.dump(a, fp, indent=4, separators=(',', ': '), encoding="utf-8")
    print('\n')
print('on a trouvé des matchs éventuels pour ', counter, 'valeurs')
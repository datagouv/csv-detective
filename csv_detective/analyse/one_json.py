import json
from os import listdir
from os.path import isfile, join
import pandas as pd

main_path = 'C:/git/csv_detective/'    
path = main_path + 'data' # 
json_path = main_path + 'data/test_csv_detector/jsons'

num_rows = 50 # nombre de lignes à analyser

# rassemble tous dans une base de donnes
def one_table():
    all_files = listdir(json_path)
    all = dict()
    for file_name in all_files:
        print('*****************************************')
        print(file_name)

        file = open(join(json_path, file_name), 'r')
        data = json.load(file)
        file.close()
        all[file_name[:-5]] = data
    return pd.DataFrame(all)


# detect headers
tab = one_table()
head = tab.loc['headers'] 
cond = (head == u'not_found')
list_not_found = tab.loc[:,cond].columns
print(list_not_found)

#file_name = list_not_found[0]
#try: 
#    filename = join(main_path, 'data', 'test_csv_detector', file_name + '.csv')
#    file = open(filename, 'r')
#except:
#    filename = join(main_path, 'data', 'test_csv_detector', file_name + '.tsv')
#    file = open(filename, 'r')

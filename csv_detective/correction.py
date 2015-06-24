# -*- coding: utf-8 -*-

def remove_extra_columns(filename, detect_extra_columns_results, out_file=None):
    res = detect_extra_columns_results
    to_remove = res[0] + res[1]
    f = open(filename, 'r')
    lines = f.read().splitlines()

    out_lines = []
    for line in lines: 
        out_lines.append(line[:-to_remove] + '\n')
    f.close()
    
    if out_file is None:
        out = open(filename, 'w')
    else:
        out = open(out_file, 'w')
    out.writelines(out_lines)
    out.close()
    
    


#def remove_empty_line(filename):
#    L = file.read().splitlines()
#    for line in L: 
#        if line != '':
            

if __name__ == '__main__':

    from os import listdir
    from os.path import isfile, join
    from csv_detective.detection import detect_extra_columns, detect_separator
    import json

    # main_path = '/home/debian/Documents/'
    main_path = 'C:/git/csv_detective/'
    path = main_path + 'data/test_csv_detector' #
    json_path = main_path + 'data/test_csv_detector/jsons'

    num_lines = 50 # nombre de lignes à analyser

    all_files = listdir(path)
    counter = 0
    for file_name in all_files:
        print '*****************************************'
        print file_name
        if any([extension in file_name for extension in ['.csv', '.tsv']]):
            file = open(join(path, file_name), 'r')
            sep = detect_separator(file)
            res = detect_extra_columns(file, sep)
            if res[0] > 1:
                print ('le fichier ' + file_name + ' est écrasé pour retirer' +
                       ' des colonnes inutiles')
                remove_extra_columns(join(path, file_name), res)
            file.close()

        print '\n'
    print 'on a trouvé des matchs éventuels pour ', counter, 'valeurs'


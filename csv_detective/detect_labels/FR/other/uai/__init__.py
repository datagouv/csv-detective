from csv_detective.process_text import _process_text

PROPORTION = 1

def _is(header):
    '''Returns 1 if the (processed) header matches one of the expected words combination, else 0'''

    words_combinations_list = ['uai', 'code etablissement', 'code uai', 'uai - identifiant', 'numero uai', 'rne', "numero de l'etablissement", 'code rne', 'codeetab', "code uai de l'etablissement", 'ref uai', 'cd rne', 'numerouai', 'numero d etablissement', 'code etablissement', 'numero etablissement']
    processed_header = _process_text(header)

    return float(any([words_combination == processed_header for words_combination in words_combinations_list]))
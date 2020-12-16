from csv_detective.process_text import _process_text

PROPORTION = 1

def _is(header):
    '''Returns 1 if the (processed) header matches one of the expected words combination, else 0'''

    words_combinations_list = ['date', 'jour', 'date de mise a jour', 'sns date', 'date maj', 'rem date', 'periode', 'date de publication', 'dpc', 'extract date', 'date immatriculation', 'date jeu donnees', 'datemaj', 'dateouv', 'date der maj', 'dmaj', 'jour']
    processed_header = _process_text(header)

    return float(any([words_combination == processed_header for words_combination in words_combinations_list]))
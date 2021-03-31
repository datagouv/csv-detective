from csv_detective.utils import full_word_strictly_inside_string
from csv_detective.process_text import _process_text

PROPORTION = 1

def _is(header):
    '''Returns 1 if the (processed) header matches one of the expected words combination, else 0'''

    words_combinations_list = ['date', 'jour', 'date de mise a jour', 'sns date', 'date maj', 'rem date', 'periode', 'date de publication', 'dpc', 'extract date', 'date immatriculation', 'date jeu donnees', 'datemaj', 'dateouv', 'date der maj', 'dmaj', 'jour']
    processed_header = _process_text(header)

    header_matches_words_combination = float(any([words_combination == processed_header for words_combination in words_combinations_list]))
    words_combination_in_header = 0.5*float(any([full_word_strictly_inside_string(words_combination, processed_header) for words_combination in words_combinations_list]))
    
    return max(header_matches_words_combination, words_combination_in_header)
from csv_detective.utils import is_word_in_string
from csv_detective.parsing.text import _process_text

PROPORTION = 0.5


def _is(header):
    '''
    Returns 1 if the (processed) header matches one of the expected words combination,
    else 0
    '''

    words_combinations_list = [
        'date',
        'jour',
        'date de mise a jour',
        'sns date',
        'date maj',
        'rem date',
        'periode',
        'date de publication',
        'dpc',
        'extract date',
        'date immatriculation',
        'date jeu donnees',
        'datemaj',
        'dateouv',
        'date der maj',
        'dmaj',
        'jour',
        'yyyymmdd',
        'aaaammjj',
    ]
    processed_header = _process_text(header)

    header_matches_words_combination = float(
        any(
            [
                words_combination == processed_header for words_combination in words_combinations_list
            ]
        )
    )
    words_combination_in_header = 0.5 * float(
        any(
            [
                is_word_in_string(
                    words_combination, processed_header
                ) for words_combination in words_combinations_list
            ]
        )
    )

    return max(header_matches_words_combination, words_combination_in_header)

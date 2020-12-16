from csv_detective.process_text import _process_text

PROPORTION = 1

def _is(header):
    '''Returns 1 if the (processed) header matches one of the expected words combination, else 0'''

    words_combinations_list = ['telephone', 'tel', 'tel1', 'tel2', 'phone', 'num tel', 'tel mob', 'telephone sav', 'telephone1', 'coordinates.phone', 'telephone du lieu']
    processed_header = _process_text(header)

    return float(any([words_combination == processed_header for words_combination in words_combinations_list]))
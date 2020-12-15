import numpy as np
from csv_detective.process_text import _process_text
import re

PROPORTION = 0.5


def _is(header):
    '''Returns the share of words in the (processed) header that match one of the expected words'''

    words_list = ['code', 'postal']
    processed_header = _process_text(header)

    return np.mean([word in words_list for word in processed_header.split()])
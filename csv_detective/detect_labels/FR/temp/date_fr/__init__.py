from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    # To improve: no header specific to "fr" found in data
    words_combinations_list = ["date"]
    return header_score(header, words_combinations_list)

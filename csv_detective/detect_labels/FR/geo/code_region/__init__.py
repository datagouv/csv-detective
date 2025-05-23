from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    # "reg" : possible confusion with region name?
    words_combinations_list = [
        "code region",
        "reg",
        "code insee region",
        "region",
    ]
    return header_score(header, words_combinations_list)

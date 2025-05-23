from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    # To improve? No specific header found in data
    words_combinations_list = [
        "csp insee",
        "csp",
        "categorie socioprofessionnelle",
    ]
    return header_score(header, words_combinations_list)

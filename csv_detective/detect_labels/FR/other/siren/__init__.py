from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "siren",
        "siren organisme designe",
        "siren organisme designant",
        "n° siren",
        "siren organisme",
        "siren titulaire",
        "numero siren",
    ]
    return header_score(header, words_combinations_list)

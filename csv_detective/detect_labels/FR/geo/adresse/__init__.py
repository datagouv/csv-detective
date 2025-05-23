from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "adresse",
        "adresse postale",
        "adresse geographique",
        "adr",
        "adresse complete",
        "adresse station",
    ]
    return header_score(header, words_combinations_list)

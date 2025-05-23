from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "jour semaine",
        "type jour",
        "jour de la semaine",
        "saufjour",
        "nomjour",
        "jour",
        "jour de fermeture",
    ]
    return header_score(header, words_combinations_list)

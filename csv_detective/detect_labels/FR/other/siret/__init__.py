from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "siret",
        "siret d",
        "num siret",
        "siretacheteur",
        "n° siret",
        "coll siret",
    ]
    return header_score(header, words_combinations_list)

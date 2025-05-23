from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "region",
        "libelle region",
        "nom region",
        "libelle reg",
        "nom reg",
        "reg libusage",
        "nom de la region",
        "regionorg",
        "regionlieu",
        "reg",
        "nom officiel region",
    ]
    return header_score(header, words_combinations_list)

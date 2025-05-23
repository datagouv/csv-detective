from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "date",
        "jour",
        "date de mise a jour",
        "sns date",
        "date maj",
        "rem date",
        "periode",
        "date de publication",
        "dpc",
        "extract date",
        "date immatriculation",
        "date jeu donnees",
        "datemaj",
        "dateouv",
        "date der maj",
        "dmaj",
        "jour",
        "yyyymmdd",
        "aaaammjj",
    ]
    return header_score(header, words_combinations_list)

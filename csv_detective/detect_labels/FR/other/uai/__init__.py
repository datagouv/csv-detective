from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "uai",
        "code etablissement",
        "code uai",
        "uai - identifiant",
        "numero uai",
        "rne",
        "numero de l'etablissement",
        "code rne",
        "codeetab",
        "code uai de l'etablissement",
        "ref uai",
        "cd rne",
        "numerouai",
        "numero d etablissement",
        "code etablissement",
        "numero etablissement",
    ]
    return header_score(header, words_combinations_list)

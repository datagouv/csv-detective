from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "year",
        "annee",
        "annee depot",
        "an nais",
        "exercice",
        "data year",
        "annee de publication",
        "exercice comptable",
        "annee de naissance",
        "annee ouverture",
    ]
    return header_score(header, words_combinations_list)

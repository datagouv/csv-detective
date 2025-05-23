from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "code ape",
        "code activite (ape)",
        "code naf",
        "code naf organisme designe",
        "code naf organisme designant",
        "base sirene : code ape de l'etablissement siege",
    ]
    return header_score(header, words_combinations_list)

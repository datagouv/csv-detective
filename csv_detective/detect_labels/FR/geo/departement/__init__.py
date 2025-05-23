from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "departement",
        "libelle du departement",
        "deplib",
        "nom dept",
        "dept",
        "libdepartement",
        "nom departement",
        "libelle dep",
        "libelle departement",
        "lb departements",
        "dep libusage",
        "lb departement",
        "nom dep",
    ]
    return header_score(header, words_combinations_list)

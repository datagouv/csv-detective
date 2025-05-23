from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "pays",
        "payslieu",
        "paysorg",
        "country",
        "pays lib",
        "lieupays",
        "pays beneficiaire",
        "nom du pays",
        "journey start country",
        "libelle pays",
        "journey end country",
    ]
    return header_score(header, words_combinations_list)

from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = ["budget", "salaire", "euro", "euros", "prêt", "montant"]
    return header_score(header, words_combinations_list)

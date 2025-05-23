from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    # "dep": Possible confusion with dep name?
    words_combinations_list = [
        "code departement",
        "code_departement",
        "dep",
        "departement",
        "dept",
    ]
    return header_score(header, words_combinations_list)

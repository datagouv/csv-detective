from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:

    words_combinations_list = [
        "telephone",
        "tel",
        "tel1",
        "tel2",
        "phone",
        "num tel",
        "tel mob",
        "telephone sav",
        "telephone1",
        "coordinates.phone",
        "telephone du lieu",
    ]
    return header_score(header, words_combinations_list)

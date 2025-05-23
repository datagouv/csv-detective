from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "datetime iso",
        "datetime",
        "timestamp",
        "osm_timestamp",
        "date",
        "created at",
        "last update",
        "date maj",
        "createdat",
        "date naissance",
        "date donnees",
    ]
    return header_score(header, words_combinations_list)

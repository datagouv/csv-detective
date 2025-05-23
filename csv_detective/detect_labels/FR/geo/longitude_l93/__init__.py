from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    # Does not detect CRS
    words_combinations_list = [
        "longitude",
        "lon",
        "long",
        "geocodage x gps",
        "location longitude",
        "xlongitude",
        "lng",
        "xlong",
        "x",
        "xf",
        "xd",
    ]
    return header_score(header, words_combinations_list)

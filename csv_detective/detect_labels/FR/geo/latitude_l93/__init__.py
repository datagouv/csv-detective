from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    # Does not always detect CRS
    words_combinations_list = [
        "latitude",
        "lat",
        "y",
        "yf",
        "yd",
        "y l93",
        "coordonnee y",
        "latitude lb93",
        "coord y",
        "ycoord",
        "geocodage y gps",
        "location latitude",
        "ylatitude",
        "ylat",
        "latitude (y)",
        "latitudeorg",
        "coordinates.latitude",
        "googlemap latitude",
        "latitudelieu",
        "latitude googlemap",
    ]
    return header_score(header, words_combinations_list)

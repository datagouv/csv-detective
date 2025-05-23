from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "latitude",
        "lat",
        "y",
        "yf",
        "yd",
        "coordonnee y",
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
        "latitude wgs84",
        "y wgs84",
        "latitude (wgs84)",
    ]
    return header_score(header, words_combinations_list)

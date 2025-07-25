from csv_detective.parsing.text import header_score

PROPORTION = 0.5

COMMON_COORDS_LABELS = [
    "c geo",
    "code geo",
    "coord gps",
    "coordonnees",
    "coordonnees ban",
    "coordonnees finales",
    "coordonnees geo",
    "coordonnees geographiques",
    "coordonnees geoloc",
    "coordonnees geoloc",
    "coordonnees gps",
    "coordonnees insee",
    "coordonnees xy",
    "geo",
    "geo coordinates",
    "geo cp",
    "geo localisation",
    "geo point",
    "geo point 2d",
    "geolocalisation",
    "geom x y",
    "geometry x y",
    "geopoint",
    "point geo",
    "point geo insee",
    "position",
    "position geographique",
    "wgs84",
    "x y",
    "xy",
]


def _is(header: str) -> float:
    words_combinations_list = [
        "latlon wgs",
        "latlon",
        "latlong",
        "lat lon",
    ] + COMMON_COORDS_LABELS
    return header_score(header, words_combinations_list)

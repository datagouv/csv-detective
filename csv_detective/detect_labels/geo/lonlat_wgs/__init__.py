from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "lonlat wgs",
        "lonlat",
        "geo point",
        "geo point 2d",
        "wgs84",
        "geolocalisation",
        "geo",
        "coordonnees finales",
        "coordonnees",
        "coordonnees ban",
        "xy",
        "geometry x y",
        "coordonnees insee",
        "coordonnees geographiques",
        "position",
        "coordonnes gps",
        "geopoint",
        "geom x y",
        "coord gps",
        "longlat",
        "position geographique",
        "c geo",
        "coordonnes geoloc",
        "lat lon",
        "code geo",
        "geo localisation",
        "coordonnes geo",
        "geo cp",
        "x y",
        "geo coordinates",
        "point geo",
        "point geo insee",
        "coordonnees geoloc",
        "coordonnees xy",
    ]
    return header_score(header, words_combinations_list)

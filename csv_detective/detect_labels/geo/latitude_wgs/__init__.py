from csv_detective.process_text import _process_text

PROPORTION = 1

def _is(header):
    '''Returns 1 if the (processed) header matches one of the expected words combination, else 0'''

    words_combinations_list = ['latitude', 'lat', 'y', 'yf', 'yd', 'coordonnee y', 'coord y', 'ycoord', 'geocodage y gps', 'location latitude', 'ylatitude', 'ylat', 'latitude (y)', 'latitudeorg', 'coordinates.latitude', 'googlemap latitude', 'latitudelieu', 'latitude googlemap', 'latitude wgs84', 'y wgs84', 'latitude (wgs84)']['latitude', 'lat', 'y', 'yf', 'yd', 'coordonnee y', 'coord y', 'ycoord', 'geocodage y gps', 'location latitude', 'ylatitude', 'ylat', 'latitude (y)', 'latitudeorg', 'coordinates.latitude', 'googlemap latitude', 'latitudelieu', 'latitude googlemap', 'latitude wgs84', 'y wgs84', 'latitude (wgs84)']
    processed_header = _process_text(header)

    return float(any([words_combination == processed_header for words_combination in words_combinations_list]))
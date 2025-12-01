from csv_detective.parsing.text import _process_text

proportion = 1
tags = ["fr"]
labels = ["sexe", "sex", "civilite", "genre", "id sexe"]


def _is(val):
    if not isinstance(val, str):
        return False
    return _process_text(val) in {"homme", "femme", "h", "f", "m", "masculin", "feminin"}


_test_values = {
    True: ["femme", "H"],
    False: ["adulte"],
}

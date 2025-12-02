from csv_detective.formats.float import _is as is_float

proportion = 0.8
labels = ["budget", "salaire", "euro", "euros", "prêt", "montant"]

currencies = {"€", "$", "£", "¥"}


def _is(val):
    if not isinstance(val, str) or val[-1] not in currencies:
        return False
    return is_float(val[:-1])


_test_values = {
    True: ["120€", "-20.2$"],
    False: ["200", "100 euros"],
}

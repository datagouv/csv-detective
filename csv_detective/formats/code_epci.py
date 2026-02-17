from csv_detective.formats.siren import _is as is_siren

proportion = 0.9
tags = ["fr", "geo"]
mandatory_label = True
labels = {
    "epci": 1,
}


def _is(val) -> bool:
    """Repere les codes EPCI (SIRENs spécifiques)"""
    if not isinstance(val, str):
        return False
    # this is the most specific test we can do without an external fetch
    # many false positive from the values, but we have a mandatory label
    return is_siren(val) and val.startswith("2")


_test_values = {
    True: ["200000172", "243 700 754"],
    False: ["130025265"],
}

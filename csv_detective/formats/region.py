from frformat import Millesime, Options, Region

proportion = 1
tags = ["fr", "geo"]
labels = {
    "region": 1,
    "libelle region": 1,
    "nom region": 1,
    "libelle reg": 1,
    "nom reg": 1,
    "reg libusage": 1,
    "nom de la region": 1,
    "regionorg": 1,
    "regionlieu": 1,
    "reg": 0.5,
    "nom officiel region": 1,
}

_extra_valid_values_set = frozenset(
    {
        "alsace",
        "aquitaine",
        "ara",
        "aura",
        "auvergne",
        "auvergne et rhone alpes",
        "basse normandie",
        "bfc",
        "bourgogne",
        "bourgogne et franche comte",
        "centre",
        "champagne ardenne",
        "franche comte",
        "ge",
        "haute normandie",
        "hdf",
        "languedoc roussillon",
        "limousin",
        "lorraine",
        "midi pyrenees",
        "nord pas de calais",
        "npdc",
        "paca",
        "picardie",
        "poitou charentes",
        "reunion",
        "rhone alpes",
    }
)


_options = Options(
    ignore_case=True,
    ignore_accents=True,
    replace_non_alphanumeric_with_space=True,
    ignore_extra_whitespace=True,
    extra_valid_values=_extra_valid_values_set,
)
_region = Region(Millesime.LATEST, _options)


def _is(val):
    """Match avec le nom des regions"""
    return isinstance(val, str) and _region.is_valid(val)


_test_values = {
    True: ["bretagne", "ile-de-france"],
    False: ["baviere", "overgne"],
}
